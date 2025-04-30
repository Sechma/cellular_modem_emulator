#!/usr/bin/env python3

import re


"""
    CHEAT SHEET
    ?= ...  test
    &,+ ... _
    ? ...   read
"""
class E_Parser():
    """
        The E_Parser is class which are parse incoming at commands
        because singles at commands will be called like methods.
        
    """
    parse_cmd = ""
    cmd_arguments = []
    tcp_cmd = False

    def __init__(self,cmd):
        self.parse_cmd = cmd
        self.handler_cmd()

    def handler_cmd(self):
        """
            Parsing of incoming at commands that are in byte format.
            Also at commands can have arguments so also parse them.
        """
        if(self.is_at_cmd()):
            self.bytes_to_pythonic()
            self.change_to_call()
            if(type(self.cmd_arguments) == list):
                if( len(self.cmd_arguments) == 2 and self.cmd_arguments[1] == ''):
                    self.cmd_arguments = str(self.cmd_arguments[0])


            if(re.match('^at_q.*',self.parse_cmd)): 
                self.tcp_cmd = True
            else:
                self.tcp_cmd = False
        
    def change_to_test(self):
        x = re.search("^at.+\=\?$", self.parse_cmd)
        if(x):
            self.parse_cmd = self.parse_cmd.replace("=?","_test")
            return True
        else:
            return False

    def change_to_read(self):
        y = re.search("^at.+\?$", self.parse_cmd)
        if(y):
            self.parse_cmd = self.parse_cmd.replace("?","_read")
            return True
        else:
            return False

    def short_at_cmd(self): #FOR ATV1, ATD99**#...etc
        if(self.parse_cmd == "atd*99***1#"):
          self.parse_cmd = "atd"
          self.cmd_arguments = "*99***1#"
          
        else:
            z = re.split('(\d+)',self.parse_cmd)
            self.parse_cmd = z[0]
            self.cmd_arguments = z[1:]
           
    def change_to_call(self):
        self.parse_cmd = self.parse_cmd.replace("+","_").replace("&","_")
        self.parse_cmd = self.parse_cmd.lower()
       
        if(self.parse_cmd == 'a/'):
            self.parse_cmd = 'a' 
        if not(self.change_to_test()):
            if not (self.change_to_read()):
                self.parse_cmd, self.cmd_arguments = self.parse_cmd.split('=')[0],self.parse_cmd.split('=')[1:]
                if re.search('\d+', self.parse_cmd):
                    self.short_at_cmd()
    
    def is_at_cmd(self):
        if(self.parse_cmd == b'\xf0'): #init from Arduino IDE
            self.parse_cmd = ""
            return False
        else:
            return True # it can be AT command
    
    def bytes_to_pythonic(self):
        self.parse_cmd = self.parse_cmd.hex() + '  ' + ''.join([chr(b) if b>32 and b<128 else '' for b in self.parse_cmd])
        self.parse_cmd, self.cmd_arguments = (self.parse_cmd.split(" "))[2],(self.parse_cmd.split(" "))[3:]
       
           
    def bytes_str_to_pythonic(cmd):
        #cmd = cmd.encode()
        cmd = cmd.hex() + '  ' + ''.join([chr(b) if b>32 and b<128 else '' for b in cmd])
        cmd, arguments = (cmd.split(" "))[2],(cmd.split(" "))[3:]
        return cmd,arguments