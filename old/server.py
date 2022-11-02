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

def len_check_3(x):
    if len(x) != 3:
        return False 

    return True 



""" DATA STRUCTURES """

valid_args = ['EHLO', 'MAIL', 'RCPT', 'DATA', 'RSET', 
        'NOOP', 'AUTH', 'QUIT']

class Custom_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

class Email():
    def __init__(self) -> None:
        self.sender = None 
        self.recpt = None # list of recipients
        self.date = None
        self.subj = None
        self.data = None # String array of each line in the file 

    def write_to_file(self):
        pass 

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
    


""" FORMATTERS + CHECKS FOR REQUESTS + RESPONSES """

def check_email_valid(email: str):
    return True 
    

def request_builder(sock: socket.socket, request: str):
    flush_print(f"S: {request}\r")
    sock.send(f"{request}\r\n".encode('ascii'))

def check_client_prefix(expected_prefix: str, client_string: str):
    
    client_response_ls = client_string.split()
    if client_response_ls[0] != expected_prefix:
        return False 

    return True

def get_client_prefix(client_string:str): 
    client_response_ls = client_string.split()
    return client_response_ls[0]

def get_client_request(sock: socket.socket):
    request = sock.recv(256).decode().strip() 
    flush_print(f"C: {request}")

    return request  


""" PARSE REQUESTS + SEND RESPONSES """

def send_220(client_sock: socket.socket):
    request_builder(client_sock, "220: Service ready")

def parse_EHLO(client_sock: socket.socket, client_response: str):

    client_response_ls = client_response.strip().split()
    if len(client_response_ls) < 2:
        request_builder(client_sock, "501 Syntax error in paramters or arguments")
        return False 

    try: 
        temp = ipaddress.ip_address(client_response_ls[1])
    except ValueError:
        request_builder(client_sock, "501 Syntax error in parameters or arguments")
        return False 

    request_builder(client_sock, f"250 {temp}")
    return True 
     

def parse_QUIT(client_sock: socket.socket, client_response: str):

    client_response_ls = client_response.strip().split()
    if len(client_response_ls) > 1:
        request_builder("501 Syntax error in parameters or arguments")
        return False 
    else: 
        request_builder("221 Service closing transmission tunnel")
        return True 
        client_sock.close()
 

def parse_MAIL_FROM(client_sock: socket.socket, client_request: str) -> Email: 

    client_response_ls = client_request.strip().replace(":", " ").split()
    print(client_response_ls)

    if len (client_response_ls) != 3:
        request_builder(client_sock, "501 Syntax error in parameters or arguments")
        return None 

    if client_response_ls[1] != "FROM":
        request_builder(client_sock, "503 Bad sequence of commands")
        return None 

    reval = Email() 
    reval.sender = client_response_ls[2]

    return reval 

def parse_RCPT(client_sock: socket.socket, client_request: str):
    pass 

def parse_DATA(client_sock: socket.socket, client_request: str):
    pass 

def parse_RSET(client_sock: socket.socket, client_request: str):
    pass 

def parse_NOOP(client_sock: socket.socket, client_request: str):
    pass 

def parse_AUTH(client_sock: socket.socket, client_request:str):
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


""" MAIN """

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    config_dict = config_parser(sys.argv[1])
    server_sock = init_socket(config_dict) 

    while True: 
        client_sock, addr = server_sock.accept() # init conn
        send_220(client_sock) # Service ready

        ehlo = False 
        mail = False 
        auth = False 
        mail_obj = None 

        """ NON-FINITE STATE MACHINE """

        while True: 
            while not ehlo:
                """ 
                When not ehlo but connected, client can access 
                    - ehlo 
                    - quit
                    - rset (does nothing)
                """
                client_request = get_client_request(client_sock)

                if check_client_prefix('EHLO', client_request):
                    if parse_EHLO(client_sock, client_request):
                        ehlo = True 
                    
                elif check_client_prefix('QUIT', client_request):
                    parse_QUIT(client_sock, client_request)

                elif check_client_prefix('RSET', client_request):
                    parse_RSET(client_sock, client_request)

                else:
                    for arg in valid_args:
                        if check_client_prefix(arg, client_request):
                            request_builder(client_sock, "503 Bad sequence of commands")
                            break 
                    else:
                        request_builder(client_sock, "501 Syntax error, command unrecognized")
                
            
            while ehlo and not mail:

                """ 
                with ehlo, valid client commands are: 
                    - ehlo
                    - quit
                    - reset 
                    - mail to 
                    - auth  
                """

                client_request = get_client_request(client_sock)

                if check_client_prefix('EHLO', client_request):
                    if not parse_EHLO(client_sock, client_request):
                        ehlo = False 

                elif check_client_prefix('QUIT', client_request):
                    parse_QUIT(client_sock, client_request)
                
                elif check_client_prefix('RSET', client_request):
                    if parse_RSET(client_sock, client_request):
                        ehlo = False 

                elif check_client_prefix('MAIL', client_request):
                    val = parse_MAIL_FROM(client_sock, client_request)
                    if val == None:
                        pass 
                    else:
                        mail = True # CONTROL FLOW GOES TO WHILE MAIL()
                        mail_obj = val
                        break 

                elif check_client_prefix('AUTH', client_request):
                    auth = parse_AUTH(client_sock, client_request)

                else:
                    for arg in valid_args:
                        if check_client_prefix(arg, client_request):
                            request_builder(client_sock, "503 Bad sequence of commands")
                            break 
                    else:
                        request_builder(client_sock, "501 Syntax error, command unrecognized")

            
            while ehlo and mail:  

                while mail_obj.recpt == None:

                    client_request = get_client_request(client_sock)

                    if check_client_prefix("RCPT", client_request):
                        if parse_RCPT(client_sock, client_request):
                            rcpt = True 

                    elif check_client_prefix('EHLO', client_request):
                        if not parse_EHLO(client_sock, client_request):
                            ehlo = False 

                    elif check_client_prefix('QUIT', client_request):
                        parse_QUIT(client_sock, client_request)
                    
                    elif check_client_prefix('RSET', client_request):
                        if parse_RSET(client_sock, client_request):
                            ehlo = False 

                    else:
                        for arg in valid_args:
                            if check_client_prefix(arg, client_request):
                                request_builder(client_sock, "503 Bad sequence of commands")
                                break 
                        else:
                            request_builder(client_sock, "501 Syntax error, command unrecognized")



                

                



            






        


            

        
            


            

       

        

        

    
        
        


        

            
        


        





    


if __name__ == '__main__':
    main()