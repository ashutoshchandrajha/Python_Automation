__author__ = 'ashutosh jha'

import re
import paramiko
import getpass
import time
import logging
import numpy as np
from netaddr import IPNetwork, IPAddress

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATEFORMAT = '%m/%d/%Y %I:%M:%S %p'
logging.basicConfig(filename='route_lookup.log', datefmt=DATEFORMAT, format=FORMAT, level=logging.DEBUG)

class Connection():
    def __init__(self):
        self.username = ""
        self.password = ""
        self.remote_conn = ""
        self.remote_conn_pre = paramiko.SSHClient()

    def _jump_host(self):
        #carmgts1a IP address
        jumphost_ip = '10.10.2.1'       #specify your jumphost IP
        return jumphost_ip

    def get_credentials(self):
        print("\n=== Please type in your crentials ====")
        self.username = input('login as: ')
        print("Using keyboard-interactive authentication.")
        self.password = getpass.getpass('password: ')

    def form_conn(self):
        jumphost_ip = self._jump_host()
        print("Opening connection to "+jumphost_ip)
        logging.info(self.username+' logging in '+jumphost_ip)
        self.remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.remote_conn_pre.connect(
            jumphost_ip,
            username=self.username,
            password=self.password,
            look_for_keys=False,
            allow_agent=False
        )
        self.remote_conn = self.remote_conn_pre.invoke_shell()
        self.remote_conn.keep_this = self.remote_conn_pre

    def close_conn(self):
        logging.info('Closing connection to '+self._jump_host())
        print("Closing connection to "+self._jump_host())
        self.remote_conn_pre.close()

    def remove_paging(self):
        set_terminal = "terminal length 0\n"
        self.expect_command(set_terminal)

    def expect_command(self, command='', termination_value='#'):
        if command:
            self.remote_conn.send(command)
        raw_data = self.remote_conn.recv(1)
        while True:
            time.sleep(.001)
            raw_data += self.remote_conn.recv(1024)
            decoded_data = raw_data.decode("utf-8").lower()
            check_termination = decoded_data.splitlines()[-1].strip()
            if check_termination.endswith(termination_value):
                if " " in check_termination and "#" in check_termination:
                    continue
                break
        parsed_data = ""
        parsed_data = ''.join(line for line in decoded_data if line!="\n")
        return parsed_data

class route_Check(Connection):
    def __init__(self):
        super().__init__()
        self.ip_to_search = "10.10.10.1"         #IP you want to search
        self.route_to_check = "10.10.10.0/24"    #Subnet you expect to find
        self.command_outputs = {}          #use switch name as key
        self.route_output_log = "route_output.log"
        self.extranet_switch_list = [
            "switch_1",
            "switch_2",
            "switch_3",
            "switch_4",
            "switch_5",
            "switch_6",
            "switch_7",
            "switch_8"
        ]

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

    def get_command_output(self, switch_name):
        command = "show ip route "+self.ip_to_search
        logging.info("Running command : '"+command+"'")
        print("Running command on switch : "+switch_name+" : "+command)
        var = self.expect_command(command + "\n")
        logging.info(var)
        if "route not found" in var.lower():
            self.command_outputs[switch_name] = "Route not found"
            return
        if "network not in table" in var.lower():
            self.command_outputs[switch_name] = "Route not found"
            return
        subnet_list = re.findall( r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', var)
        unique_var = np.unique(subnet_list).tolist()
        for ip in unique_var:
            if IPNetwork(self.route_to_check) in IPNetwork(ip):
                self.command_outputs[switch_name] = ip
                break
        if switch_name not in self.command_outputs:
            self.command_outputs[switch_name] = "Route is not there"

    def check_route(self):
        for switch in self.extranet_switch_list:
            self.open_connection_to_switch(switch)
            self.get_command_output(switch)
            self.end_connection_to_switch(switch)
        #for switch in self.command_outputs:
        print("Writing results to 'route_output.log' file." )
        self.open_route_output_file()
        self.close_route_output_file()

    def open_route_output_file(self):
        self.route_out = open(self.route_output_log, "w")
        for switch in self.extranet_switch_list:
            self.route_out.write(str("Route on switch : "+switch+" : "+self.command_outputs[switch]+"\n"))

    def close_route_output_file(self):
        self.route_out.close()

def main():
    route_check = route_Check()
    route_check.get_credentials()
    route_check.form_conn()
    route_check.check_route()
    route_check.close_conn()

if __name__ == '__main__':
    main()
