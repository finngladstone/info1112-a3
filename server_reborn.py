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

def get_client_prefix(request : str):
    client_response_ls = request.strip().split()
    return client_response_ls[0]

def check_email_valid(email_address:str): # todo
    return True 


class Custom_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

class Email():
    def __init__(self) -> None:
        self.sender = None 
        self.recpt = [] # list of recipients
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
        command_dict.add("EHLO", self.parse_EHLO)
        command_dict.add("QUIT", self.parse_QUIT)
        command_dict.add("RSET", self.parse_RSET)
        command_dict.add("NOOP", self.parse_NOOP)
   


        if self.state == 1:
            command_dict.add("MAIL", self.parse_MAIL)
            command_dict.add("AUTH", self.parse_AUTH)

        if self.state == 2:
            command_dict.add("RCPT", self.parse_RCPT)
            command_dict.add("DATA", self.parse_DATA)

        return command_dict


    def parse_EHLO(self):

        ls = self.current_request.split()
        if len(ls) < 2:
            self.send_501()
            return  

        try:
            temp = ipaddress.ip_address(ls[1])
        except ValueError:
            self.send_501()
            return  

        response_builder(self.client, f"250 {temp}")
        self.state = 1

    def parse_QUIT(self):

        if self.current_request != "QUIT":
            self.send_501()
            return  
        else: 
            pass # close the whole joint 

    def parse_RSET(self):
        
        temp = self.current_request.strip()
        if temp != "RSET":
            self.send_501()

        else: 
            self.state = 0
            self.current_email = None 
            response_builder(self.client, "250 Requested mail action okay completed")


    def parse_MAIL(self):

        temp = self.current_request.strip().replace(":", " ").split()
        if len(temp) != 3 or temp[1] != "TO":
            self.send_501()
            return 
        
        if not check_email_valid(temp[2]):
            self.send_501()
            return 

        self.current_email = Email() 
        self.current_email.sender = temp[2]

        return  
    
    def parse_RCPT(self):

        temp = self.current_request.strip().replace(":", " ").split()
        if len(temp) != 3 or temp[1] != "TO":
            self.send_501()
            return

        if not check_email_valid(temp[2]):
            self.send_501()
            return 

        self.current_email.recpt.append(temp[2])
         

    def parse_NOOP(self):
        temp = self.current_request.strip()
        if temp != "NOOP":
            self.send_501()
        else:
            response_builder(self.client, "250 Requested mail action okay completed") 

    def parse_AUTH(self):
        pass 

    def parse_DATA(self):
        pass 


    """ CODES """

    def send_220(self):
        response_builder(self.client, "220: Service ready")

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
        server.send_220()

        while True: 
            server.get_request() # updates server.current_request pointer
            
            prefix = get_client_prefix(server.current_request)
            available_commands = server.get_command_dict()
            
            try: 
                available_commands[prefix]()
            except IndexError:
                if prefix in server.possible_commands:
                    server.send_504()
                else:
                    server.send_500()



        

     

if __name__ == '__main__':
    main()