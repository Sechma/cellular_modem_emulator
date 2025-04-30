#!/usr/bin/env python3

import ipaddress

class E_Context:
    context_id = 0
    context_type = 1 # 1 is ipv4, 2 is ipv6
    context_state = 0 # 0 deactivated, 1 is activated
    domain_name = 'localhost'
    ain_name = '""'
    remote_port = 0 # 0-65535
    local_port = 0 # 0-65535
    access_mode = 0 # 0 buffer_access_mode, 1 direct push mode 2 transparent access mode
    apn = '""'
    username = '""'
    password = '""'
    authentication = 0 # 0 is None, 1 is PAP, 2 CHAP, 3 both(PAP/CHAP)
    activate = False
    ipv4 = ipaddress.ip_address('127.0.0.1')
    ipv6 = ipaddress.ip_address('::1')

    service_type = "TCP" # TCP(client), UDP(client), TCP LISTENER(server), TCP INCOMING(start like server)
                         # UDP SERVICE Start UDP service
    connect_id = 0 # Connect id 0-11
    err = 0

    def __init__(self,c_id):
        """
        Constructor for Context
        @param is number which represent context id <1,16>
        """
        self.context_id = c_id # range is 1-16
       
    def activate(self):
        """
        Set context to state activate (1)
        """
        self.context_state = 1
    def deactivate(self):
        """
        Set context to state deactivate (0)
        """
        self.context_state = 0
 
    def is_activate(self):
        """
        Returns context state of one context.
        """
        return self.context_state