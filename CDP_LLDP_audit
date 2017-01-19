"""
This script takes a list of IOS and Nexus devices as input and 
checks whether LLDP or CDP is explicitly enabled on any interface.
This can used to audit a list of switches and create excel reports.
"""

class cdp_lldp_extranet_audit(Connection):
    def __init__(self):
        super().__init__()
        self.remove_extra_spaces_pattern = re.compile("^\s+|\s* \s*|\s+$")
        self.command_outputs = {}          #use switch name + command as key
        self.switch_list_IOS = [
            "switch1",
            "switch1"
        ]
        self.switch_list_NEXUS = [
            "switch1",
            "switch1"
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
        return self.expect_command(command + "\n")

    def resolve_interface_description(self,switch,interface):
        command = "show runn interface "+interface
        output = self.get_show_command_output(switch,command)
        for line in output.split("\r"):
            if "description" in line.lower():
                description = line.split("description")[1]
                return description
        return "no description"

    def show_config(self):

        #create a workbook and worksheet
        workbook = xlsxwriter.Workbook('cdp_lldp.xlsx')
        worksheet1 = workbook.add_worksheet('CDP LLDP STATUS')

        #add a bold format
        bold = workbook.add_format({'bold':True})

        #write the header
        worksheet1.write('A1','Interface', bold)
        worksheet1.write('B1','Description',bold)
        worksheet1.write('C1','Status',bold)
        worksheet1.write('D1','LLDP Transmit',bold)
        worksheet1.write('E1','LLDP Receive', bold)
        worksheet1.write('F1','CDP Status', bold)

        row = 2
        col = 0

        #setup conditional formatting
        #worksheet1.conditional_format()
        # Green fill with dark green text.
        switch_name_color_fill = workbook.add_format({'bg_color':   '#C6EFCE',
                               'font_color': '#006100'})

        cdp_lldp_enabled = workbook.add_format({'bg_color':   '#FFC7CE',
                               'font_color': '#9C0006'})

        for switch in self.switch_list_NEXUS:

            #write the switch name
            worksheet1.write(row,col,switch,switch_name_color_fill)
            row+=1

            self.open_connection_to_switch(switch)
            command = "sh int status"
            output = self.get_show_command_output(switch,command)
            customer_interface_parameter_list = []

            """
            check if the interface in the output is a customer interface.
            If it is, put it in the customer_interface_list
            """
            for line in output.split("\r"):
                if line.lower().startswith("eth") or line.lower().startswith("gi") or line.lower().startswith("te"):
                    line = re.sub('\s+', ' ', line).strip()
                    interface_name = line.split(" ")[0]
                    interface_description = self.resolve_interface_description(switch, interface_name)
                    interface_status = ""
                    if "connected" in line.lower():
                        interface_status = "connected"
                    elif "disabl" in line.lower():
                        interface_status = "disabled"
                    elif "notconne" in line.lower():
                        interface_status = "notconnect"
                    elif "sfpabs" in line.lower():
                        interface_status = "sfpAbsent"
                    else:
                        interface_status = "not resolved"
                    interface_parameter_list = [interface_name,interface_description,interface_status]
                    if "mpid" in interface_description.lower():
                        customer_interface_parameter_list.append(interface_parameter_list)

            #print(customer_interface_parameter_list)
            """
            Now check if lldp is disabled on every interface in customer_interface_list
            """
            for customer_interface_parameters in customer_interface_parameter_list:

                #write the interface parameters to worksheet
                worksheet1.write(row,col,customer_interface_parameters[0])
                worksheet1.write(row,col+1,customer_interface_parameters[1])
                worksheet1.write(row,col+2,customer_interface_parameters[2])

                lldp_output = self.get_show_command_output(switch, "show running-config interface "+customer_interface_parameters[0])
                lldp_transmit = False
                lldp_receive = False
                cdp_disable = False
                for line in lldp_output.split("\r"):
                    if "no lldp transmit" in line.lower():
                        lldp_transmit = True
                    if "no lldp receive" in line.lower():
                        lldp_receive = True
                    if "no cdp enable" in line.lower():
                        cdp_disable = True

                if lldp_transmit:
                    worksheet1.write(row,col+3,"Disabled")
                else:
                    worksheet1.write(row,col+3,"Enabled",cdp_lldp_enabled)

                if lldp_receive:
                    worksheet1.write(row,col+4,"Disabled")
                else:
                    worksheet1.write(row, col+4, "Enabled", cdp_lldp_enabled)

                if cdp_disable:
                    worksheet1.write(row, col+5, "Disabled")
                else:
                    worksheet1.write(row, col + 5, "Enabled", cdp_lldp_enabled)

                # increase row and reset col to 0
                row += 1
                col = 0

            self.end_connection_to_switch(switch)


        #open connection to CARMGTS1A for logging into
        self.open_connection_to_switch("CARMGTS1A")


        for switch in self.switch_list_IOS:

            # write the switch name
            worksheet1.write(row, col, switch, switch_name_color_fill)
            row += 1

            self.open_connection_to_switch(switch)
            command = "sh int status"
            output = self.get_show_command_output(switch, command)
            customer_interface_parameter_list = []

            """
            check if the interface in the output is a customer interface.
            If it is, put it in the customer_interface_list
            """
            for line in output.split("\r"):
                if line.lower().startswith("eth") or line.lower().startswith("gi") or line.lower().startswith("te"):
                    line = re.sub('\s+', ' ', line).strip()
                    interface_name = line.split(" ")[0]
                    interface_description = self.resolve_interface_description(switch, interface_name)
                    interface_status = ""
                    if "connected" in line.lower():
                        interface_status = "connected"
                    elif "disabl" in line.lower():
                        interface_status = "disabled"
                    elif "notconne" in line.lower():
                        interface_status = "notconne"
                    elif "sfpabs" in line.lower():
                        interface_status = "sfpAbsent"
                    else:
                        interface_status = "not resolved"
                    interface_parameter_list = [interface_name, interface_description, interface_status]
                    if "mpid" in interface_description.lower():
                        customer_interface_parameter_list.append(interface_parameter_list)

            # print(customer_interface_parameter_list)
            """
            Now check if lldp is disabled on every interface in customer_interface_list
            """
            for customer_interface_parameters in customer_interface_parameter_list:

                # write the interface parameters to worksheet
                worksheet1.write(row, col, customer_interface_parameters[0])
                worksheet1.write(row, col + 1, customer_interface_parameters[1])
                worksheet1.write(row, col + 2, customer_interface_parameters[2])

                cdp_output = self.get_show_command_output(switch, "show running-config interface " +
                                                           customer_interface_parameters[0])

                cdp_disable = False
                for line in cdp_output.split("\r"):
                    if "no cdp enable" in line.lower():
                        cdp_disable = True


                worksheet1.write(row, col + 3, "LLDP DISABLED")
                worksheet1.write(row, col + 4, "LLDP DISABLED")

                if cdp_disable:
                    worksheet1.write(row, col + 5, "Disabled")
                else:
                    worksheet1.write(row, col + 5, "Enabled", cdp_lldp_enabled)

                # increase row and reset col to 0
                row += 1
                col = 0

            self.end_connection_to_switch(switch)

        #end connection to CARMGTS1A after doing work on IOS devices
        self.end_connection_to_switch("CARMGTS1A")
        #workbook.close()



def main():
    mac = cdp_lldp_extranet_audit()
    #push_acl.get_credentials()
    mac.form_conn()
    mac.show_config()
    mac.close_conn()

if __name__ == '__main__':
    main()
