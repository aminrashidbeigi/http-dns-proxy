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
    dns_type = client_request['dns_type']
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    dns_target = client_request['dns_target']
    dns_server = client_request['dns_server']
    dns_message = r.get('dns:' + str(dns_target))
    if not r.get('dns:' + str(dns_target)):
        dns_resolver = dns.resolver.Resolver()
        dns_resolver.timeout = 1
        dns_resolver.lifetime = 1
        query = dns.message.make_query(dns_target, dns_type)
        dns_message = dns.query.udp(query, dns_server)
        r.set('dns:' + str(dns_target), dns_message)
    # for key in r.scan_iter("dns:*"):
    #     print(key)
    return str(dns_message)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5555)