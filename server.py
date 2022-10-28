import os
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = '506D1D'
PERSONAL_SECRET = 'ca1316f53ed206e3217d41b3951fffa5'

""" Class definitions """

class Config_dict(dict): # https://www.geeksforgeeks.org/python-add-new-keys-to-a-dictionary/
    
    def __init__(self):
        self = dict()
    
    def add(self, key, value):
        self[key] = value  
    
    def check_data(self): # asserts all required datapoints are covered

        if len(self) != 5: # check all datapoints are addressed
            return False 

        key_names = ['server_port', 'client_port', 'inbox_path', \
            'send_path', 'spy_path']
        
        for key in key_names: # check keys are valid 
            if key not in self.keys():
                return False 
            
        paths = ['send_path', 'spy_path', 'inbox_path']

        for key in paths:
            path_temp = os.path.expanduser(self[key])
            if not os.path.exists(path_temp):
                return False 
        
        return True 

class Email:
    
    def __init__(self, sender, recp, time, subject, body) -> None:
        self.sender = sender 
        self.recp = recp 
        
        self.time = None # todo
        self.subject = subject
        self.body = body

    def write_to_file(self):
        # The file should be named after the Unix timestamp of the sending time
        if self.time == None: #(invalid time)
            #file_name = unknown.txt 
            pass 
        else:
            #file_name = time_epoch.txt
            pass



""" Functions """

def parse_config(file_path): # creates custom dict object, adds data from config file as specified in cmdarg, checks validity

    return_dict = Config_dict()
    
    try:
        with open(file_path, 'r') as fl:
            for line in fl:
                temp = line.strip().split("=")
                return_dict.add(temp[0], temp[1])
            
    except FileNotFoundError:
        print("config file path invalid")
        sys.exit(2)

    if not return_dict.check_data():
        print("config file has invalid data")
        sys.exit(2)

    return return_dict

def init_socket(config: dict):
    
    port = int(config['server_port'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), port))
    sock.listen(1)

    return sock

def confirm_valid(msg: str):

    valid_fns = ["EHLO", "MAIL_FROM", "RCPT_TO", "DATA", "QUIT"]

    for x in valid_fns:
        if x in msg:
            return True 

    return False 

def read_email(sock: socket.socket): # emails are inputted here
    temp = Email()
    



def write_to_file(email: Email, config: dict):

    path = os.path.expanduser(config['inbox_path'])
    
    with open(path.joinpath(email.time, 'w')) as f:
        f.write(f"From: {email.sender}")
        f.write(f"To: {email.recp}")
        f.write(f"Date: {email.time}")
        f.write(f"Subject: {email.subject}")
        f.write(f"{email.body}")

    return 



def main():
    
    if len(sys.argv) < 2:
        sys.exit(1)
    
    config = parse_config(sys.argv[1])

    server_sock = init_socket(config)

    while True:
        client_sock, addr = server_sock.accept()
        



if __name__ == '__main__': 
    main()
