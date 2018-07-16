import _thread
import time
import copy


class ReliableUDP:

    class Timer(object):
        TIMER_STOP = -1

        def __init__(self, duration):
            self._start_time = self.TIMER_STOP
            self._duration = duration

        def start(self):
            if self._start_time == self.TIMER_STOP:
                self._start_time = time.time()

        def stop(self):
            if self._start_time != self.TIMER_STOP:
                self._start_time = self.TIMER_STOP

        def running(self):
            return self._start_time != self.TIMER_STOP

        def timeout(self):
            if not self.running():
                return False
            else:
                return time.time() - self._start_time >= self._duration

    def __init__(self, sock, dest, client_port, proxy_port):

        self.dest = dest
        self.sock = sock

        self.packet_size = 1024

        self.proxy_address = 'localhost'
        self.proxy_port = proxy_port
        self.proxy = (self.proxy_address, self.proxy_port)

        self.client_address = 'localhost'
        self.client_port = client_port
        self.client = (self.client_address, self.client_port)

        self.destination = self.client if dest == "client" else self.proxy

        self.SLEEP_INTERVAL = 0.05
        self.TIMEOUT_INTERVAL = 0.5
        self.WINDOW_SIZE = 4

        self.segment_period = 0

        self.mutex = _thread.allocate_lock()
        self.send_timer = self.Timer(self.TIMEOUT_INTERVAL)
        self.base = 0

        self.buffer_size = 1024

    def send(self, message):

        packets = self.make_packets(message)

        number_of_packets = len(packets)

        window_size = min(self.WINDOW_SIZE, number_of_packets - self.base)

        next_to_send = 0
        self.base = 0

        _thread.start_new_thread(self.receive_ack, (self.sock,))

        while self.base < number_of_packets:
            self.mutex.acquire()

            while next_to_send < self.base + window_size:
                print('Sending packet', next_to_send)
                self.sock.sendto(packets[next_to_send], self.destination)
                next_to_send += 1

            if not self.send_timer.running():
                print('Starting timer')
                self.send_timer.start()

            while self.send_timer.running() and not self.send_timer.timeout():
                self.mutex.release()
                print('Sleeping')
                time.sleep(self.SLEEP_INTERVAL)
                self.mutex.acquire()

            if self.send_timer.timeout():
                print('Timeout')
                self.send_timer.stop()
                next_to_send = self.base

            else:
                print('Shifting window')
                window_size = min(self.WINDOW_SIZE, number_of_packets - self.base)

            self.mutex.release()

    def receive_ack(self, sock):

        while True:
            pkt, _ = sock.recvfrom(1024)
            ack, _ = unpack(pkt)

            print('Got ACK', ack)
            if ack >= self.base % 16:
                self.mutex.acquire()
                self.base = self.segment_period * 16 + ack + 1
                if ack + 1 == 16:
                    self.segment_period += 1
                print('Base updated', self.base)
                self.send_timer.stop()
                self.mutex.release()

    def make_packets(self, message):

        byte_request = bytes(message, "utf-8")
        packets = []
        sequence_number = 0
        first, last = 0, self.packet_size

        if last < len(byte_request):

            while last < len(byte_request):
                packets.append(pack((sequence_number % 16), byte_request[first:min(last, len(byte_request))]))
                first = copy.deepcopy(last)
                last = first + self.packet_size
                sequence_number += 1
        else:
            packets.append(pack((sequence_number % 16), byte_request[first:len(byte_request)]))

        return packets

    def receive(self):

        expected_sequence_number = 0
        message = bytes()

        while True:
            pkt, address = self.sock.recvfrom(self.buffer_size)
            sequence_number, data = unpack(packet=pkt)

            print("sending ack with sequence number: ", sequence_number)

            if sequence_number == expected_sequence_number:
                message += data
                pkt = pack(sequence_number)
                self.sock.sendto(pkt, address)
                expected_sequence_number += 1
                expected_sequence_number %= 16
            else:
                print("sending ack with sequence number: ", sequence_number - 1)
                pkt = pack(sequence_number - 1)
                self.sock.sendto(pkt, address)

            if self.dest == "client":
                break

        return message


def unpack(packet):
    sequence_num = int.from_bytes(packet[0:4], byteorder="little", signed=True)
    return sequence_num, packet[4:]


def pack(sequence_number, data=b''):
    sequence_bytes = sequence_number.to_bytes(4, byteorder='little', signed=True)
    return sequence_bytes + data

