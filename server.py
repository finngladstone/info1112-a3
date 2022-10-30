import ipaddress
import os
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = ''
PERSONAL_SECRET = ''

def flush_print(x):
    print(x, flush=True)

class Custom_dict(dict):
    pass 

class Email():
    pass 

def config_parser():
    pass 

def email_writer():
    pass 


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
    pass 




def main():
    # TODO
    pass


if __name__ == '__main__':
    main()