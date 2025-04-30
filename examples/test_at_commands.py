#!/usr/bin/env python3

import sys
import time

def test(cmd):
    if(cmd == 'AT\r'):
        print("AT")
        print("ERROR")
        print(3)
    elif(cmd == 'AT&W\r'):
        print("ERROR")
        print(2)
    elif(cmd == 'ATE0\r' ):
        print("ERROR")
        print(5)
    elif(cmd == 'AT+CGMM\r'):
        print("BG96")
        print("ERROR")
        print(2)
    else:
        print("")

if __name__ == '__main__':
    cmd = sys.argv[1]
    test(cmd)
    