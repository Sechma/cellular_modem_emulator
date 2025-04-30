#!/usr/bin/env python3

from at_cmd import E_AT_CMD
from modem import *
from context import *

class E_AT_TCP_CMD(E_AT_CMD):
    def at_qicsgp_test(cls):
        s = b'+QICSGP:\r\n(1-16),(1,2),<APN>,<username>,<password>,(0-3)'
        return (s,True)
        
    def at_qicsgp(cls,contextid_and_others):
        contextid_and_others = contextid_and_others[0].split(",")
        if(len(contextid_and_others) == 1):

            if(int(contextid_and_others[0]) > 0 and int(contextid_and_others[0]) < 17):
                i = int(contextid_and_others[0])
                
                typ = E_AT_CMD.m_bg96.get_context_type_by_id(i)
                apn = E_AT_CMD.m_bg96.get_context_apn_by_id(i)
                username = E_AT_CMD.m_bg96.get_context_username_by_id(i)
                passw = E_AT_CMD.m_bg96.get_context_password_by_id(i)
                aut = E_AT_CMD.m_bg96.get_context_auth_by_id(i)

                s = '+QICSGP:\r\n'+str(typ)+','+apn+','+username+','+passw+','+str(aut)
                return s,True
            else:
                return "",False
        else:
            id_c = int(contextid_and_others[0])
            for idx, val in enumerate(contextid_and_others[1:]):
                if not( val == "" or val == ''):
                    if(idx == 0): #context_type
                        E_AT_CMD.m_bg96.set_context_type_by_id(id_c,val)
                    elif(idx == 1): #apn
                         E_AT_CMD.m_bg96.set_context_apn_by_id(id_c,val)
                    elif(idx == 2): #username
                        E_AT_CMD.m_bg96.set_context_username_by_id(id_c,val)
                    elif(idx == 3): #passwrod
                        E_AT_CMD.m_bg96.set_context_password_by_id(id_c,val)
                    else: #auth
                        if(idx >= 5):
                            return("", False)
                        E_AT_CMD.m_bg96.set_context_auth_by_id(id_c,val)

            return "",True

            
    def at_qiact_test(cls): #TODO
        return '+QIACT: (1-16)\r\n', True
    
    def at_qiact_read(cls):
        n = E_AT_CMD.m_bg96.get_activated_context()
        s = ""
        for i in n:
            s += "+QIACT:\r\n" + i + "\r\n"
        return s,True

    def at_qiact(cls,context_id):
        try:
            E_AT_CMD.m_bg96.set_activate_context_by_id(int(context_id[0]))
        except:
            pass
            
        return "",True
    

    def at_qideact_test(cls): 
        return '+QIDEACT: (1-16)\r\n', True

    def at_qideact(cls,context_id):
        E_AT_CMD.m_bg96.set_deactivated_context_by_id(int(context_id[0]))
        return "",True

    def at_qiopen_test(cls):
        ("+QIOPEN: (1-16),(0-11),'TCP/UDP/TCP LISTENER/UDPSERVICE','<IP_address>/<domain_name>',<remote_port>,<local_port>,(0-2)", True)
    def at_qiopen_write(cls,params):
        pass
    def at_qiclose_test(cls):
        pass
    def at_qiclose_write(cls):
        pass
    def at_qistate_test(cls):
        pass
    def at_qistate(cls):
        pass
    def at_qistate_read(cls):
        pass
    def at_qisend_test(cls):
        pass
    def at_qisend_write(cls,paramas):
        pass
    def at_qird_test(cls):
        pass
    def at_qird_write(cls,paramas):
        pass
    def at_qisendex_test(cls):
        return (b'+QISENDEX: (0-11),<hex_string>',True)
    def at_qisendex(cls,params):
        if(len(params) <= 0 ):
            return(b'SEND OK',True)
        else:
            return(b'SEND FAIL',True)

    def at_qping_test(cls):
        return(b'+QPING: (1-16),<host>,(1-255),(1-10)',True)

    def at_qping(cls):
        pass
        #TODO

    def at_qntp_test(cls):
        pass
    def at_qntp_read(cls):
        pass
    def at_qntp_write(cls):
        pass
    def at_qidnscfg_test(cls):
        pass
    def at_qidnscfg_write(cls,params):
        pass
    def at_qidnsgip_test(cls):
        pass
    def at_qidnsgip_write(cls,params):
        pass
    def at_qicfg_test(cls):
        pass
    def at_qicfg_write(cls,params):
        pass
    def at_qisde_test(cls):
        pass
    def at_qisde_read(cls):
        pass
    def at_qifeterror_test(cls):
        pass
    def at_qifeterror(cls):
        pass
    def at_qiurc(cls):
        pass

    def at_qpowd(cls,params):
        return("",True)
    def at_qpowd_test(cls):
        return("+QPOWD: (0,1)", True)
