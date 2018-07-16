 import json
import dns.resolver
import redis
from flask import Flask, request


port = 5555
host = '127.0.0.1'

app = Flask(__name__)
@app.route('/', methods = ['POST'])
def client_service():
    client_request = json.loads(str(request.data, encoding="utf_8"))
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    dns_type = client_request['dns_type']
    dns_target = client_request['dns_target']
    dns_server = client_request['dns_server']
    print("is here")
    dns_message = r.get('dns:' + str(dns_target))
    if not r.get('dns:' + str(dns_target)):
        dns_resolver = dns.resolver.Resolver()
        dns_resolver.timeout = 1
        dns_resolver.lifetime = 1
        query = dns.message.make_query(dns_target, dns_type)
        dns_message = dns.query.udp(query, dns_server)
        r.set('dns:' + str(dns_target), dns_message)
    if dns_type is 'A':
        return str(dns_message)
    elif dns_type is 'CNAME':
        dns_message = dns.resolver.query('mail.google.com', 'CNAME')
        print('query qname:', dns_message.qname, ' num ans.', len(dns_message))
        for data in dns_message:
            print(' cname target address:', data.target)
        return str(dns_message)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5555)