#!/usr/bin/env python3

import sys
from scapy.all import *
sys.path.insert(1, '../src')
from ppp import *


def test(cmd):
    
    if(cmd.startswith('AT') == False): #PPP byte stream in str
        name_file = cmd
        f = open(name_file,'rb+')
        data = f.read()
        f.seek(0)
        f.truncate()
        
        p = E_PPP(data)
        p.hdlc_to_ppp()
       
        if(p.packet[PPP].proto == 0xc021): #LCP
            p.packet[PPP].code = 11 #Discard packet

        p.ppp_to_hdlc()
        f.write(p.packet)
        f.close()

        print(3)
    else:
        print("")
if __name__ == '__main__':
    cmd = sys.argv[1]
    
    test(cmd)
    