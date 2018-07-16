import json
import dns.resolver
import redis
from flask import Flask, request
import socket
import requests
from Reliable import ReliableUDP as reliable

# DNS variables
port = 5555
host = '127.0.0.1'
app = Flask(__name__)

# HTTP variables
proxy_address = 'localhost'
proxy_port1 = 2500
proxy_port2 = 2501
proxy1 = (proxy_address, proxy_port1)
proxy2 = (proxy_address, proxy_port2)


@app.route('/', methods = ['POST'])
def client_service():
    client_request = json.loads(str(request.data, encoding="utf_8"))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    dns_type = client_request['dns_type']
    dns_target = client_request['dns_target']
    dns_server = client_request['dns_server']
    answer_for_client_in_cache = r.get('dns:' + str(dns_target) + str(dns_type))
    answer_for_client = {
        'authoritative': 0,
        'result': []
    }
    if not r.get('dns:' + str(dns_target) + str(dns_type)):
        print("Response from dns server.")
        if dns_type == 'A':
            query = dns.resolver.query(dns_target, dns_type)
            make_query = dns.message.make_query(dns_target, dns_type)
            udp_message = dns.query.udp(make_query, dns_server)
            answer_for_client['authoritative'] = udp_message.flags & dns.flags.AA
            for data in query:
                answer_for_client['result'].append(data.to_text())
        elif dns_type == 'CNAME':
            query = dns.resolver.query(dns_target, dns_type)
            make_query = dns.message.make_query(dns_target, dns_type)
            udp_message = dns.query.udp(make_query, dns_server)
            answer_for_client['authoritative'] = udp_message.flags & dns.flags.AA
            for data in query:
                answer_for_client['result'].append(data.to_text())
        r.set('dns:' + str(dns_target) + str(dns_type), answer_for_client)
        return str(answer_for_client)
    else:
        print("Response from cache :)")
        return str(answer_for_client_in_cache)


def send_request(request):
    request, headers = request.split('\r\n', 1)
    headers = headers.split('\r\n')
    options = {}
    for option in headers:
        option_key = option.split(':')[0]
        option_value = option.split(': ')[1]
        options[option_key] = option_value
    r = requests.get(options["Host"])
    return r.text

if __name__ == '__main__':
    type_of_proxy = 'HTTP'
    if type_of_proxy == 'DNS':
        app.run(host="127.0.0.1", port=5555)
    elif type_of_proxy == 'HTTP':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(proxy1)
        reliable_udp = reliable(sock, "client", 5000, 2500)
        message = reliable_udp.receive()
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(proxy2)
        reliable_udp = reliable(sock, "client", 5001, 2501)
        data = send_request(message.decode('utf-8'))
        reliable_udp.send(data)
        sock.close()