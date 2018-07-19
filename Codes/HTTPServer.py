import socket
import requests
from reliable import ReliableUDP

proxy_address = 'localhost'
proxy_port1 = 2500
proxy_port2 = 2501

proxy1 = (proxy_address, proxy_port1)
proxy2 = (proxy_address, proxy_port2)


def send_request(request):
    request, headers = request.split('\r\n', 1)
    headers = headers.split('\r\n')

    options = {}

    for option in headers:
        option_key = option.split(':')[0]
        option_value = option.split(': ')[1]
        options[option_key] = option_value

    r = requests.get(options["Host"])
    if r.status_code == 404:
        return "404"
    else:
        return r.text


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(proxy1)

    reliable_udp = ReliableUDP(sock, "client", 5000, 2500)
    message = reliable_udp.receive()
    sock.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(proxy2)
    reliable_udp = ReliableUDP(sock, "client", 5001, 2501)

    data = send_request(message.decode('utf-8'))
    reliable_udp.send(data)
    sock.close()







