import ipaddress
import os
import socket
import sys
import time

def flush_print(x):
    print(x, flush=True)

def response_builder(sock: socket.socket, response: str):
    flush_print(f"S: {response}\r")
    sock.send(f"{response}\r\n".encode('ascii'))

def check_client_prefix(expected_prefix: str, request: str):
    client_response_ls = request.split()

    if client_response_ls[0] != expected_prefix:
        return False 
    return True 


class Custom_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

class Email():
    def __init__(self) -> None:
        self.sender = None 
        self.recpt = None # list of recipients
        self.date = None
        self.subj = None
        self.data = None # String array of each line in the file 

    def write_to_file(self):
        pass

class Server():
    def __init__(self):
        self.email = None 
        self.config = None 
        self.socket = None 
        self.client = None 
        self.current_email = None 
        self.current_request = None 

        self.state = 0
        self.possible_commands = [
            "EHLO", "MAIL", "RCPT", "DATA", "RSET", "NOOP",
            "AUTH", "QUIT"
        ]

        """ 
        0 = no ehlo
        1 = ehlo 
        2 = mail
        """

    def init_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hn = socket.gethostname()
        port = int(self.config['server_port'])

        try:
            sock.bind((hn, port))
            sock.listen(1)
        except socket.error:
            flush_print("Failed to establish connection")
            return None 
        
        self.socket = sock 

    def init_config(self, file_path: str): 
        reval = Custom_dict()

        try: 
            with open(file_path, 'r') as fl:
                for line in fl:
                    temp = line.strip().split("=")
                    reval.add(temp[0], temp[1])

        except FileNotFoundError:
            flush_print("Config file could not be found.")  
            sys.exit(2)

        key_names = ['server_port', 'inbox_path']

        for key in key_names:
            if key not in reval.keys():
                # Config parser invalid key 
                sys.exit(2) 

        path_temp = os.path.expanduser(reval['inbox_path'])
        if not os.path.exists(path_temp): #invalid path 
            flush_print("Path invalid in server_config")
            sys.exit(2) 

        if not reval['server_port'].isnumeric(): #invalid port
            sys.exit(2)

        self.config = reval

    def get_request(self):
        request = self.client.recv(256).decode().strip()
        self.current_request = request
        flush_print(f"C: {request}")

    def get_command_dict(self):
        
        command_dict = Custom_dict()
        command_dict.add("EHLO", self.parse_EHLO())
        command_dict.add("QUIT", self.parse_QUIT())
        command_dict.add("RSET", self.parse_RSET())
        command_dict.add("NOOP", self.parse_NOOP())
   


        if self.state == 1:
            command_dict.add("MAIL", self.parse_MAIL())
            command_dict.add("AUTH", self.parse_AUTH())

        if self.state == 2:
            command_dict.add("RCPT", self.parse_RCPT())
            command_dict.add("DATA", self.parse_DATA())


    def send_220(self):
        response_builder(self.client, "220: Service ready")

    def parse_EHLO(self):

        ls = self.current_request.split()
        if len(ls) < 2:
            

        pass 

    def parse_QUIT(self):
        pass 

    def parse_RSET(self):
        pass 

    def parse_MAIL(self):
        pass 

    def parse_NOOP(self):
        pass 

    def parse_AUTH(self):
        pass 

    def parse_RCPT(self):
        pass 

    def parse_DATA(self):
        pass 

    """ ERROR MESSAGES"""

    def send_500(self):
        response_builder(self.client, "500 Syntax error, command unrecognized")

    def send_501(self):
        response_builder(self.client, "501 Syntax error in parameters or arguments")

    def send_503(self):
        response_builder(self.client, "503 Bad sequence of commands")

    def send_504(self):
        response_builder(self.client, "504 Command parameter not implemented")
    
    def send_535(self):
        response_builder(self.client, "535 Authentication credentials invalid")

def main():
    server = Server() 

    if len(sys.argv) < 2:
        sys.exit(1)

    server.init_config(sys.argv[1])
    server.init_socket()

    while True:
        server.client, addr = server.socket.accept()
        server.SEND_220()

        while True: 
            server.get_request() 
            try: 
                server.command_dict[server.current_request]
            except IndexError:
                flush_print("")



        

     

if __name__ == '__main__':
    main()