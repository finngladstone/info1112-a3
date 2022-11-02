import ipaddress
import os
import socket
import sys
import time


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = ''
PERSONAL_SECRET = ''

def flush_print(x):
    print(x, flush=True)

class Custom_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

class Email():
    def __init__(self, sender, recpt, date, subj, data) -> None:
        self.sender = sender 
        self.recpt = recpt # list of recipients
        self.date = date
        self.subj = subj
        self.data = data # String array of each line in the file 

def config_parser(file_path: str): # missing some checks 

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

    return reval

def email_writer(config: dict, mail: Email):
    
    email_name = int(time.time()) # will be fixed later down the line
    
    email_path = os.path.join(email_name, config['send_path']) 
    with open(email_path, 'x') as fl:
        fl.write(f"From: {mail.sender}\n")
        fl.write(f"To: {mail.recpt}\n")
        fl.write(f"Date: {mail.date}\n")
        fl.write(f"Subject: {mail.subj}\n")
        
        for line in mail.data:
            fl.write(line + "\n")
    


""" SEND / RECEIVE """

def request_builder(sock: socket.socket, request: str):
    flush_print(f"S: {request}\r")
    sock.send(f"{request}\r\n".encode('ascii'))

def check_client_prefix(expected_prefix: str, client_string: str):
    
    client_response_ls = client_string.split()
    if client_response_ls[0] != expected_prefix:
        raise ValueError(f"Expected {expected_prefix}: Received {client_response_ls[0]}")

""" SERVICE READY """

def send_220(client_sock: socket.socket):
    request_builder(client_sock, "220: Service ready")

""" EHLO """

def catch_ehlo(client_sock: socket.socket):

    client_response = client_sock.recv(256).decode()
    flush_print(f"C: {client_response.strip()}")

    client_response_ls = client_response.strip().split()
    check_client_prefix("EHLO", client_response_ls[0])

    try:
        check_ip(client_response_ls[1])
    except ValueError: # send error code to client, reset
        request_builder(client_sock, "501 Syntax error in parameters or arguments")
        return False 

    request_builder(client_sock, f"250 {client_response_ls[1]}")
    return True 

def check_ip(ip: str): 
    ip_parse = ipaddress.ip_address(ip)

""" MAIL """

def mail_start(client_sock: socket.socket):
    pass 

""" SOCKET FNS """

def init_socket(config: dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    hostname = socket.gethostname()
    port = int(config['server_port'])

    try:
        sock.bind((hostname, port))
        sock.listen(1)
    
    except socket.error:
        print("Failed to init sock")

    return sock 


""" PROGRAM STATE FNS """



def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    config_dict = config_parser(sys.argv[1])
    server_sock = init_socket(config_dict)

    while True: 
        client_sock, addr = server_sock.accept() # init conn
        send_220(client_sock) # Service ready

        catch_ehlo(client_sock)

            
        


        





    


if __name__ == '__main__':
    main()