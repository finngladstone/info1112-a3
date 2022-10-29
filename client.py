import os
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
            flush_print("Config_parser: missing property")
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

def email_parser(path: str):
    email_ls = []
    email_dir = os.path.expanduser(path)
    email_path_ls = []

    # constructs list of email paths
    for filename in os.scandir(email_dir):
        if not filename.is_file():
            continue
        else:
            flush_print(f"Email dir: {email_dir}")
            email_item_path = os.path.join(os.path.abspath(email_dir), filename)
            email_path_ls.append(email_item_path)

    # iterates through email paths and creates Email objects if valid 
    for email_path in email_path_ls:

        email_dict = Custom_dict()

        try:
            with open(email_path, 'r') as fl:
                for i in range(0, 4):
                    temp = fl.readline().strip().split(": ")
                    email_dict.add(temp[0], temp[1])

                data = fl.read()
                email_dict.add("Data", data)
                    

        except OSError as e:
            flush_print(f"Could not read file {email_path}")
            flush_print(e)
            sys.exit(2)

        valid_keys = {"From", "To", "Date", "Subject", "Data"}
        for key in email_dict.keys():
            if key not in valid_keys:
                flush_print(f"C: {email_path} Bad formation")
                break 

        else:
            temp = Email(
                email_dict['From'],
                email_dict['To'],
                email_dict['Date'],
                email_dict['Subject'],
                email_dict['Data']
            )

            email_ls.append(temp)

        
    return email_ls

def main():
    if len(sys.argv) < 2:
        flush_print("No config path given")
        sys.exit(1)
    
    config_dict = config_parser(sys.argv[1])
    Email_objs = email_parser(config_dict['send_path'])

    sys.exit(0)


if __name__ == '__main__':
    main()