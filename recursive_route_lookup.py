class recursive_route_lookup(Connection):
    def __init__(self):
        super().__init__()
        self.switch_name = ""
        self.ip_address = ""
        self.ip_address_to_be_looked_up = ""
        self.show_ip_route = "show ip route "
        self.next_hop_interface_pattern = re.compile("^\s+|\s* \s*|\s+$")
        self.next_hop_ip_cisco_ios = ""
        self.command_outputs = {}       #use switchname+command as key

    def get_Task_details(self):
        print("\nEnter the Switchname where you want to start:")
        self.switch_name = input("Please enter switchname: ")
        self.ip_address = input("Please enter IP address to lookup: ")
        self.ip_address_to_be_looked_up = self.ip_address

    def open_connection_to_switch(self):
        logging.info(str(self.expect_command("ssh "+self.switch_name + "\n", ":")))
        logging.info("Logging into switch "+self.switch_name)
        print("Logging into " + self.switch_name)
        logging.info(str(self.expect_command(self.password + "\n")))
        self.remove_paging()

    def end_connection_to_switch(self):
        print("Logging out of "+self.switch_name)
        logging.info("Closing connection to "+self.switch_name)
        logging.info(str(self.expect_command("exit\n")))

    def get_command_output(self, command):
        logging.info("Running command '"+command+"'")
        print("Running command on switch : "+self.switch_name+" : "+command)
        self.command_outputs[self.switch_name+command] = self.expect_command(command + "\n")

    def get_route_cisco_nexus(self):
        next_hop_ip = ""
        command = self.show_ip_route+self.ip_address
        self.get_command_output(command)
        attached_route = False
        show_ip_route_output = self.command_outputs[self.switch_name+command]
        logging.info(show_ip_route_output)
        for line in show_ip_route_output.split("\r"):
            if "route not found" in line.strip().lower():
                print("===========Route not found================")
                return
            if "ubest/mbest:" in line.strip():
                ip_network = (re.findall( r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', line))[0]
                #ip_network = line.strip().split(",")[0]
            if "*via" in line.strip():
                next_hop_ip = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))[0]
                #next_hop_ip = line.strip().split(" ")[1].split(",")[0]
                next_hop_interface = line.strip().split(" ")[2].split(",")[0]
                break
        #check if the route is attached
        if "attached" in show_ip_route_output:
            attached_route = True
        #check if the route is a default route
        if IPNetwork(ip_network) == IPNetwork("0.0.0.0/0"):
            print("There is a default route on "+self.switch_name+" for IP "+self.ip_address)
            return
        #check if the route is found, return
        if IPAddress(self.ip_address_to_be_looked_up) in IPNetwork(ip_network) and IPAddress(next_hop_ip) in IPNetwork(ip_network):
            print("Route found on switch "+self.switch_name+" : Interface : "+next_hop_interface)
            return
        #check if the IP to be searched and the next hop IP are the same
        #if not, do a recursive lookup
        if IPAddress(self.ip_address) == IPAddress(next_hop_ip):
            #program should jump to the next switch in question
            next_hop_switch_name = self.get_next_hop_switch_name_cisco_nexus(next_hop_interface)
            self.end_connection_to_switch()
            self.switch_name = next_hop_switch_name
            self.open_connection_to_switch()
            self.ip_address = self.ip_address_to_be_looked_up
            return self.get_switch_type()
        else:
            self.ip_address = next_hop_ip
            return self.get_switch_type()

    def get_next_hop_switch_name_cisco_nexus(self,next_hop_interface):
        command = "show runn interface "+next_hop_interface
        self.get_command_output(command)
        description = ""
        show_run_interface_output = self.command_outputs[self.switch_name+command]
        for line in show_run_interface_output.split("\r"):
            if "description" in line.strip():
                description = line.strip().split(" ")[1]
        print("Next Hop interface = "+description)
        return description

    def get_route_arista(self):
        next_hop_ip = ""
        command = self.show_ip_route+self.ip_address
        self.get_command_output(command)
        attached_route = False
        show_ip_route_output = self.command_outputs[self.switch_name+command]
        logging.info(show_ip_route_output)
        for line in show_ip_route_output.split("\r"):
            line = re.sub('\s+',' ',line).strip()
            if "via" in line.strip():
                ip_network = (re.findall( r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', line))[0]
                #ip_network = line.strip().split(" ")[2]
                next_hop_ip = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))[1]
                #next_hop_ip = line.strip().split(" ")[5].split(",")[0]
                next_hop_interface = ([x for x in self.next_hop_interface_pattern.split(line[8:]) if x])[4]
                #next_hop_interface = line.strip().split(" ")[6]
                break
            if "directly connected" in line.strip():
                ip_network = (re.findall( r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', line))[0]
                next_hop_ip = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))[0]
                #next_hop_interface = line.strip().split(" ")[6]
                next_hop_interface = ([x for x in self.next_hop_interface_pattern.split(line[8:]) if x])[4]
                break
        #check if the route is attached
        if "attached" in show_ip_route_output:
            attached_route = True
        #check if the route is a default route
        if IPNetwork(ip_network) == IPNetwork("0.0.0.0/0"):
            print("There is a default route on "+self.switch_name+" for IP "+self.ip_address)
            return
        #check if the route is found, return
        if IPAddress(self.ip_address_to_be_looked_up) in IPNetwork(ip_network) and IPAddress(next_hop_ip) in IPNetwork(ip_network):
            print("Route found on switch "+self.switch_name+" : Interface : "+next_hop_interface)
            return
        #check if the IP to be searched and the next hop IP are the same
        #if not, do a recursive lookup
        if IPAddress(self.ip_address) == IPAddress(next_hop_ip):
            #program should jump to the next switch in question
            next_hop_switch_name = self.get_next_hop_switch_name_Arista(next_hop_interface)
            self.end_connection_to_switch()
            self.switch_name = next_hop_switch_name
            self.open_connection_to_switch()
            self.ip_address = self.ip_address_to_be_looked_up
            return self.get_switch_type()
        else:
            self.ip_address = next_hop_ip
            return self.get_switch_type()

    def get_next_hop_switch_name_Arista(self,next_hop_interface):
        if next_hop_interface.lower().startswith("vlan"):
            next_hop_vlan = next_hop_interface[4:]
            command = "show vlan id "+next_hop_vlan
        elif next_hop_interface.lower().startswith("eth") or next_hop_interface.lower().startswith("g") or next_hop_interface.lower().startswith("t"):
            return self.get_next_hop_switch_name_cisco_nexus(next_hop_interface)
        self.get_command_output(command)
        description = ""
        show_vlan_id_output = self.command_outputs[self.switch_name+command]
        for line in show_vlan_id_output.split("\r"):
            if self.switch_name in line.strip():
                description = ([x for x in self.next_hop_interface_pattern.split(line) if x])[1]
                break
        print("Next Hop interface = "+description.split("-")[1])
        return description.split("-")[1]

    def get_route_cisco_ios(self):
        next_hop_ip = ""
        command = self.show_ip_route+self.ip_address
        self.get_command_output(command)
        attached_route = False
        show_ip_route_output = self.command_outputs[self.switch_name+command]
        logging.info(show_ip_route_output)
        for line in show_ip_route_output.split("\r"):
            line = re.sub('\s+',' ',line).strip()
            if "Network not in table" in line.strip().lower():
                print("===========Route not found================")
                return
            if line.strip().lower().startswith("routing entry"):
                ip_network = (re.findall( r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', line))[0]
            if line.strip().startswith("*"):
                if re.findall( r'[0-9]+(?:\.[0-9]+){3}',line):
                    next_hop_ip = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))[0]
            if "directly connected" in line.strip():
                next_hop_interface = line.strip().split(" ")[4]
                break
        if next_hop_ip:
            self.next_hop_ip_cisco_ios = next_hop_ip
        else:
            next_hop_ip = self.next_hop_ip_cisco_ios
        #check if the route is a default route
        if IPNetwork(ip_network) == IPNetwork("0.0.0.0/0"):
            print("There is a default route on "+self.switch_name+" for IP "+self.ip_address)
            return
        #check if the route is found, return
        if IPAddress(self.ip_address_to_be_looked_up) in IPNetwork(ip_network) and IPAddress(next_hop_ip) in IPNetwork(ip_network):
            print("Route found on switch "+self.switch_name+" : Interface : "+next_hop_interface)
            return
        #check if the IP to be searched and the next hop IP are the same
        #if not, do a recursive lookup
        if IPAddress(self.ip_address) == IPAddress(next_hop_ip):
            #program should jump to the next switch in question
            next_hop_switch_name = self.get_next_hop_switch_name_Arista(next_hop_interface)
            self.end_connection_to_switch()
            self.switch_name = next_hop_switch_name
            self.open_connection_to_switch()
            self.ip_address = self.ip_address_to_be_looked_up
            return self.get_switch_type()
        else:
            self.ip_address = next_hop_ip
            return self.get_switch_type()

    def get_switch_type(self):
        if self.switch_name.lower().startswith("us02rtt"):
            self.get_route_arista()
        elif self.switch_name.lower().startswith("us02"):
            self.get_route_cisco_nexus()
        elif self.switch_name.lower().startswith("car") or self.switch_name.lower().startswith("ash") or self.switch_name.lower().startswith("sec"):
            self.get_route_cisco_ios()
        else:
            print("Not a valid switch")
