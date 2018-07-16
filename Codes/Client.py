import json
import requests

port = 5555
host = 'localhost'
dns_type = 'CNAME'
dns_target = 'aut.ac.ir'
dns_server = '8.8.8.8'
body = json.dumps({
    'dns_type': dns_type,
    'dns_target': dns_target,
    'dns_server': dns_server
})
r = requests.post('http://127.0.0.1:5555/', body)

print('Received', r.text)
