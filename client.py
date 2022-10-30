import os
from re import S
import socket
import sys


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

    def fix_recpt(self):
        if not "," in self.recpt:
            recpt_temp = [self.recpt]
        else:
            recpt_temp = self.recpt.split(",")
        self.recpt = recpt_temp
        return


"""
CONFIG_PARSER()

Using 1st cmdline argument(path to config file)'
- Check if exists
- Create dictionary of keys/values 
- Check that keys are valid 
- Check that port values are numeric 
- Return config dictionary obj

"""

def config_parser(file_path): # handles creation + all error checks for config

    reval = Custom_dict()

    try:
        with open(file_path, 'r') as fl:
            for line in fl:
                temp = line.strip().split("=")
                reval.add(temp[0], temp[1])

    except FileNotFoundError:
        flush_print("Config file could not be found")
        sys.exit(2)

    key_names = ['server_port', 'send_path']

    for key in key_names:
        if key not in reval.keys():
            # flush_print("Config_parser: missing property")
            sys.exit(2)

    # check that send_path is valid 
    path_temp = os.path.expanduser(reval['send_path'])
    if not os.path.exists(path_temp):
        flush_print("Config_parser: invalid path to send_path")
        sys.exit(2)

    if not reval['server_port'].isnumeric():
        flush_print("Config_parser: port is not numeric")
        sys.exit(2)

    return reval 

""" 
EMAIL_PARSER()

Using send_path: 
    - rectify relative paths 
    - create list of paths to email txt files 
    - iterate email text files and check validity 
    - if validity checks pass, create Email object for each file 
    - return list of email objs

"""

def email_parser(path: str):

    email_ls = []
    email_path_ls = []
    path_temp = os.path.expanduser(path)
    
    if "./" in path_temp:
        path_temp = path_temp.replace("./", os.getcwd() + "/")

    # constructs list of email paths
    for filename in os.scandir(path_temp):

        if not filename.is_file():
            continue
        else:
            email_item_path = os.path.join(path_temp, filename.name)
            email_path_ls.append(email_item_path)
            email_path_ls.sort()

    # iterates through email paths and creates Email objects if valid 
    for email_path in email_path_ls:

        email_dict = Custom_dict()

        try:
            with open(email_path, 'r') as fl:
                for i in range(0, 4):
                    temp = fl.readline().strip().split(": ")
                    email_dict.add(temp[0], temp[1])

                data = fl.read() # reads entire data chunk 
                data = data.split("\n")
                
                if "" in data: # clean after split
                    data.remove("")
                
                email_dict.add("Data", data)
                    

        except OSError as e:
            flush_print(f"Could not read file {email_path}")
            sys.exit(2)

        except IndexError:
            flush_print(f"C: {email_path}: Bad formation")
            continue 

        valid_keys = {"From", "To", "Date", "Subject", "Data"}
        for key in email_dict.keys():
            if key not in valid_keys:
                flush_print(f"C: {email_path} Bad formation")
                break 

        else:

            temp = Email(
                email_dict['From'],
                email_dict['To'].split(","),
                email_dict['Date'],
                email_dict['Subject'],
                email_dict['Data']
            )

            email_ls.append(temp)

        
    return email_ls

""" 
# Socket helper functions:

START_SOCKET() - using given port, create socket obj, connect to server
CHECK_SERVER_CODE() - adapted from polak's goated tut, checks response code 

"""

def start_socket(config: dict):
    port = int(config['server_port'])
    hostnm = socket.gethostname()

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((hostnm, port))

    except socket.error :
        flush_print("C: Cannot establish connection")
        sys.exit(3)

    return client_sock

def check_server_code(client_sock: socket.socket, expected_code: int):
    # no error checking on recv()

    server_response = (client_sock.recv(256)).decode()
    flush_print(f"S: {server_response.strip()}\r")

    ls = server_response.split()

    if expected_code != int(ls[0]):
        raise ValueError(f"Expected code {expected_code}, actual code {ls[0]}")

    return None

def check_service_ready(client_sock: socket.socket):
    
    try:
        server_response = (client_sock.recv(256)).decode()
        flush_print(f"S: {server_response.strip()}\r")

        server_response_ls = server_response.split()

        if server_response_ls[0] == '220':
            pass 
    except:
        flush_print("220 Not received")


""" EMAIL SENDER FNS """

def request_builer(sock:socket.socket, request: str): # flushes
    flush_print(f"C: {request}\r")
    sock.send(f"{request}\r\n".encode('ascii'))

def EHLO(sock: socket.socket):
    request = "EHLO 127.0.0.1"
    request_builer(sock, request)
    

def MAIL_FROM(sock: socket.socket, email: Email):
    request = f"MAIL FROM:{email.sender}"
    request_builer(sock, request)
     

def RCPT_TO(sock: socket.socket, email: Email):

    for recipient in email.recpt:
        request = f"RCPT TO:{recipient}"
        request_builer(sock, request)
        check_server_code(sock, 250)


def DATA(sock: socket.socket, email: Email):
    
    # sock.send("DATA\r\n".encode('ascii'))
    request_builer(sock, "DATA")
    check_server_code(sock, 354)
    
    # sock.send(f"Date: {email.date}\r\n".encode('ascii'))
    request_builer(sock, f"Date: {email.date}")
    check_server_code(sock, 354)

    # sock.send(f"Subject: {email.subj}\r\n".encode('ascii'))
    request_builer(sock, f"Subject: {email.subj}")
    check_server_code(sock, 354)

    for line in email.data:
        request_builer(sock, line)
        check_server_code(sock, 354)


    # sock.send(".\r\n".encode('ascii'))
    
    request_builer(sock, ".")
    check_server_code(sock, 250)

def QUIT(sock: socket.socket):
    request_builer(sock, "QUIT")
    # sock.send("QUIT\r\n".encode('ascii'))


def main():
    if len(sys.argv) < 2:
        # flush_print("No config path given")
        sys.exit(1)
    
    config_dict = config_parser(sys.argv[1])
    Email_objs = email_parser(config_dict['send_path'])

    for email in Email_objs:
        sock = start_socket(config_dict)
        check_service_ready(sock)

        EHLO(sock)
        check_server_code(sock, 250) 

        MAIL_FROM(sock, email)
        check_server_code(sock, 250)

        RCPT_TO(sock, email)
        # checks handled inside rcpt_to()

        DATA(sock, email)
        # server code checks are handled within data() block

        QUIT(sock)
        check_server_code(sock, 221)
        sock.close()

    sys.exit(0)


if __name__ == '__main__':
    main()