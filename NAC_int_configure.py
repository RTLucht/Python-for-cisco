from ciscoconfparse import CiscoConfParse
#This script will parse the file with path listed below.
parse = CiscoConfParse('h:/Scripts/Cisco_Python/switchconfig.txt')
#This will parse the config for all interfaces and if there is an access vlan in it the vlan_id will be pulled for each interface.
for intf in parse.find_objects(r'^interface.+?thernet'):
    vlan_id = intf.re_match_iter_typed(r'switchport access vlan (\S+)',default='')
    
#If the interface is a switchport access without the dot1x it will be selected to have the below configuration added.
    is_switchport_access = intf.has_child_with(r'switchport access vlan')
    is_switchport_mode_trunk = intf.has_child_with(r'switchport mode trunk')
#This is the config that will be applied to each of the selected interfaces with the variable vlan_id from the loop command from above.
    if is_switchport_access and (not is_switchport_mode_trunk):
        intf.append_to_family(' device-tracking attach-policy ISE-DEVICE-TRACK-POL')
        intf.append_to_family(' authentication event server dead action authorize vlan ' + vlan_id)
        intf.append_to_family(' authentication event server dead action authorize voice')
        intf.append_to_family(' authentication host-mode multi-auth')
        intf.append_to_family(' switchport mode access')
        intf.append_to_family(' authentication open')
        intf.append_to_family(' authentication order dot1x mab')
        intf.append_to_family(' authentication priority dot1x mab')
        intf.append_to_family(' authentication port-control auto')
        intf.append_to_family(' authentication periodic')
        intf.append_to_family(' authentication timer reauthenticate server')
        intf.append_to_family(' mab')
        intf.append_to_family(' dot1x pae authenticator')
        intf.append_to_family(' dot1x timeout tx-period 3')

## Write the new configuration and save it as a file in a path of your choosing.
parse.save_as('h:/Scripts/Cisco_Python/newswitchconfig.txt')