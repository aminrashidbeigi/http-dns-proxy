import json
import dns.resolver
import redis
from flask import Flask, request

# DNS variables
port = 5555
host = '127.0.0.1'
app = Flask(__name__)


@app.route('/', methods=['POST'])
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
            # answer_for_client['authoritative'] = bytes(query[7])
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


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5555)
