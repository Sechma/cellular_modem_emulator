#!/usr/bin/env python3

from context import * 

class E_Modem:
    """!
        E_Modem base class
        Defines variables which are represent values after restart of reall modem.

    
    """

    # Base imei code 
    imei = 674820345123456

    # Current setings of several AT commands parametrs
    conf_v = {  "&C":1, "&W":0, "E":0, "Q":0, "V":0,  
        "&F":0,"&D":1, "X":4,  "Z":0, "S0":0, "S0":0,
        "S3":13, "S4":10, "S6": 2,"S5":8, "S7":0, "S8":2, "S10":15
    }
    # Current echo mode is off
    echo_mode = False
    # Current command line termination character
    cmd_term_char = '\n'      #CR in default

    # Current response formating character
    cmd_response_char = '\r' # LF in default

    # Current command line editing character
    cmd_edit_char = '\x08'      # Backspace in default ('\X08')

    at_v = 1

    #TCP IP STACK
    context_list = []
    timeout = 1 # 1-655535 (s)
    socket_state = 0 # 0 or 1 (initial, opening)
    server_id = '""'
    at_port = "usbmodem" #TODO i dont know is right..  "usbmodem", "usbat", "uart1"
    send_len = 0
    remote_ip = '""'
    total_send_length = 0 #[byte]
    acked_bytes = 0 # [byte]

    total_receive_length = 0 #[byte]
    have_read_length = 0 #[byte]
    unread_length = 0 #[byte]
    hex_string = "" # max is 512bytes

    #not all

    ERROR_CODES = {0:"Operation successful", 550: "Unkown error", 551: "Operation blocked", 552: "Invalid parametres",
     553: "Memory not enough", 554: "Create socked failed", 555:"Operation not supported", 556:"Socket bind failed", 
    557: "Socket listen failed", 558: "Socket write failed", 559: "Socket read failed", 560: "Socket accept failed",
    561: "Open PDP context failed", 562:"Close PDP context failed", 563:"Socket identity has been used", 564: "DNS busy"}

    def __init__(self, name , company, revision):
        """! E_Modem class initializer

            @param name: The name of modem
            @param company: The company which made modem
            @param revision: The last revision of modem

        """
        self.name = name #"BG96"
        self.company = company #"Quectel"
        self.revision = revision #"BG96MAR01A01M1G" 
        self.pin = ""

        #create 16 contexts

        for i in range(1,17):
            self.context_list.append(E_Context(i))
           

    def serial_output(func):
        """! Decorator for prepare of serial output
            @func is function which are be used for serial output
        """
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            if(args[0].at_v):
                # Example:
                # output = '\r\n' + output + '\r\n'
                output = args[0].cmd_response_char + args[0].cmd_term_char + output + args[0].cmd_response_char + args[0].cmd_term_char

            else:
                # Example:
                # output = output + '\r\n'
                 output = output + args[0].cmd_response_char + args[0].cmd_term_char
                
            return output
        return wrapper


    @serial_output
    def __str__(self):
        """! Retrieves information about modem info, decorated by serial_output
            @return Information about modem (name,company,revision)
        """
        x = "{}\n{}\nRevision:{}\n".format(self.name, self.company, self.revision )
        return(x)

    def get_name(self):
        """! @return name of modem
        """
        return self.name

    def get_company(self):
        """! @return name of company """
        return self.company

    def revision(self):
        """! @return revision of modem """
        return self.revision

    def set_pin(self,pin):
        """! setter of pin of modem """
        self.pin = pin

    def set_revision(self,revision):
        """! setter of revision"""
        self.revision = revision

    def set_imei(self,imei):
        """! setter of IMEI code """
        self.imei = imei

    def get_imei(self):
        """! @return IMEI code """
        return(self.imei)
    
    def set_default(self):
        """! setter of factory current setttings
        """
        self.pin = ""
        self.get_imei = 674820345123456
        self.revision = "BG96MAR01A01M1G"

    def get_current_config(self):
        """! @return current configs (one on the line)
        """    
        for key in self.conf_v:
            output = key + ':' + self.conf_v[key] + '\n'
        return output

    def set_change_echo_mode(self):
        """!
        """
        self.echo_mode = not self.echo_mode
        
    def get_term_char(self):
        return(self.cmd_term_char)

    def set_term_char(self,n):
        self.cmd_term_char = chr(n)

    def get_response_char(self):
        return self.cmd_response_char
    
    def set_response_char(self,n):
        self.cmd_response_char = chr(n)

    def get_edit_char(self):
        return self.cmd_edit_char
    
    def set_edit_char(self,n):
        self.cmd_edit_char = chr(n)

    def get_context_type_by_id(self,n):
        return self.context_list[n-1].context_type
    
    def get_context_username_by_id(self,n):
        
        return self.context_list[n-1].username

    def get_context_password_by_id(self,n):
        return self.context_list[n-1].password

    def get_context_apn_by_id(self,n):
        return self.context_list[n-1].apn

    def get_context_auth_by_id(self,n):
        return self.context_list[n-1].authentication

    def set_context_type_by_id(self,id_c,context):
        self.context_list[id_c-1].context_type = str(context)
    
    def set_context_username_by_id(self,id_c,name):
        self.context_list[id_c-1].username = str(name)

    def set_context_password_by_id(self,id_c,passw):
        self.context_list[id_c-1].password = passw

    def set_context_apn_by_id(self,id_c,apn):
        self.context_list[id_c-1].apn = apn

    def set_context_auth_by_id(self,id_c,auth):
        self.context_list[id_c-1].authentication = auth

    def set_activate_context_by_id(self,id_c):
        self.context_list[id_c-1].activate()
        
    def get_activated_context(self):
        #1,<context_state>,<context_type>[,<IP_address>]
        l = []
        for val in self.context_list:
            if(val.is_activate() == 1):
                s = str(val.context_id)+','+ str(val.context_state)+',' + str(val.ipv4) 
                if(s != None):
                    l.append(s)
        return l
             
    def set_deactivated_context_by_id(self,context_id):
        self.context_list[context_id-1].deactivate()