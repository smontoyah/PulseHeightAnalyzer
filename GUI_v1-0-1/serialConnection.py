import serial

class ArduinoConnection:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate)
        return self.connection.is_open

    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            return True
        return False

    def send(self, data):
        if self.connection and self.connection.is_open:
            self.connection.write(data.encode()+ b'\n')
            return True
        return False

    def read(self):
        if self.connection and self.connection.is_open:
            return self.connection.readline().decode().strip()
        return None
