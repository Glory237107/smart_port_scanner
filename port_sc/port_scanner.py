import socket
#define a function to scan the ports
def scan_ports(target_ip, ports):
    open_ports = [] #Tuple to store open ports
    for port in ports:
        s = socket.socket()  #Generating a socket object
        s.settimeout(1)  #stting a 1 second time lapse before moving to the next step
        try:
           s.connect((target_ip, port))  #connecting toa port using the socket object
           open_ports.append(port)  #if the port is open, storing it the tuple
        except:
            pass  #it ignores the closed ports
        s.close()  #it close the socket
    return open_ports     
