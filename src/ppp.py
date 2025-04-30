from re import X
from tabnanny import verbose
import crcmod
from binascii import unhexlify
import threading
from scapy.all import *
from itertools import cycle
from random import randint

class E_PPP:
    """
         the E_PPP is class which parse PPP protocol and also make pakets for incoming queries.
         Under PPP we met protolcs like LCP or IPCP.
    """
    _LCP = 0xc021 # LCP flag
    _IPCP = 0x8021 #IPCP flag
    _UDP = 17 # number of protocol in ip
    _TCP = 6 
    _ICMP = 1

    _IPP_head =  [0xff,0x03]
    _IPCP_flag = [0x80,0x21]
    _LCP_flag =  [0xc0,0x21]
    
    def __init__(self,packet):
        self.packet = packet #incoming packet like HDLC

    def hdlc_to_ppp(self):
        """
            Removing of flags and FCS and parse packet to scapy PPP format.
        """
        self.packet = self.packet[1:]  # remove flag,add,control
        self.packet = self.packet[:-1] # remove flag from butt
        self.packet = self.packet[:-2] # remove FCS
        self.remove_stuffin() # function for removing of escaping
        self.packet = scapy.layers.ppp.PPP(self.packet) 
       
    def ppp_to_hdlc(self):
        """
            Method pack PPP packet to HDLC frame
        """
        self.packet = bytes(self.packet)
        fcs = self.fcs()
        self.packet += fcs
        self.add_stuffin() # adding of escape sequence
        self.packet = b'\x7e' + self.packet
        self.packet += b'\x7e'


    def ppp_code(self): #code of LCP/IPCP packet
        return self.packet[PPP].code
    
    def ppp_proto(self): # About LCP or IPCP
        return self.packet[PPP].proto

    def ppp_id(self): # ID of packet 
        return self.packet[PPP].id

    def ppp_packet(self):
        return self.packet

    def lcp_answer(self):
        """
            LCP answers and sending reqistration querry
        """
        packet_buffer = []
      
        if(self.ppp_code() == 1 and self.ppp_id() == 1):
              
            self.set_ack_ppp() # SET packet on ack
            self.ppp_to_hdlc() # Transfrom packet to HDLC
            packet_buffer.append(self.packet) # append to packet list

            self.hdlc_to_ppp() 
            self.set_first_req_ppp() # send request for start my dialog
            self.ppp_to_hdlc() # Transform to HDLC
            packet_buffer.append(self.packet) # append to packet list

            return packet_buffer
        else:
            self.set_ack_ppp() # send ack LCP

    def ipcp_answer(self):
        packet_buffer = []
    
        if(self.ppp_code() == 1 ): # esp32 start dialog 
            if(self.ppp_id() == 0x01):
                self.set_req_first_ipcp() # send req with id 0
                self.ppp_to_hdlc() 
                packet_buffer.append(self.packet) 

                self.hdlc_to_ppp()
                self.set_first_nack_ipcp() # send nack on esp settings of ip's
                self.ppp_to_hdlc()
                
                packet_buffer.append(self.packet)
                return packet_buffer
            elif( self.ppp_id() == 0x02 ): # we continuin in dialog
                self.set_req_second_ipcp() 
                self.ppp_to_hdlc()
                packet_buffer.append(self.packet)
                return packet_buffer

            elif(self.ppp_id() == 3):
                self.set_ack_on_dns() # we expect request on out ip's
                self.ppp_to_hdlc() 
                packet_buffer.append(self.packet)
                return packet_buffer

        elif(self.ppp_code() == 2): # dialog
            if(self.ppp_id() == 1):
                self.set_nack_dns_ipcp()
                self.ppp_to_hdlc()
                packet_buffer.append(self.packet)
                return packet_buffer
    
    def send_answer(self): # W
        """
            Send answer or anwser's on incoming packet 
        """
        try:
            if(self.packet.decode().startswith('AT')):
                return "AT"
        except:
            pass
        
        self.hdlc_to_ppp()
        self.packet.show()
        if(bytes(self.packet) == b'!'): # ***
            return "AT"

        if(self.ppp_proto() == self._LCP):
            return self.lcp_answer()

        elif(self.ppp_proto() == self._IPCP):
            return self.ipcp_answer()
 
        
        elif(self.ppp_proto() == 33): #Ipv4 
            x =(bytearray(bytes(self.packet)))
            answer = ""
            if(self.packet[IP].proto == self._UDP):#udp
                
                dns_req = IP(x[1:21]) / UDP(x[21:])
                answer = sr1(dns_req, verbose=0)
             
                
            elif(self.packet[IP].proto == self._TCP): #tcp
                packet = IP(x[1:21]) / TCP(x[21:])
                answer = ""
                if(packet[TCP].flags == 'A'):
                    send(packet, verbose = 0)
                    answer = ""
                elif(packet[TCP].flags == 'PA'):
                    send(packet, verbose = 0)
                    capture = sniff(filter = "tcp",count = 2)
                    for i in range(len(capture)):
                        if(capture[i].getlayer(IP).src == '137.135.83.217' and capture[i].getlayer(TCP).flags == 'PA' ):
                            answer = capture[i].getlayer(IP) / capture[i].getlayer(TCP)
                       
                else:
                    answer = sr1(packet, verbose = 0)
             
                if(str(type(answer)) == "<class 'NoneType'>" ):
                    pass
               
            x = []
            if(answer != ""):
                self.packet = b'!' + bytes(answer) 
                self.ppp_to_hdlc()
                x.append(self.packet)
            return x
        else:
            return  


    def set_ack_on_dns(self):
        self.packet[PPP].code = 2 #ack

    """
    _IPP_head = [0xff,0x03,0x80,0x021]
    _IPCP_flag = [0x80,0x21]
    _LCP_flag = [0xc0,0x21]
    """
    def set_req_second_ipcp(self):
        x = self._IPP_head + self._IPCP_flag
        x = x + [0x01,0x01,0x00,0x04]# request, id, len
        #x = [0xff,0x03,    0x80,0x21,  0x01,0x01,0x00,0x04]
        
        x = scapy.layers.ppp.PPP(bytes(x))
        self.packet = x

    def set_req_first_ipcp(self):
        x = self._IPP_head + self._IPCP_flag
        x = x + [0x01,0x00,0x00,0x04] # request, id, len
        #x = [0xff,0x03,0x80,0x21,0x01,0x00,0x00,0x04]
        x = scapy.layers.ppp.PPP(bytes(x))
        self.packet = x

    def set_nack_dns_ipcp(self): # ip na koleji:  0x93,0xe5,0xc1,0x86   0x7f,0x00,0x00,0x01
        x = self._IPP_head + self._IPCP_flag
        x = x + [0x03,0x02,0x00,0x16,0x03,0x06] # nak, id, len, type: IP, len
        #x = [0xff,0x03, 0x80,0x21 ,0x03,0x02,0x00,0x16,0x03,0x06]
        x = x + self.get_ip()
        x = x + [0x81,0x06, 0x08,0x08,0x08,0x08] # type: prim. dns, len, ipv4 of dns
        x = x + [0x83,0x06, 0x08,0x08,0x04,0x04] # type: second dns, len, ipv4 of dns

        x = scapy.layers.ppp.PPP(bytes(x))
        self.packet = x

    def set_req_dns_ipcp(self):
        x = self._IPP_head + self._IPCP_flag
        x = x + [0x01,0x03,0x00,0x16,0x03,0x06] # req, id, len, type:IP, len
        #x = [0xff,0x03,0x80,0x21,  0x01,0x03,0x00,0x16,0x03,0x06]
        x = x + self.get_ip()  #0x93,0xe5,0xc1,0x86 
        x = x + [0x81,0x06, 0x08,0x08,0x08,0x08] # type: prim. dns, len, ipv4 of dns
        x = x + [0x83,0x06, 0x08,0x08,0x04,0x04] # type: second dns, len, ipv4 of dns
        #DNS 8.8.8.8
        #IP 127.0.0.1
        #ID 0x02
        x = scapy.layers.ppp.PPP(bytes(x))
        self.packet = x

    def set_first_req_ppp(self):
        x = self._IPP_head + self._LCP_flag

        x = x + [0x01,0x00,0x00,20, # header, id, code, proto,len
                0x02,0x06,0x00,0x00,0x00,0x00,]  #async control map
        x = x + [0x05,0x06] # magic num
        
        x.append(randint(0,255))
        x.append(randint(0,255))
        x.append(randint(0,255))
        x.append(randint(0,255))
        
        x = x + [0x07,0x02,0x08,0x02] # protocol field compresion, adres control compresion

        y = scapy.layers.ppp.PPP(bytes(x))
        self.packet = y

    def set_ack_ppp(self):
        self.packet[PPP].code = 2 #ack
        
    def set_first_nack_ipcp(self):
        x = self._IPP_head + self._IPCP_flag
        x = x + [0x04,0x01,0x00,0x0a,0x02,0x06,0x00,0x2d,0x0f,0x01]
        x = scapy.layers.ppp.PPP(bytes(x))
        self.packet = x
    
    
    def fcs(self):
        """
            Made fcs in right format 
        """
        fcs = self.pppfcs16(0xffff)
        fcs = fcs ^ 0xffff
        tmp = []
        tmp.append( fcs & 0x00ff)
        tmp.append( ((fcs >> 8) & 0x00ff))
        return bytes(tmp)

    def remove_stuffin(self):
        """
            Removing of escape sequence
        """
        escaped = False
        unescapedPacket = []
        packet = bytes(self.packet)
        for ch in packet:
            if escaped:
                escaped = False
                if ch is 0x7e:
                    continue

                ch = ch ^ 0x20
            
            elif ch is 0x7d:
                escaped = True
                continue

            unescapedPacket.append(ch)

        self.packet =  bytes(unescapedPacket)
 
       
    def add_stuffin(self):
        """
            Addiction of escape sequence
        """
        framed_packet = []
        for ch in bytes(self.packet):
            if (ch) < 0x20 or ch in [0x7e, 0x7d]:
                framed_packet.append(0x7d)
                framed_packet.append(ch ^ 0x20)
            else:
                framed_packet.append(ch)

        self.packet = (bytes(framed_packet))
       
    

    def pppfcs16(self, fcs, formated=False):
        packet = bytes(self.packet)
        fcstab = [
       0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78,
        ]#lookup table 
        for ch in packet:
            fcs = (fcs >> 8) ^ fcstab[(fcs ^ ch) & 0xff] # (byte shift) xor ([xor logical and])
        
        return fcs

    def get_ip(self):
        ip = get_if_addr(conf.iface)
        ip = ip.split('.')
        new_ip_list = []
        for str_num in ip:
            new_ip_list.append((int(str_num)))
        
        return new_ip_list