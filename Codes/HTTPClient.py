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
    # request = "GET / HTTP/1.1\r\nHost: http://aut.ac.ir/"
    # request = "GET / HTTP/1.1\r\nHost: http://img.p30download.com/mac/image/2018/01/1515129443_3.jpg"
    request = "GET / HTTP/1.1\r\nHost: https://hw19.cdn.asset.aparat.com/aparat-video/131bd8138752fb07b71be9e6b3c7605611248968-720p__20585.mp4"
    reliable_udp.send(request)
    sock.close()

    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock1.bind(client2)
    reliable_udp = ReliableUDP(sock1, "proxy", 5001, 2501)
    message = reliable_udp.receive()

    # print(len(message))

    if message == b'404':
        print("404 error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! YOU LOSE")
    else:
        file = open("result", "wb")
        file.write(message)
        file.close()

    sock1.close()



