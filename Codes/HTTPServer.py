import socket
import requests
from reliable import ReliableUDP
import redis
import os

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

    host_option = options["Host"]
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete('http:status:' + str(host_option))
    cached_http_response_content = r.get('http:content:' + str(host_option))
    cached_http_response_status = r.get('http:status:' + str(host_option))
    if not cached_http_response_status:
        print("Response from http server.")
        http_response = requests.get(host_option)
        cached_http_response_status = http_response.status_code
        cached_http_response_content = http_response.content

        # print(http_response)
        r.set('http:status:' + str(host_option), cached_http_response_status)
        r.set('http:content:' + str(host_option), cached_http_response_content)
        if http_response.status_code == 404:
            return "404".encode("utf-8")
        else:
            return http_response.content
    elif cached_http_response_status == b'404':
        print("Response from cache :)")
        return "404".encode("utf-8")
    else:
        print("Response from cache :)")
        return cached_http_response_content


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
    file = open("result2", "wb")
    file.write(data)
    file.close()

    # print(len(data))
    #
    # fakedata = bytearray(os.urandom(1030))
    reliable_udp.send(data)
    # print("Len of fake data is ", len(fakedata))
    # print("fake data is -> ", str(fakedata))
    sock.close()
