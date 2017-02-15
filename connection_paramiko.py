__author__ = 'ashutosh jha'

import paramiko
import getpass

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
