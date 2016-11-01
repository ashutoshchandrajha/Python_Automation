"""
this script logs into network devices from a jumphost,
it takes the ARP output and resolves the manufacturing
vendor. it then writes the output in an excel sheet

This script works separately from two different jumphosts
because of SSH issues from Cisco terminal servers to 
Nexus devices
"""

class mac_vendor_lookup(Connection):
    def __init__(self):
        super().__init__()
        self.remove_extra_spaces_pattern = re.compile("^\s+|\s* \s*|\s+$")
        self.command_outputs = {}          #use switch name + command as key
        self.switch_list_IOS = [
            "IOS LIST"
        ]
        self.switch_list_NEXUS = [
            "NEXUS LIST"
        ]
        self.ip_mac_mapping={}

    def open_connection_to_switch(self,switch_name):
        logging.info(str(self.expect_command("ssh "+switch_name + "\n", ":")))
        logging.info("Logging into switch "+switch_name)
        print("Logging into " + switch_name)
        logging.info(str(self.expect_command(self.password + "\n")))
        self.remove_paging()

    def end_connection_to_switch(self,switch_name):
        print("Logging out of "+switch_name)
        logging.info("Closing connection to "+switch_name)
        logging.info(str(self.expect_command("exit\n")))

    #this is for commands which do not have any outputs like ACL updates
    def get_command_output(self, command):
        logging.info("Running command '"+command+"'")
        print("Running command : "+command)
        self.expect_command(command + "\n")

    #this is for commands with outputs like show commands
    def get_show_command_output(self, switch, command):
        logging.info("Running command '"+command+"'")
        print("Running command : "+command)
        self.command_outputs[switch+command] = self.expect_command(command + "\n")

    def get_oui(self, mac):
        maco = EUI(mac)
        try:
            macf = maco.oui.registration().org
        except NotRegisteredError:
            macf = "Not available"
        return macf

    def resolve_interface_description(self,switch,interface):
        command = "show runn interface "+interface
        self.get_show_command_output(switch,command)
        output = self.command_outputs[switch+command]
        for line in output.split("\r"):
            if "description" in line.lower():
                description = line.split("description")[1]
                return description

    def show_config(self):

        #create a workbook and worksheet
        workbook = xlsxwriter.Workbook('devices.xlsx')
        worksheet1 = workbook.add_worksheet('Devices')

        #add a bold format
        bold = workbook.add_format({'bold':True})

        #write the header
        worksheet1.write('A1','MAC ADDRESS', bold)
        worksheet1.write('B1','Interface',bold)
        worksheet1.write('C1','Vendor',bold)
        worksheet1.write('D1','Description',bold)

        row = 2
        col = 0

        #setup conditional formatting
        #worksheet1.conditional_format()
        # Green fill with dark green text.
        switch_name_color_fill = workbook.add_format({'bg_color':   '#C6EFCE',
                               'font_color': '#006100'})

        not_cisco_juniper_arista = workbook.add_format({'bg_color':   '#FFC7CE',
                               'font_color': '#9C0006'})

        for switch in self.switch_list_NEXUS:

            #write the switch name
            worksheet1.write(row,col,switch,switch_name_color_fill)
            row+=1

            self.open_connection_to_switch(switch)
            command = "sh ip arp"
            self.get_show_command_output(switch,command)
            peer_IP=[]
            output = self.command_outputs[switch+command]
            for line in output.split("\r"):
                line = re.sub('\s+',' ',line).strip()
                peer_IP = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))
                if peer_IP!=[] and "incomplete" not in line.lower():
                    mac_line = ([x for x in self.remove_extra_spaces_pattern.split(line) if x])
                    mac_address = mac_line[2]
                    interface = mac_line[3]
                    mac_org = self.get_oui(mac_address)
                    description = self.resolve_interface_description(switch,interface)

                    #write to worksheet
                    worksheet1.write(row,col,mac_address)
                    worksheet1.write(row,col+1,interface)
                    mac_org_lower=mac_org.lower()

                    if "cisco" not in mac_org_lower and "juniper" not in mac_org_lower and "arista" not in mac_org_lower and "fortinet" not in mac_org_lower:
                        worksheet1.write(row,col+2,mac_org,not_cisco_juniper_arista)
                    else:
                        worksheet1.write(row,col+2,mac_org)
                    worksheet1.write(row,col+3,description)
                    #increase row and reset col to 0
                    row+=1
                    col=0

                    print(mac_address+" - "+interface+" - "+mac_org)

            self.end_connection_to_switch(switch)

        #open connection to CARMGTS1A for logging into
        self.open_connection_to_switch("CARMGTS1A")

        for switch in self.switch_list_IOS:

            #write the switch name
            worksheet1.write(row,col,switch,switch_name_color_fill)
            row+=1

            self.open_connection_to_switch(switch)
            command = "sh ip arp"
            self.get_show_command_output(switch,command)
            peer_IP =[]
            output = self.command_outputs[switch+command]
            for line in output.split("\r"):
                line = re.sub('\s+',' ',line).strip()
                peer_IP = (re.findall( r'[0-9]+(?:\.[0-9]+){3}',line))
                if peer_IP!=[] and "incomplete" not in line.lower():
                    mac_line = ([x for x in self.remove_extra_spaces_pattern.split(line) if x])
                    mac_address = mac_line[3]
                    interface = mac_line[5]
                    mac_org = self.get_oui(mac_address)
                    description = self.resolve_interface_description(switch,interface)

                    #write to worksheet
                    worksheet1.write(row,col,mac_address)
                    worksheet1.write(row,col+1,interface)
                    mac_org_lower=mac_org.lower()

                    if "cisco" not in mac_org_lower and "juniper" not in mac_org_lower and "arista" not in mac_org_lower and "fortinet" not in mac_org_lower:
                        worksheet1.write(row,col+2,mac_org,not_cisco_juniper_arista)
                    else:
                        worksheet1.write(row,col+2,mac_org)
                    worksheet1.write(row,col+3,description)
                    """
                    worksheet1.conditional_format(row,col+2,row,col+2,{'type':'text',
                                                                        'criteria':'not containing',
                                                                        'value':'jdsalsniads',
                                                                        'format':not_cisco_juniper_arista})
                    """
                    #increase row and reset col to 0
                    row+=1
                    col=0

                    print(mac_address+" - "+interface+" - "+mac_org)

            self.end_connection_to_switch(switch)

        #end connection to CARMGTS1A after doing work on IOS devices
        self.end_connection_to_switch("CARMGTS1A")
        #workbook.close()


def main():
    mac = mac_vendor_lookup()
    #push_acl.get_credentials()
    mac.form_conn()
    mac.show_config()
    mac.close_conn()

if __name__ == '__main__':
    main()
