__author__ = 'ashjha'


#This script will push some user defined access lists
#to a list of switches and log the outputs

import logging
from netaddr import IPNetwork, IPAddress

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATEFORMAT = '%m/%d/%Y %I:%M:%S %p'
logging.basicConfig(filename='push_ACL.log', datefmt=DATEFORMAT, format=FORMAT, level=logging.DEBUG)

class push_ACL(Connection):
    def __init__(self):
        super().__init__()
        self.command_outputs = {}          #use switch name as key
        self.route_output_log = "route_output.log"
        """
            put int all the ACLs to be pushed here
        """
        self.acl = "IP access-list standard ----------"
        self.acl_1 = "permit 234.65.23.0 0.0.0.3"
        self.exit_acl = "exit"

        self.switch_list = ["Switch1",
            "Switch2",
            "Switch3",
            "Switch4",
            "Switch5",
            "Switch6",
            "Switch7",
            "Switch8"]

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

    def get_command_output(self, command):
        logging.info("Running command '"+command+"'")
        print("Running command : "+command)
        self.expect_command(command + "\n")

    def get_show_command_output(self, command):
        logging.info("Running command '"+command+"'")
        print("Running command : "+command)
        self.expect_command(command + "\n")

    def open_route_output_file(self):
        self.route_out = open(self.route_output_log, "w")
        for switch in self.switch_list:
            self.route_out.write(str("Route on switch : "+switch+" : "+self.command_outputs[switch]+"\n"))

    def push_config(self):
        print("Starting to push ACL")
        for switch in self.switch_list:
            self.open_connection_to_switch(switch)
            self.get_command_output("conf t")
            """
                remember to get in the configuration mode to execute commands
                execute every command one by one and log their output
            """
            self.get_command_output(self.acl)
            self.get_command_output(self.acl_1)
            self.get_command_output(self.exit_acl)
            #self.get_command_output("sh ip access-lists unicast-to-clients | i 206.200.40.0")
            self.end_connection_to_switch(switch)
        print("ACL Update complete")

    def close_route_output_file(self):
        self.route_out.close()

def main():
    push_acl = push_ACL()
    push_acl.form_conn()
    #push_acl.open_route_output_file()
    push_acl.push_config()
    #push_acl.close_route_output_file()


if __name__ == '__main__':
    main()
