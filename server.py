import ipaddress # needs to go 
import os
import socket
import sys
import time
from datetime import datetime

import base64, hmac, hashlib, secrets, string

PERSONAL_ID = '506D1D'
PERSONAL_SECRET = 'ca1316f53ed206e3217d41b3951fffa5'

def flush_print(x):
    print(x, flush=True)

def response_builder(sock: socket.socket, response: str):
    flush_print(f"S: {response}\r")
    sock.send(f"{response}\r\n".encode('ascii'))

def response_builder_ehlo_auth(sock: socket.socket, response:str): 
    flush_print(f"S: {response}\r")
    flush_print(f"S: 250 AUTH CRAM-MD5\r")
    sock.send((f"{response}\r\n" + "250 AUTH CRAM-MD5\r\n").encode('ascii'))

def response_builder_b64(sock: socket.socket, response): 
    flush_print(f"S: 334 {response}\r")
    code = "334 ".encode('ascii')
    sock.send(code + response + "\r\n".encode('ascii'))

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
        self.data = [] # String array of each line in the file 

    def write_to_file(self, save_path):

        # Date: Mon, 14 Sep 1987 23:07:00 +1000

        for line in self.data:
            line_ls = line.split(": ")
            if line_ls[0] == "Date":
                try:
                    time_interpreter = datetime.strptime(line_ls[1], "%a, %d %b %Y %H:%M:%S %z")
                    fl_name = f"{int(datetime.timestamp(time_interpreter))}.txt"
                    break 
                except:
                    continue

        else:
            fl_name = "unknown.txt"

        fl_path = os.path.join(save_path, fl_name)

        with open(fl_path, 'x') as fl:
            fl.write(f"From: {self.sender}\n")

            s = ""
            for address in self.recpt:
                s += f"{address},"
            fl.write(f"To: {s.rstrip(',')}\n")

            for line in self.data:
                fl.write(f"{line}\n")
                



        pass

class Server():
    def __init__(self):
        self.email = None 
        self.config = None 
        self.socket: socket.socket = None 
        self.client: socket.socket = None 
        self.current_email = None 
        self.current_request = None 

        self.state = 0

        """ 
        program states
        0 = no ehlo
        1 = ehlo 
        2 = mail
        3 = getting_auth
        """

        self.possible_commands = [
            "EHLO", "MAIL", "RCPT", "DATA", "RSET", "NOOP",
            "AUTH", "QUIT"
        ]

        

    def init_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hn = socket.gethostname()
        port = int(self.config['server_port'])

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((hn, port))
            sock.listen(1)
        except socket.error:
            flush_print("Failed to establish connection")
            sys.exit(1)
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
        flush_print(f"C: {request}\r")

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

        if self.state == 3:
            command_dict.add("AUTH", self.parse_AUTH)

        return command_dict


    def parse_EHLO(self):

        ls = self.current_request.split()
        if len(ls) != 2:
            self.send_501()
            return  

        try:
            temp = ipaddress.ip_address(ls[1])
        except ValueError:
            self.send_501()
            return  

        response_builder_ehlo_auth(self.client, f"250 {temp}")
        self.state = 1

    def parse_QUIT(self):

        if self.current_request != "QUIT":
            self.send_501()
            return  
        else: 
            self.send_221()
            self.client.shutdown(1)
            self.client.close()
            self.client = None # clear pointer
            

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

        if len(temp) != 3 or temp[1] != "FROM":
            self.send_501()
            return 
        
        if not check_email_valid(temp[2]):
            self.send_501()
            return 

        self.current_email = Email() 
        self.current_email.sender = temp[2]

        response_builder(self.client, "250 Requested mail action okay completed")
        self.state = 2

        return  
    
    def parse_RCPT(self):

        if self.current_email == None:
            self.send_503()
            return

        temp = self.current_request.strip().replace(":", " ").split()
        if len(temp) != 3 or temp[1] != "TO":
            self.send_501()
            return

        if not check_email_valid(temp[2]):
            self.send_501()
            return 

        self.current_email.recpt.append(temp[2])
        response_builder(self.client, "250 Requested mail action okay completed")
         

    def parse_NOOP(self):
        temp = self.current_request.strip()
        if temp != "NOOP":
            self.send_501()
        else:
            response_builder(self.client, "250 Requested mail action okay completed") 


    def parse_AUTH(self):

        temp = self.current_request.strip().split()
        if len(temp) != 2:
            self.send_501()
            return
        
        if temp[1] != "CRAM-MD5":
            self.send_504()
            return 

        self.state = 3

        challenge = "".join(secrets.choice(string.ascii_letters + string.digits) for x in range(32))

        challenge = challenge.encode('ascii')
        challenge = base64.b64encode(challenge)

        response_builder_b64(self.client, challenge)

    def parse_AUTH_token(self):
        pass 

    def parse_DATA(self):

        if len(self.current_email.recpt) == 0:
            self.send_503()
            return 
        else:
            response_builder(self.client, "354 Start mail input end <CRLF>.<CRLF>")

        while True:
            self.get_request() 
            if self.current_request == ".":
                break 
            else:
                self.current_email.data.append(self.current_request)
                response_builder(self.client, "354 Start mail input end <CRLF>.<CRLF>")
                continue
        
        response_builder(self.client, "250 Requested mail action okay completed")
        
        self.current_email.write_to_file(
            os.path.expanduser(self.config['inbox_path'])
        )
        self.current_email = None 
        self.state = 1

        return 


    """ CODES """

    def send_220(self):
        response_builder(self.client, "220 Service ready")

    def send_221(self):
        response_builder(self.client, "221 Service closing transmission channel")

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
        server.state = 0
        sock, address = server.socket.accept()
        
        server.client = sock
        server.send_220()

        while True: 
            server.get_request() # updates server.current_request pointer

            try: 
                prefix = get_client_prefix(server.current_request)
            except:
                flush_print("S: Connection lost")
                break
            
            available_commands = server.get_command_dict()
            
            try: 
                available_commands[prefix]()
            except KeyError:
                if prefix in server.possible_commands:
                    server.send_503()
                
                elif server.state == 3:
                    server.parse_AUTH_token()
                else:
                    server.send_500()

            if server.client == None:
                break



        

     

if __name__ == '__main__':
    main()