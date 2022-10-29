import os
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = ''
PERSONAL_SECRET = ''

""" Generic helper functions """

def flush_print(x):
    print(x, flush=True)

""" Class Definitions """

class Config_dict(dict):
    def __init__(self):
        self = dict()
    
    def add(self, key, value):
        self[key] = value  
    
    def check_data(self): # asserts all required datapoints are covered

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


class Email():
    def __init__(self, sender, recpt, date, subj, data) -> None:
        self.sender = sender 
        self.recpt = recpt
        self.date = date
        self.subj = subj
        self.data = data

    def fix_recpt(self):
        if not "," in self.recpt:
            recpt_temp = [self.recpt]
        else:
            recpt_temp = self.recpt.split(",")

        self.recpt = recpt_temp
        return


""" Email parsing functions """


def parse_config(file_path):

    return_dict = Config_dict()
    
    try:
        with open(file_path, 'r') as fl:
            for line in fl:
                temp = line.strip().split("=")
                return_dict.add(temp[0], temp[1])
            
    except FileNotFoundError: # can't find config file
        sys.exit(2)

    if not return_dict.check_data(): # config file invalid data
        sys.exit(2)

    return return_dict


def init_email(path): 

    # data is handled in a weird way 
    # no checks

    fl_dict = dict()

    with open(path, 'r') as fl:
        for i in range(0, 4):
            temp = fl.readline().strip().split(": ")
            fl_dict[temp[0]] = temp[1]

        fl_dict['data'] = fl.readlines()

    keywords = ['From', 'To', 'Date', 'Subject']

    for i in keywords: # could abstract 
        if i not in fl_dict:
            flush_print(f"C: {path}: Bad formation")
            return None

    reval = Email(fl_dict['From'], fl_dict['To'], fl_dict['Date'], \
        fl_dict['Subject'], fl_dict['data'])

    reval.fix_recpt() # handles multiple emails 

    return reval

def init_email_ls(config:dict): # https://www.geeksforgeeks.org/how-to-iterate-over-files-in-directory-using-python/

    emails = []

    real_path = os.path.expanduser(config['send_path'])

    for filename in os.scandir(real_path):
        if not filename.is_file():
            continue

        new_path = os.path.join(real_path, filename)
        emails.append(init_email(new_path))

    return emails

""" SOCKET HELPER FUNCTIONS """

def check_server_response(client_sock: socket.socket, expected_code: int):

    server_response = str(client_sock.recv(256))
    ls = server_response.split()

    if expected_code != ls[0]:
        raise ValueError(f"Expected server code {expected_code} \n Actual code {ls[0]}") 

def start_socket(config:dict):

    port = int(config['server_port'])
    hostnm = socket.gethostname()

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((hostnm, port))

    return client_sock

def close_socket(sock: socket.socket):

    sock.send("QUIT")
    check_server_response(sock, 221)
    sock.close()
    
    return 

""" EMAIL HELPER FNS """

def EHLO(sock: socket.socket):
    pass 

def MAIL_FROM(sock: socket.socket, email: Email):
    pass 

def RCPT_TO(sock: socket.socket, email: Email):
    pass 

def DATA(sock: socket.socket, email: Email):
    # handle code 354 in here
    pass 



""" EMAIL SENDER FN"""

def send_email(email: Email, sock: socket.socket):
    
    with sock:
        check_server_response(sock, 220)
        
        EHLO(sock)
        check_server_response(sock, 250)

        MAIL_FROM(sock, email)
        check_server_response(sock, 250)

        RCPT_TO(sock, email)
        check_server_response(sock, 250)

        DATA(sock, email)
        check_server_response(sock, 250)

    return None 




def main():

    if len(sys.argv) < 2:
        sys.exit(1)
    
    config = parse_config(sys.argv[1])
    to_send = init_email_ls(config)

    for email_item in to_send:
        send_sock = start_socket(config)

        send_email(email_item, send_sock)

        close_socket(send_sock)

    
    


if __name__ == '__main__':
    main()
