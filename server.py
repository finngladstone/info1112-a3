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

def init_socket(config: dict): # initiates socket using config dictionary

    port = int(config['server_port'])
    hostnm = socket.gethostname()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind( (hostnm, port) )
    sock.listen(5) # will need to modify this for multiprocessing 

    return sock


def establish_connection(sock: socket.socket):

    while True:
        client_conn, client_addr = sock.accept()
        sys.stdout.flush("")

        client_conn.send("Have a great day./n".encode())

        client_conn.close()
        break



def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    config = parse_config(sys.argv[1])
    server_sock = init_socket(config)

    establish_connection(server_sock)

    
    


if __name__ == '__main__':
    main()
