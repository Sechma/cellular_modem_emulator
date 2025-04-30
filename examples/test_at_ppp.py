#!/usr/bin/env python3

import sys
from scapy.all import *
sys.path.insert(1, '../src')
from ppp import *
def test(cmd):
    if(cmd == 'AT\r'):
        print("AT")
        print("ERROR")
        print(10)
    elif(cmd == 'AT&W\r'):
        print("ERROR")
        print(4)
    elif(cmd == 'ATE0\r' ):
        print("ERROR")
        print(7)
  
    elif(cmd.startswith('AT') == False): #PPP byte stream in str
        name_file = cmd
        try:
            f = open(name_file,'rb+')
        except:
            return
        data = f.read()
        f.seek(0)
        f.truncate()
        
        p = E_PPP(data)
        p.hdlc_to_ppp()
       
        if(p.packet[PPP].proto == 0xc021): #LCP
            p.packet[PPP].code = 12 #Without means

        p.ppp_to_hdlc()
        f.write(p.packet)
        f.close()

        print(3)
    else:
        print("")

if __name__ == '__main__':
    cmd = sys.argv[1]
    test(cmd)