import os
from serial import Serial
if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError(f"Sorry: no implementation for platform ('{os.name}')")
from time import sleep

DEVICE = 'CH340'    # USB serial adapter reported by OBD-II device driver


def find_port(device=None):     # Find serial port used by device
    devport = ''
    i = -1
    while not devport:
        ports = []
        for port, desc, hwid in sorted(comports()):
            ports.append({'port': port, 'desc': desc, 'hwid': hwid})
            if device in desc:
                return port     # Found it
        if not (i := (i + 1) % 15):
            print(f'Waiting for device {device}, {[k["desc"] for k in ports]}')
        sleep(1)


class Sp:
    def __init__(self, port=None):
        self.port = port        # Serial port name
        self.model = None       # OBD device model
        self.response = ''      # Raw response string received from device
        self.Sc = None          # Serial port class
        self.connect()          # Connect to and initialize device

    def command(self, cmd=''):      # Send AT or OBD command, wait for > prompt
        self.Sc.write(f'{cmd}\r'.encode())
        t = 100
        while (t := t - 1) >= 0:
            rsp = self.Sc.read(100)
            if rsp.endswith(b'>'):
                self.response = rsp.decode()
                return [k for k in self.response.split('\r') if k][-2]
        raise RuntimeError(f'Timeout waiting for prompt, cmd={cmd}, rsp={rsp.decode()}')

    def connect(self):
        self.Sc = Serial(self.port, 38400, timeout=0.01)
        self.model = self.command('atws')     # Warm start
        self.command('ate0')    # Echo off


if __name__ == '__main__':
    port = find_port(DEVICE)
    sp = Sp(port)
    print(sp.model, 'connected on', sp.port)
    print('Battery:', sp.command('atrv'), 'Ignition:', sp.command('atign'))
    sp.command('atsp0')
    print('Protocol:', sp.command('0100'))



