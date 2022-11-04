import os
import socket
import sys

def flush_builder(x):
    print(x, flush=True)

class CustomDict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


class Eavesdropper():
    pass 

def main():
    # TODO
    pass


if __name__ == '__main__':
    main()
