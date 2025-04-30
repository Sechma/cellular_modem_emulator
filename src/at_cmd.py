#!/usr/bin/env python3

#import at_tcp_cmd
#import parser
import serial
from modem import *


class E_AT_CMD:
    """
    The class E_AT_CMD represent all basics AT Commands for modem BG96
    """
    m_bg96 = E_Modem("BG96","Quectel","BG96MAR01A01M1G")
    """
    Create object which is represent E_Modem(name,company,serial number)
    """ 

    f = ""
    previous_arguments = ""
    """
    Temporary variables for previous function and theirs arguments
    """

    def save(func):
        """
        Decorator of saving previous AT command.
        """
        def wrapper(*args, **kwargs):       
            E_AT_CMD.f = str(func.__name__)
            E_AT_CMD.previous_arguments = (str(args)) #TODO not tested
            return(func(*args,**kwargs))
        return wrapper
    @save
    def at(cls):
        return "AT",True

    @save
    def ati(cls):
        """
            Represent AT command: ATI
        """
        return(E_AT_CMD.m_bg96.__str__(), True)

    @save
    def at_gmi(cls):
        """
            Represent AT command: AT+GMI
        """ 
        return(E_AT_CMD.m_bg96.get_company(),True)
    
    @save
    def at_gmi_test(cls):
        """
            Represent AT command: AT+GMI=?
        """
        return("",True)
    
    @save
    def at_gmm(cls):           
        """
            Represent AT command AT+GMM
        """
        return(E_AT_CMD.m_bg96.get_name(), True)
    
    @save
    def at_gm_test(cls):
        """
            Represent AT command AT+GMM=?
        """
        return("",True)
    
    @save
    def at_gmr(cls):
        """
            Represent AT command AT+GMR
        """
        return(E_AT_CMD.m_bg96.get_revision(), True)
    
    @save
    def at_gmr_test(cls):      #AT+GMR=?
        """
            Represent AT command AT+GMR=?
        """
        return("",True)
    
    @save
    def at_cgmi(cls):          
        """
            Represent AT command AT+CGMI
        """
        return(E_AT_CMD.m_bg96.get_company(),True)
    
    @save
    def at_cgmi_test(cls):
        """
            Represent AT command AT+CGMI=?
        """
        return("",True)
    
    @save
    def at_cgmm(cls):
        """
            Represent AT command AT+CGMM
        """
        return(E_AT_CMD.m_bg96.get_name(),True)
    
    @save
    def at_cgmm_test(cls):
        """
            Represent AT command AT+CGMI=?
        """ 
        return("",True) 
    
    @save
    def at_cgmr(cls):         
        """
            Represent AT command AT+CGMR
        """
        return(E_AT_CMD.m_bg96.revision(), True)
    
    @save
    def at_cgmr_test(cls):     #AT+CGMR=?
        """
            Represent AT command AT+CGMR=?
        """
        return("",True)

    @save
    def at_gsn(cls):
        """
            Represent AT command AT+GSN
        """           
        return(E_AT_CMD.m_bg96.get_imei(), True)

    @save
    def at_gsn_test(cls):      #AT+GSN=?
        """
            Represent AT command AT+GSN=?
        """
        return("",True)
        
    @save
    def at_cgsn(cls):
        """
            Represent AT command AT+CGSN
        """
        
        return(str(E_AT_CMD.m_bg96.get_imei())+"\r\n", True)
     
    @save
    def at_cgsn_test(cls):
        """
            Represent AT command AT+CGSN?
        """
        return("", True)

    @save
    def at_f(cls,value):
        """
            Represent AT command AT&F
        """  
        if(int(value) != 0):    
            return("", False)
        else:
            E_AT_CMD.m_bg96.set_default
            return("", True)
    
    @save
    def at_v(cls):
        """
            Represent AT command AT&V
        """        
        return(E_AT_CMD.m_bg96.get_current_config(), True)
    @save
    def at_w(cls):
        return("", True)

    @save
    def atz(cls,value):
        """
            Represent AT command ATZ
        """
        return("", False)

    @save
    def atq(cls,n):            #ATQ -  n = 0 OK, n = 1 (none) #TODO
        return ("", False)

    @save
    def atv(cls,value):
        
        """
            Represent AT command ATV
        """
       
        x = E_AT_CMD.m_bg96.get_atv() #TODO get atv doesnt exist
       
        if (int(value) == x):
            return("", True)
        elif(int(value) == 1 or int(value) == 0):
            E_AT_CMD.m_bg96.change_atv() #TODO change_atv doesn exist
            return("", True)
        else:
            return("",False)
    @save
    def ate(cls,value):
        """
            Represent AT command ATE
        """
        if( int(value) == 0 or int(value) == 1):
            E_AT_CMD.m_bg96.set_change_echo_mode()
            return("", True)
        else:
            return("",False)

    def a(cls):
        """
            Represent AT command \A
            Specific command for calling previous function
            which is load in variable f by decorator save
        """
        return(getattr(E_AT_CMD,E_AT_CMD.f)("cls"))
       
    @save
    def ats3_read(cls):
        """
            Represent AT command ATS3?
        """
        return E_AT_CMD.m_bg96.get_term_char(),True

    @save
    def ats3(cls,n):
        """
            Represent AT command ATS3
        """
        if(cls.at_formal_char(n)):
            return E_AT_CMD.m_bg96.set_term_char(n), True
        else:
            return ("", False)

    @save
    def ats4_read(cls):
        """
            Represent AT command ATS4?
        """
        return E_AT_CMD.m_bg96.get_response_char(), True

    @save
    def ats4(cls,n):
        """
            Represent AT command ATS4
        """
        if(cls.at_formal_char(n)):
            return E_AT_CMD.m_bg96.set_response_char(n),True
        else:
            return "", False
    @save
    def ats5_read(cls):
        """
            Represent AT command ATS5?
        """
        return E_AT_CMD.m_bg96.get_edit_char(), True

    @save
    def ats5(cls,n):
        """
            Represent AT command ATS5
        """
        if(cls.at_formal_char(n)):
            return E_AT_CMD.m_bg96.get_response_char(n),True
        else:
            return "",False

    @save
    def at_cimi(cls):
        return "460023210226023\r\n", True

    @save
    def at_cimi_test(cls):
        return "",True

    @save
    def at_cops_read(cls):
        return "+COPS: 0,0,“CHN-UNICOM”,0\r\n", True
    @save
    def at_cops_test(cls):
        return "",True
    @save
    def at_ifc(cls,args):
        return ("", True)
    @save
    def at_csq(cls):
        return ("+CSQ: 28,99\r\n"),True
    @save
    def at_cbc(cls):
        return "+CBC: 1,90,330\r\n", True

    @save
    def at_cfun_test(cls):    
        return (b'+CFUN: 0,0', True)
    @save
    def ath(cls):
        return("",True)
    

    @save
    def at_cgreg_read(cls):
        return "+CGREG: 1,0\r\n", True
        # n = 1 ...Enable network registration unsolicited result code
    @save
    def at_cgreg_test(cls):
        return "+CGREG: 1\r\n", True

      
    @save
    def at_cgreg(cls,n):
        """
            if( n == 1): #only n = 1 is enable
                return "", True
            else:
                return "", False
        """

    @save 
    def at_cgdcont_test(cls):
        pass

    @save 
    def at_cgdcont_read(cls):
        pass
    
    @save
    def at_cgdcont(cls,args):
        return "",True

    @save
    def atd(cls,args):
        if( args != '*99***1#'):
            return "",False
        
        return "CONNECT \r\n",True


    def at_formal_char(cls,n):
        if(chr(n) >=  0 and chr(n) <= 127):
            return True
        else:
            return False        
    #*********************************





