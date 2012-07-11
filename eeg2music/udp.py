import socket


def send(port, message):

	UDP_IP = "127.0.0.1"
        UDP_PORT = port
        MESSAGE = message                
                
 
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "message:", MESSAGE

        sock = socket.socket( socket.AF_INET, # Internet
                        socket.SOCK_DGRAM ) # UDP
        sock.sendto( MESSAGE, (UDP_IP, UDP_PORT) )
