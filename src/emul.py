#!/usr/bin/env python3


import click
import os
# imports another modules
from interface import *
from parser import *

# Parsing of commands by click
@click.command()
 
@click.option("--modem","-m",help="Name of modem")
@click.option("--file","-f", help="Source to file")
@click.option("--baudrate","-brate", help = "Set baud rate, default: 115200",
 default = 115200, type=click.Choice([9600,19200,38400,57600,115200,230400,4600800]))

@click.option("--bytesize","-bsize", help = "Set bytesize , default: 8 ",
 type=click.Choice([5,6,7,8]), default = 8)

@click.option("--parity","-p", help = "Set parity, default: N", default = 'N',
type=click.Choice(['N','E','O','S','M']))

@click.option("--stopbits","-sbits", help = "Set stop bits , default : 1", type=click.Choice([1, 1.5, 2]),default = 1 )
@click.option("--rtscts", help = " Enable flow control, default: off", type = bool, default = False)
@click.option("--xonxoff", help = "Enabled software flow control, default: off", type = bool, default = False)

@click.option("--serialport", help = "Serial port, default: dev/ttyUSB1 (Linux)", default = '/dev/ttyUSB0')
#Testing 
@click.option("--repeat","-r", help = "If u input script with set AT command on error or timeout it will be in circle",
 type = bool, default = False)

def main(modem,file,baudrate,bytesize,parity,stopbits,rtscts,xonxoff, serialport,repeat):
    '''
        Available modems: BG96
        Version: 1.00
    '''
    """
        main: emul.py
        type modem: string
        param modem: Name of modem (BG96..)
        type baudrate: int
        param baudrate: Set of baudrate for serial com.
        type bytesize: int
        param bytesite: Set of bytesite for serial com.
        type parity: char
        param parity: Set of parity in serial com.
        type stopbits: float
        param stopbits: Set of stopbits in serial com.
        type rtscts: bool
        param rtscts: Set of flow control in serial com.
        type xonxoff: bool
        param xonxoff: Set of software flow control in serial com.
        type serialport: string
        param serialport: Set of serial port for serial com. 


    """
    
    #Start of interface, implicit waiting for at commands which are comming on serial link
    intf = E_Interface(["BG96"],modem,file,baudrate,bytesize,parity,stopbits,rtscts,xonxoff,serialport,repeat)
   
    
if __name__ == "__main__":
    main()