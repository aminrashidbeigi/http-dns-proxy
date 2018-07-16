import json
import requests
import socket
from Reliable import ReliableUDP as reliable

# DNS variables
port = 5555
host = 'localhost'
dns_type = 'CNAME'
dns_target = 'mail.google.com'
dns_server = '8.8.8.8'

# HTTP variables
client_address = 'localhost'
client_port1 = 5000
client_port2 = 5001
client1 = (client_address, client_port1)
client2 = (client_address, client_port2)

body = json.dumps({
    'dns_type': dns_type,
    'dns_target': dns_target,
    'dns_server': dns_server
})
if __name__ == '__main__':
    type_of_proxy = 'HTTP'
    if type_of_proxy == 'DNS':
        r = requests.post('http://127.0.0.1:5555/', body)
        print(r.text)
    elif type_of_proxy == 'HTTP':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(client1)
        reliable_udp = reliable(sock, "proxy", 5000, 2500)
        request = "GET / HTTP/1.1\r\nHost: http://aut.ac.ir"
        reliable_udp.send(request)
        sock.close()
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock1.bind(client2)
        reliable_udp = reliable(sock1, "proxy", 5001, 2501)
        reliable_udp.receive()
        sock1.close()

