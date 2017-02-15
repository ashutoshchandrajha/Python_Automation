
class find_multicast_publisher(Connection):
    def __init__(self):
        super().__init__()
        self.multicast_ip_to_lookup = "Multicast IP to be looked UP"
        self.source_ip_for_multicast = ""
        self.next_hop_source_route = ""
        self.next_hop_interface_source_route = ""
        self.next_hop_switch = ""
        self.is_publisher = False
        self.mroute_source_command_available = True
        self.running_config_file = "multicast_running_config.log"
        self.line_without_extra_spaces = re.compile("^\s+|\s* \s*|\s+$")
        self.command_outputs = {}          #use command + switchname as key
        self.switch_type = {}              #use switch name as key to find the type i.e. Nexus or IOS or Arista
        self.switches_Traversed = []
        self.switch_name = "US02EXTCASRP001"

    def get_Task_details(self):
        print("\nEnter the Switchname where you want to start:")
        self.switch_name = input("Please enter switchname: ")
        self.multicast_ip_to_lookup = input("Please enter multicast IP address to lookup: ")

    def open_connection_to_switch(self, switch_name):
        logging.info(str(self.expect_command("ssh "+switch_name + "\n", ":")))
        logging.info("Logging into switch "+switch_name)
        print("Logging into " + switch_name)
        logging.info(str(self.expect_command(self.password + "\n")))
        self.remove_paging()

    def end_connection_to_switch(self, switch_name):
        print("Logging out of "+switch_name)
        logging.info("Closing connection to "+switch_name)
        logging.info(str(self.expect_command("exit\n")))

    def get_command_output(self, command):
        logging.info("Running command '"+command+"'")
        print("Running command on switch : "+self.switch_name+" : "+command)
        self.command_outputs[self.switch_name+command] = self.expect_command(command + "\n")

    def get_running_config_in_file(self, switch_name):
        self.running_config = open(self.running_config_file, "w")
        command = "show running"
        self.running_config.write(str(self.expect_command(command + "\n")))
        self.running_config.close()

    def get_show_version(self):
        command = "show version"
        self.get_command_output(command)
        self.set_Switch_type()

    def set_Switch_type(self):
        command = "show version"
        show_version = self.command_outputs[self.switch_name+command]
        for line in show_version.split("\r"):
            if "ios software" in line.lower():
                self.switch_type[self.switch_name] = "IOS"
                return
            elif "cisco nexus" in line.lower():
                self.switch_type[self.switch_name] = "NEXUS"
                return
            elif "arista" in line.lower():
                self.switch_type[self.switch_name] = "ARISTA"
                return

    def get_show_lldp_neighbor_output(self):
        command = "show lldp neighbor"
        self.get_command_output(command)

    def get_show_cdp_neighbor_output(self):
        command = "show cdp neighbor"
        self.get_command_output(command)

    def get_rp_addresses(self):
        command = "show startup-config | i rp-address"
        self.get_command_output(command)

    def get_show_ip_igmp_snooping_output(self):
        command = "show ip igmp snooping group "+self.multicast_ip_to_lookup +" detail"
        self.get_command_output(command)

    def get_show_ip_pim_rp_output(self):
        command = "show ip pim rp "+ self.multicast_ip_to_lookup
        self.get_command_output(command)

    def get_show_ip_pim_neighbor_output(self):
        command = "show ip pim neighbor "+self.next_hop_source_route
        self.get_command_output(command)

    def get_show_mroute_output(self):
        command = "show ip mroute "+self.multicast_ip_to_lookup
        self.get_command_output(command)

    def get_show_ip_route_output(self, ip_address):
        command = "show ip route "+ip_address
        self.get_command_output(command)

    def get_show_mroute_Shared_Tree_output(self):
        command = "show ip mroute "+self.multicast_ip_to_lookup+" shared-tree"
        self.get_command_output(command)

    def get_show_mroute_Source_Tree_output(self):
        command = "show ip mroute "+self.multicast_ip_to_lookup+" source-tree"
        self.get_command_output(command)

    def get_next_hop_source_route_NEXUS(self):
        #returns next hop for multicast source
        #In case of multiple paths, returns highest IP
        self.get_show_ip_route_output(self.source_ip_for_multicast)
        next_hop_list = []
        command = "show ip route "+self.source_ip_for_multicast
        show_ip_route = self.command_outputs[self.switch_name+command]
        for line in show_ip_route.strip().split("\r"):
            if "route not found" in line.lower():
                print("Route not found on "+self.switch_name)
                return
            if "*via" in line:
                #next_hop = (re.findall(r'[0-9]+(?:\.[0-9]+){3}',line))[0]
                next_hop_list.append(IPAddress((re.findall(r'[0-9]+(?:\.[0-9]+){3}',line))[0]))
            if "0.0.0.0" in line:
                return IPAddress("0.0.0.0")
        if len(next_hop_list) == 1:
            return IPAddress(next_hop_list[0])
        else:
            return max(next_hop_list)

    def get_source_address_for_RPF_NEXUS(self):
        self.get_show_mroute_Source_Tree_output()
        command = "show ip mroute "+self.multicast_ip_to_lookup+" source-tree"
        show_mroute = self.command_outputs[self.switch_name+command]
        if "invalid ip" in show_mroute.lower():
            self.mroute_source_command_available = False
            print("show ip mroute "+self.multicast_ip_to_lookup+" source-tree : command not available on this switch")
            self.get_show_mroute_output()
            command = "show ip mroute "+self.multicast_ip_to_lookup
            show_mroute = self.command_outputs[self.switch_name+command]
        source_ip = ""
        if "group not found" in show_mroute.lower():
            #self.get_show_ip_igmp_snooping_output()
            return
        for line in show_mroute.split("\r"):
            if line.strip().startswith("(") and "(*" not in line:
                source_ip_list = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))
                if source_ip_list:
                    source_ip = source_ip_list[0]
                    self.source_ip_for_multicast = source_ip
                    break

    def get_source_address_for_ARISTA(self):
        self.get_show_mroute_output()
        command = "show ip mroute "+self.multicast_ip_to_lookup
        show_mroute = self.command_outputs[self.switch_name+command]

        #will write

    def resolve_next_hop_show_cdp(self):
        next_hop_resolved = False
        self.get_show_cdp_neighbor_output()
        command = "show cdp neighbor"
        show_cdp_neighbor = self.command_outputs[self.switch_name+command]
        if "cdp not enabled" in show_cdp_neighbor.lower():
            return next_hop_resolved
        if self.next_hop_interface_source_route.lower().startswith("eth"):
            interface = self.next_hop_interface_source_route[:3]+self.next_hop_interface_source_route[8:]
        previous_line = ""
        #previous line variable will take care of cases when CDP neighbor output is not in one line
        for line in show_cdp_neighbor.strip().split("\r"):
            if interface.lower() in line.lower() and line.startswith(" "):
                self.next_hop_switch = ([x for x in self.line_without_extra_spaces.split(previous_line) if x])[0]
                next_hop_resolved = True
                break
            elif interface.lower() in line.lower():
                self.next_hop_switch = ([x for x in self.line_without_extra_spaces.split(line) if x])[0]
                next_hop_resolved = True
                break
            previous_line = line
        return next_hop_resolved

    def resolve_next_hop_show_lldp(self):
        next_hop_resolved = False
        self.get_show_lldp_neighbor_output()
        command = "show lldp neighbor"
        show_lldp_neighbor = self.command_outputs[self.switch_name+command]
        if "lldp is not enabled" in show_lldp_neighbor.lower():
            return next_hop_resolved
        #set the interface variable
        if self.next_hop_interface_source_route.lower().startswith("po"):
            command = "show runn interface "+self.next_hop_interface_source_route+" membership"
            self.get_command_output(command)
            #get first member of port channel. assuming that this port-channel is not a VPC
            port_channel_membership = self.command_outputs[self.switch_name+command]
            for line in port_channel_membership.strip().split("\r"):
                if "interface ethernet" in line.lower():
                    interface = line.split()[1]
                    if interface.startswith("eth"):
                        interface = interface[:3]+interface[8:]
                        break
        if self.next_hop_interface_source_route.lower().startswith("eth"):
            interface = self.next_hop_interface_source_route[:3]+self.next_hop_interface_source_route[8:]
        for line in show_lldp_neighbor.strip().split("\r"):
            if interface.lower() in line.lower():
                self.next_hop_switch = ([x for x in self.line_without_extra_spaces.split(line) if x])[0]
                next_hop_resolved = True
                break
        return next_hop_resolved

    def check_source_address_for_RPF_NEXUS(self):
        #gets the source route for multicast
        #if the source route exists, gets the next hop for source route
        #if next hop for source is valid, gets pim neighbor
        #gets next hop interface from show ip pim neighbor output
        #checks if this interface is in show ip mroute output as incoming interface
        #if RPF check passes, takes show lldp output and resolves next hop
        self.get_source_address_for_RPF_NEXUS()
        if self.source_ip_for_multicast:
            print("Source IP = "+self.source_ip_for_multicast)
            self.next_hop_source_route = str(self.get_next_hop_source_route_NEXUS())
            if self.next_hop_source_route == IPAddress("0.0.0.0"):
                print("Next hop for "+self.next_hop_source_route+" reachable via Default route")
                return
            elif self.next_hop_source_route:
                self.get_show_ip_pim_neighbor_output()
                command = "show ip pim neighbor "+self.next_hop_source_route
                show_ip_pim_neighbor = self.command_outputs[self.switch_name+command]
                if "neighbor not found" in show_ip_pim_neighbor:
                    print("No pim neighbor exists for "+self.next_hop_source_route+" on switch "+self.switch_name)
                    return
                for line in show_ip_pim_neighbor.strip().split("\r"):
                    if self.next_hop_source_route in line and "show ip pim" not in line.lower():
                        self.next_hop_interface_source_route = ([x for x in self.line_without_extra_spaces.split(line) if x])[1]
                        print("Next hop interface for source route = "+self.next_hop_interface_source_route)
                        break
                if self.mroute_source_command_available:
                    command = "show ip mroute "+self.multicast_ip_to_lookup+" source-tree"
                else:
                    command = "show ip mroute "+self.multicast_ip_to_lookup
                show_ip_mroute = self.command_outputs[self.switch_name+command]
                if self.next_hop_interface_source_route not in show_ip_mroute:
                    print("RPF CHECK FAILED. EXITING!")
                    return
                s_comma_g = False
                for line in show_ip_mroute.strip().split("\r"):
                    if line.startswith("(") and not line.startswith("(*"):
                        s_comma_g = True
                        break
                if not s_comma_g:
                    print("No (S,G) found on this switch. Group is not publishing")
                    return
                for line in show_ip_mroute.strip().split("\r"):
                    if "incoming interface" in line.lower() and self.next_hop_interface_source_route in line.lower():
                        print("RPF CHECK PASSED. MOVING FORWARD")
                        break
                #should go in lldp function
                next_hop_resolved = self.resolve_next_hop_show_lldp()
                if not next_hop_resolved:
                    print("Could not resolve LLDP. Trying to resolve next hop with CDP")
                    next_hop_resolved = self.resolve_next_hop_show_cdp()
                if not next_hop_resolved:
                    print("Could not resolve next hop with CDP. EXITING!")
                    return
                if self.next_hop_switch:
                    print("Next hop switch : "+ self.next_hop_switch)
                return
            else:
                print("Next hop route not found for "+self.next_hop_source_route+" on switch "+self.switch_name)
        else:
            print("Group not found on "+self.switch_name)

    def check_source_address_for_RPF_ARISTA(self):
        print("ARISTA SWITCH")

    def check_source_address_for_RPF_IOS(self):
        pass

    def check_source_address_for_RPF(self):
        if self.switch_type[self.switch_name] == "NEXUS":
            self.check_source_address_for_RPF_NEXUS()
            return
        if self.switch_type[self.switch_name] == "ARISTA":
            #self.check_source_address_for_RPF_ARISTA()
            print("ARISTA MODULE IS CURRENTLY UNDER DEVELOPMENT")
            return
        if self.switch_type[self.switch_name] == "IOS":
            #self.check_source_address_for_RPF_IOS()
            print("IOS MODULE IS CURRENTLY UNDER DEVELOPMENT")
            return

    def get_show_mroute_summary_output(self):
        self.get_command_output("show ip mro "+ self.multicast_ip_to_lookup+" summary")

    def get_show_igmp_output(self):
        self.get_command_output("show ip igmp groups "+ self.multicast_ip_to_lookup)

    def get_ip_arp_output(self,ip_address):
        self.get_command_output("show ip arp | i "+ip_address)

    def check_config_for_igmp_join_group(self):
        #self.get_running_config_in_file(self.switch_name)
        parse = CiscoConfParse(self.running_config_file)
        all_interface = parse.find_objects(r"^interf")
        igmp_join_group = [obj for obj in parse.find_objects(r"^interf") \
                   if obj.re_search_children(r"ip igmp join-group")]
        for interface in igmp_join_group:
            logging.info("Please check the IGMP JOIN GROUP commands which may result in data not being forwarded : "+str(interface))
            print("Please check the IGMP JOIN GROUP commands which may result in data not being forwarded : "+str(interface))

    def start_troubleshooting(self):
        self.switches_Traversed.append(self.switch_name)
        self.source_ip_for_multicast = ""
        self.next_hop_source_route = ""
        self.next_hop_interface_source_route = ""
        self.next_hop_switch = ""
        self.mroute_source_command_available = True
        #open connection to switch from jumphost
        self.open_connection_to_switch(self.switch_name)
        self.get_show_version()
        self.check_config_for_igmp_join_group()
        self.check_source_address_for_RPF()
        #self.check_source_address_for_RPF_NEXUS()
        #close connection to switch
        self.end_connection_to_switch(self.switch_name)
        if self.next_hop_switch:
            self.switch_name = self.next_hop_switch.split(".")[0]
            self.start_troubleshooting()

def main():
    tshoot = find_multicast_publisher()
    #tshoot.get_credentials()
    tshoot.form_conn()
    tshoot.start_troubleshooting()
    print ("List of switches traversed : ")
    print(tshoot.switches_Traversed)
    tshoot.close_conn()

if __name__ == '__main__':
    main()
