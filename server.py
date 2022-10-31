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
    



""" REQUEST PARSERS """

def parse_EHLO(request_str:str):
    pass 

    #todo check ip validity somewhere

def parse_MAIL_FROM(request_str: str):
    pass 

def parse_MAIL_TO(request_str: str):
    pass 


""" SEND / RECEIVE """

def get_client_message(sock: socket.socket):
    # flush print c: ...
    pass 

""" SOCKET FNS """

def init_socket(config: dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((socket.gethostname(), config['server_port']))
        sock.listen(1)
    
    except socket.error:
        print("Failed to init sock")

    return sock 


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    config_dict = config_parser(sys.argv[1])
    pass


if __name__ == '__main__':
    main()