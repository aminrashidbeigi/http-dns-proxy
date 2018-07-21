import json
import requests

# DNS variables
port = 5555
host = 'localhost'
dns_type = 'A'
dns_target = 'mail.google.com'
dns_server = '8.8.8.8'
body = json.dumps({
    'dns_type': dns_type,
    'dns_target': dns_target,
    'dns_server': dns_server
})

if __name__ == '__main__':
    r = requests.post('http://127.0.0.1:5555/', body)
    print(r.text)

