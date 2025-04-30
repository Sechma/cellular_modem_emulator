#!/usr/bin/env python3

"""
Author: Marek Sechra
Date : 26.4.2020

"""

import click
import os

import serial
from ppp import E_PPP
from parser import E_Parser
from at_cmd import *
from at_tcp_cmd import *
from context import *
import time

import crcmod
from binascii import unhexlify
import threading
import asyncio
from scapy.all import *
import subprocess


class E_Interface:
    """
        Class when is set serial link for communication with embeded devices.
        There are also serial outputs and outputs for command line 
    
    """
    yes = ['yes','y', 'ye']
    no = ['no','n']
    modems = []
    ser = None
    buffer = ""
    at_cmd = ""
    at_arguments = []
    hdlc = None

    previous_cmd = {} #dicts
    previous_arguments = {} # dicts
    cmd_coun_repeat = 0
    
    previous_ppp_packets = {}

    test_cmd_out = ""
    flag_test_script = False

    def __init__(self,modems,modem,pfile,baudrate,bytesize,parity,stopbits,rtscts,xonxoff,serialport,repeat):
        self.modems.extend(modems)
        self.modem = modem
        self.file = pfile
        self.port = serialport
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.rtscts = rtscts
        self.xonxoff = xonxoff
        self.repeat = repeat
        
        if(self.modem == None):
            self.choose_modem()
        #if(self.file == None):
        self.start_emul()

    #Decorators *********************************************************
    def output_commad_cr_lf(func):
        """
            Decorator of pretty outputs of <CR><LF>
        """
        def wrapper(*args, **kwargs):
             output = func(*args, **kwargs)
             if(output != ""):
                click.secho(f"{output}", fg="white", bold=True, nl=False)
                click.secho(f"  CR+LF", fg="bright_blue", dim=True)
        return wrapper

    def output_answer_decorator(func):
        """
            Decorator for pretty output to command line
        """
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
          
            if(str(output) != "" and output != None):
                output,is_ok = output[0],output[1]

                x = (output).splitlines()
              
                for i in x:
                    if(i != ""):
                        click.secho(f"{i}", fg="yellow", bold=True, nl=False)
                        click.secho(f"  CR+LF", fg="bright_blue", dim=True)
                    else:
                        click.secho(f"")
                if(str(type(is_ok)) == "<class 'bool'>"):
                    if(is_ok):
                        click.secho(f"\nOK", fg="green", bold=True, nl=False)
                        click.secho(f"  CR+LF", fg="bright_blue", dim=True)
                    else:
                        click.secho(f"\nERROR", fg="red", bold=True, nl = False)
                        click.secho(f"  CR+LF", fg="bright_blue", dim=True)
                else:
                    click.secho(f"{is_ok}", fg="red", bold=True, nl=False)
                    click.secho(f"  CR+LF", fg="bright_blue", dim=True)

        return wrapper



    #******************************************************************

    def choose_modem(self):
        print("Available modems:")
        [print("    " + x) for x in self.modems]
        modem = click.prompt('Please enter one of the modems',type=str)
        if(modem.upper() not in self.modems):
            self.choose_modem()

    def one_at(self):
        os.system('cls||clear')
        at = click.prompt(click.style("Enter AT command",fg="yellow", bold=True))
        click.secho(f"{at}", fg="red", bold=True)
        E_Parser.handler_syntax(self,at)
    
    def start_emul(self):
        os.system('cls||clear')
        if(self.file != None):
            self.test_open_file()
      
        self.serial_config()
        self.serial_read()
    
    def test_open_file(self):
        try:
            child = subprocess.Popen(['python3',self.file,""], stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=False)
            self.flag_test_script = True
           
        except Exception as e:
            print(e)
            print("Wrong source to python script:"+self.file)

    def run_file(self,cmd):
        self.cmd_coun_repeat = 0
        child = subprocess.Popen(['python3',self.file,cmd],stdout=subprocess.PIPE)
        stdout = (child.communicate())
        if(stdout[0].decode().startswith('$')):
            pole = stdout[0].decode().split('$')
            try:
                stdout = pole[1],pole[3]
                if( pole[4].split('\n')[1].isdigit() ):
                    self.cmd_coun_repeat = int(pole[4].split('\n')[1])
            except:
                stdout = pole[1]
            return stdout

        pole = stdout[0].decode().split('\n')
       
        if(len(pole) == 2): # no arguments
            stdout = pole[0]

        elif(len(pole) == 3):
            if(pole[1].isdigit()):
                stdout = pole[0]
                self.cmd_coun_repeat = int(pole[1])
            else:    
                stdout = pole[0],pole[1]

        elif(len(pole) == 4):
           stdout = pole[0],pole[1]
           self.cmd_coun_repeat = int(pole[2])

        else:
            if(stdout[0] == b''):
               pass
            else:
                print("Wrong number of answers")
                print("Emulator expect two answers on command")
                print("If u want test special character for new line in answers")
                print("Please starts and ends  AT command $")
                print("Example:")
                print(" $\\n\\n AT \\n \\n$")
                print(" $OK$")
           
            stdout = ""
       
        return stdout

    def serial_config(self):
        """
            Settings of serial config parametrs 
        """
        try:
            self.ser = serial.Serial(self.port,self.baudrate, timeout=0.050)
            self.ser.bytesize = self.bytesize
            self.ser.parity = self.parity
            self.ser.stopbits = self.stopbits
            self.ser.rtscts = self.rtscts
            self.ser.xonxoff = self.xonxoff
            
        except Exception as e:
            print("Serial connection problem")
            print(e)

    def serial_read(self):
        """
            Procedure for serial read of at commands 
        """
        while 1 :
            try:
                while self.ser.in_waiting:
                    data_in = self.ser.readline()
                    self.serial_read_cmd(data_in)
                   
            except Exception as e:
                print(e)
                break

    def serial_read_cmd(self,data_in):
        ppp = False
     
        self.output_print(data_in)
        
        if(self.flag_test_script):
            try:
                x = self.run_file(data_in)
                if(x != ""):
                    self.test_cmd_out = x
            except Exception as e:
                print(e)
                      
        Parser = E_Parser(data_in)
        self.at_cmd, self.at_arguments, tcp = Parser.parse_cmd, Parser.cmd_arguments , Parser.tcp_cmd
                   
        if(self.at_cmd == "atd"):
            ppp = True
        if(tcp):
            self.call_at_tcp()
        else:   
            self.call_at()
        if(ppp):
            self.serial_ppp()

    @output_answer_decorator
    def call_at(self):
        """
            Calling of methods which are represent usuall at commands
        """
        if(self.at_cmd != ""):
           
            if(self.at_arguments != []):
                try:
                    data = getattr(E_AT_CMD, self.at_cmd)("E_AT_CMD",self.at_arguments)
                except:
                    print("Command not implemented in Emulator")
                    data = ["",False]
            else:
                try:
                    data = getattr(E_AT_CMD, self.at_cmd)("E_AT_CMD")
                except:
                    print("Command not implement")
                    data = ["",False]
                    

            data,succ = data[0],data[1]
            
           
            if(data.startswith("CONNECT")):
                data = "CONNECT " + str(self.ser.baudrate) + "\r\n"
                data,succ = self.test_out_parse(data,succ)
                self.serial_answer(data,succ)
                return (data,succ,"PPP")
            else:
                data,succ = self.test_out_parse(data,succ)
                self.serial_answer(data,succ)
                return (data,succ,"")


    @output_answer_decorator
    def call_at_tcp(self):
        """
            Calling of methods which are represent at commands from tcp/ip stack
        """
        if(self.at_arguments == []):
            try:
                d = getattr(E_AT_TCP_CMD,self.at_cmd)("TCP")
            except:
                print("Command not implemented in Emulator")
                d = ["",False]
        else:
            try:
                d = getattr(E_AT_TCP_CMD,self.at_cmd)("TCP",self.at_arguments)
            except:
                print("Command not implemented in Emulator")
                d = ["",False]

        data,succ = d[0],d[1]
        data,succ = self.test_out_parse(data,succ)
       
        self.serial_answer(data,succ)
       
        return(data,succ)

    def serial_answer(self,data,succ):
        """
            Serial answer on oncoming AT command
        """
        self.test_cmd_out = ""
        if(data is not None or str(data) != ""):
            data = str.encode(str(data))
            self.ser.write(data)
           
        if(str(type(succ)) == "<class 'bool'>"):
            if(succ):
                self.ser.write(b'\r\nOK\r\n') #expectd OK/ERROR 1/0
            else:
                self.ser.write(b'\r\nERROR\r\n')
        else:
            succ = succ.encode()
            self.ser.write(b'\r\n'+succ+b'\r\n')

    @output_commad_cr_lf
    def output_print(self,output):
        """
            Prepare for printing to command line
        """
        output = output.hex() + '  ' + ''.join([chr(b) if b>32 and b<128 else '' for b in output])
        output = (output.split(" "))[2]
        return output

    def serial_ppp(self):
        """
            Operates and starts PPP comunications
        """
        x = True
        click.secho(f"PPP started", fg="yellow", bold=True)
       
        while 1 :
            while self.ser.in_waiting:
                stop = False
                data = ""
                packet = self.ser.readline()


                if(self.flag_test_script):
                    try:
                        data,count = self.run_file_ppp(packet)
                    except:
                        pass
                    if(not self.repeat and data != ""):
                        if( data not in self.previous_ppp_packets):
                            self.previous_ppp_packets[data] = count
                        
                        else:
                            if(self.previous_ppp_packets[data] <= 0):
                                stop = True
                            self.previous_ppp_packets[(data)] -= 1


                p = E_PPP(packet)
                try:
                    buff = p.send_answer()
                except Exception as e:
                    print(e)
                try:
                    if(buff == "AT"):
                        self.ser.write(b'\r\nERROR\r\n')
                        return
                
                    if(buff != ""):
                        if(buff != data):
                            if(not stop):
                                buff = data
                        for i in buff:
                            self.ser.write(bytes(i))
                except Exception as e:
                    pass

    def run_file_ppp(self,packet):
        name_file = 'paket.bin'
        f = open(name_file, "wb")
        f.write(packet)
        f.close()
        child = subprocess.Popen(['python3',self.file,name_file],stdout=subprocess.PIPE)
        counter = child.communicate()

        f = open(name_file,'rb')
        data = f.read()
        f.close()
        os.remove(name_file)
       
        counter = counter[0].decode().split('\n')[0]
        return data,int(counter)

    def test_out_parse(self,data,succ):
        if(self.flag_test_script):
            if(self.test_cmd_out != ""):
                if( self.at_cmd in self.previous_cmd):
                    if(self.previous_cmd[self.at_cmd] <= 0):
                        return data,succ
                else:        
                    if(not self.repeat):
                        self.previous_cmd[self.at_cmd] = self.cmd_coun_repeat
                       
                if(type(self.test_cmd_out) == str):
                    data = ""
                    succ = self.test_cmd_out

                if(self.test_cmd_out == "ERROR"):
                    data = ""
                    succ = self.test_cmd_out

                if( str(type(self.test_cmd_out)) == "<class 'tuple'>"):
                    data = self.test_cmd_out[0]
                    succ = self.test_cmd_out[1]

                self.previous_cmd[self.at_cmd] -= 1
       
        return data,succ

    