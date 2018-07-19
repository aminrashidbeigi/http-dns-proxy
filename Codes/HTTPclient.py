import socket
from reliable import ReliableUDP

client_address = 'localhost'
client_port1 = 5000
client_port2 = 5001

client1 = (client_address, client_port1)
client2 = (client_address, client_port2)

if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(client1)
    reliable_udp = ReliableUDP(sock, "proxy", 5000, 2500)
    # request = "GET / HTTP/1.1\r\nHost: http://aut.ac.ir"
    request = "GET / HTTP/1.1\r\nHost: http://www.google.com/"
    reliable_udp.send(request)
    sock.close()

    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock1.bind(client2)
    reliable_udp = ReliableUDP(sock1, "proxy", 5001, 2501)
    message = reliable_udp.receive()
    message = message[20:]
    if message == b'404':
        print("404 error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! YOU LOSE")
    else:
        print(message.decode("utf-8"))

    sock1.close()



