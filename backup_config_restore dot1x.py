from netmiko import ConnectHandler
from getpass import getpass
from ciscoconfparse import CiscoConfParse

import json
from napalm import get_network_driver

#this script has only been tested on one switch but it will take a backup of a switch then apply the 
#802.1x interface port settings and save the file as the switch hostname

IP = input('Enter IP address: ')

username = input('Enter your username: ')
password = getpass()


Switch = {
            'device_type': 'cisco_ios',
            'ip': IP,
            'username': username,
            'password': password
        }

net_connect = ConnectHandler(**Switch)

hostname = net_connect.send_command('show run | i hostname')
hostname.split(" ")
hostname,device = hostname.split(" ")
print ("Backing up " + device)

filename = 'H:/Scripts/Cisco_Python/' + device + '.txt'
        # to save backup to same folder as script use below line and comment out above line 
        # filename = device + '.txt' 

showrun = net_connect.send_command('show run | beg interface GigabitEthernet1/0/1')
log_file = open(filename, "a")   # in append mode
log_file.write(showrun)
log_file.write("\n")

# Finally close the connection
net_connect.disconnect()




#This portion of the script will parse the file with path listed below.


parse = CiscoConfParse(filename)
#This will parse the config for all interfaces and if there is an access vlan in it the vlan_id will be pulled for each interface.
for intf in parse.find_objects(r'^interface.+?thernet'):
    vlan_id = intf.re_match_iter_typed(r'switchport access vlan (\S+)',default='')
    
#If the interface is a switchport access without the dot1x it will be selected to have the below configuration added.
    is_switchport_access = intf.has_child_with(r'switchport access vlan')
    is_switchport_trunk = intf.has_child_with(r'switchport mode trunk')
#This is the config that will be applied to each of the selected interfaces with the variable vlan_id from the loop command from above.
    if is_switchport_access and (not is_switchport_trunk):
        intf.append_to_family(' device-tracking attach-policy ISE-DEVICE-TRACK-POL')
        intf.append_to_family(' authentication event server dead action authorize vlan ' + vlan_id)
        intf.append_to_family(' authentication event server dead action authorize voice')
        intf.append_to_family(' authentication host-mode multi-auth')
        intf.append_to_family(' switchport mode access')
        intf.append_to_family(' authentication open')
        intf.append_to_family(' authentication order dot1x mab')
        intf.append_to_family(' authentication priority mab dot1x')
        intf.append_to_family(' authentication port-control auto')
        intf.append_to_family(' authentication periodic')
        intf.append_to_family(' authentication timer reauthenticate server')
        intf.append_to_family(' mab')
        intf.append_to_family(' dot1x pae authenticator')
        intf.append_to_family(' dot1x timeout tx-period 3')

## Write the new configuration and save it as a file in a path of your choosing.
parse.save_as(filename)





driver = get_network_driver('ios')
iosvl2 = driver(IP, username, password, optional_args={'global_delay_factor': 2})
iosvl2.open()

print ("Accessing" + device)
iosvl2.load_merge_candidate(filename=filename)

#if the config in the txt document is not present in the switch the config file will be added to the switch and then saved.  
#ip scp server enable needs to be added to the switch for this to work

diffs = iosvl2.compare_config()
if len(diffs) > 0:
    iosvl2.commit_config()
else:
    print('No changes required.')
    iosvl2.discard_config()

iosvl2.close()