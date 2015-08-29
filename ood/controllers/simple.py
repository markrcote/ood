import socket


class SimpleServerController(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        return self._send_cmd('start')

    def stop(self):
        return self._send_cmd('stop')

    def running(self):
        response = self._send_cmd('running').lower()
        return response == 'true'

    def _send_cmd(self, cmd):
        buf = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.sendall('%s\n' % cmd)

        while '\n' not in buf:
            buf += s.recv(1024)

        response, nl, buf = buf.partition('\n')
        s.close()
        return response
