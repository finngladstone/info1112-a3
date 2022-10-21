import os
from pathlib import Path
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = ''
PERSONAL_SECRET = ''



""" Class Definitions """



class Config_dict(dict):
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


""" Helper Functions """



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

    if not return_dict.check_data():
        print("config file has invalid data")
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
            sys.stdout.flush(f"C: {path}: Bad formation")
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


""" Socket Helpers"""

def init_socket(config: dict):



def main():

    if len(sys.argv) < 2:
        sys.exit(1)
    
    config = parse_config(sys.argv[1])
    to_send = init_email_ls(config)
    


if __name__ == '__main__':
    main()
