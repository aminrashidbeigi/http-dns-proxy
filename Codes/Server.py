import socket
import json
import dns.resolver
import redis

port = 5555
host = '0.0.0.0'
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host, port))
socket.listen(1)
connect, address = socket.accept()
print('Connected by', address)
while True:
    client_request_json = connect.recv(1024)
    if not client_request_json:
        break
    client_request = json.loads(str(client_request_json, encoding="utf_8"))
    dns_type = client_request['dns_type']
    dns_target = client_request['dns_target']
    dns_server = client_request['dns_server']
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    dns_message = redis.get('dns:' + str(dns_target))
    if not redis.get('dns:' + str(dns_target)):
        dns_resolver = dns.resolver.Resolver()
        query = dns.message.make_query(dns_target, dns_type)
        dns_message = dns.query.udp(query, dns_server)
        redis.set('dns:' + str(dns_target), dns_message)
    connect.send(bytes(str(dns_message), encoding='utf_8'))
    for key in redis.scan_iter("dns:*"):
        print(key)
connect.close()