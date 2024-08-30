import serial  # Import the serial library for serial communication

# Define a class to manage the Arduino connection
class ArduinoConnection:
    def __init__(self, port, baudrate):
        # Initialize with the specified port and baud rate
        self.port = port
        self.baudrate = baudrate
        self.connection = None  # Placeholder for the serial connection

    # Method to establish a connection with the Arduino
    def connect(self):
        # Create a serial connection using the provided port and baudrate
        self.connection = serial.Serial(self.port, self.baudrate)
        # Return True if the connection is successfully opened
        return self.connection.is_open

    # Method to disconnect the Arduino
    def disconnect(self):
        # Check if there is an active connection
        if self.connection and self.connection.is_open:
            # Close the connection
            self.connection.close()
            return True  # Indicate that the disconnection was successful
        return False  # Indicate that there was no active connection to close

    # Method to send data to the Arduino
    def send(self, data):
        # Check if the connection is active
        if self.connection and self.connection.is_open:
            # Send the data encoded as bytes with a newline character
            self.connection.write(data.encode() + b'\n')
            return True  # Indicate that the data was successfully sent
        return False  # Indicate that the data could not be sent due to an inactive connection

    # Method to read data from the Arduino
    def read(self):
        # Check if the connection is active
        if self.connection and self.connection.is_open:
            # Read a line of data, decode it, and remove leading/trailing whitespace
            return self.connection.readline().decode().strip()
        return None  # Return None if there is no active connection to read from

