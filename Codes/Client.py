import socket
import json

port = 5555
host = 'localhost'
dns_type = 'A'
dns_target = 'aut.ac.ir'
dns_server = '8.8.8.8'
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))
socket.send(bytes(json.dumps({
    'dns_type': dns_type,
    'dns_target': dns_target,
    'dns_server': dns_server
}), encoding="utf_8"))

response = socket.recv(1024)
socket.close()
print('Received', repr(response))
