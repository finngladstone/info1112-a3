import os
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = '506D1D'
PERSONAL_SECRET = 'ca1316f53ed206e3217d41b3951fffa5'

class Config_dict(dict): # https://www.geeksforgeeks.org/python-add-new-keys-to-a-dictionary/
    
    def __init__(self):
        self = dict()
    
    def add(self, key, value):
        self[key] = value  
    
    def check_data(self):
        if len(self) == 5:
            pass 
        else:
            return False 

        key_names = ['server_port', 'client_port', 'inbox_path', \
            'send_path', 'spy_path']
        
        for key in key_names:
            if key not in self:
                return False 

        

def parse_config(file_path):

    return_dict = Config_dict()
    
    try:
        with open(file_path, 'r') as fl:
            for line in fl:
                temp = line.strip().split("=")
                return_dict.add(temp[0], temp[1])
            
    except FileNotFoundError:
        print("config file path invalid")
        sys.exit(2)

    print(return_dict)

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









    

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    parse_config(sys.argv[1])


if __name__ == '__main__':
    main()