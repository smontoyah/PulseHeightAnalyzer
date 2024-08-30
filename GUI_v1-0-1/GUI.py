# All the functions have been tested
# Pending: Colorize the interface, make a version compatible with Raspberry Pi display
# Add the possibility to change the y-range even if the serial connection is finished
# It would be nice to have the possibility of stopping the spectra without closing the port

import tkinter as tk
from tkinter import messagebox
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI:
    def __init__(self, port, speed):
        # Initialize the GUI with the given serial port and speed
        self.port = port
        self.speed = speed
        self.generating_data = False
        self.ser = None
        self.x_data_accumulative = []
        self.y_data_accumulative = []
        self.save_flag = False

        # Set up the main window of the application
        self.root = tk.Tk()
        self.root.title("PHA UdeA 1.0.1")
        self.root.geometry("740x450")

        # Status label to show connection and operation status
        self.label = tk.Label(self.root, text="Status: OK") 
        self.label.grid(row=0, column=0, padx=10, pady=10, columnspan=4)

        # Create and arrange all the widgets in the window
        self.create_widgets()
        # Start updating the plot periodically
        self.update_plot()

    ################################################### 
    # Main function to create the widgets
    def create_widgets(self):
        # Create and arrange buttons, labels, and entry fields in the GUI
        button_connect = tk.Button(self.root, text="Connect", command=self.connect_serial)
        button_connect.grid(row=1, column=0, padx=5, pady=1)

        button_disconnect = tk.Button(self.root, text="Disconnect", command=self.disconnect_serial)
        button_disconnect.grid(row=1, column=1, padx=5, pady=1, columnspan=2)

        tk.Button(self.root, text="Run PHA", command=self.button_a_clicked).grid(row=2, column=0, padx=5, pady=1)
        tk.Button(self.root, text="Upper level", command=self.button_b_clicked).grid(row=3, column=0, padx=5, pady=1, sticky="e")
        
        # Entry field for setting the upper level
        self.entry_b = tk.Entry(self.root, width=6)
        self.entry_b.grid(row=3, column=1, padx=4, pady=1, sticky="w")
        self.entry_b.insert(0, "255")  # Default value to show
        tk.Label(self.root, text="0 to 255").grid(row=3, column=2, padx=5, pady=1, sticky="w")

        tk.Button(self.root, text="Lower level", command=self.button_c_clicked).grid(row=4, column=0, padx=5, pady=1, sticky="e")
        
        # Entry field for setting the lower level
        self.entry_c = tk.Entry(self.root, width=6)
        self.entry_c.grid(row=4, column=1, padx=5, pady=1, sticky="w")
        self.entry_c.insert(0, "0")  # Default value to show
        tk.Label(self.root, text="0 to 255").grid(row=4, column=2, padx=5, pady=1, sticky="w")

        tk.Button(self.root, text="Time window", command=self.button_d_clicked).grid(row=5, column=0, padx=5, pady=1, sticky="e")
        
        # Entry field for setting the time window
        self.entry_d = tk.Entry(self.root, width=6)
        self.entry_d.grid(row=5, column=1, padx=5, pady=1, sticky="w")
        self.entry_d.insert(0, "10")  # Default value to show
        tk.Label(self.root, text="ms").grid(row=5, column=2, padx=1, pady=5, sticky="w")

        tk.Button(self.root, text="Dwell time", command=self.button_e_clicked).grid(row=6, column=0, padx=5, pady=1, sticky="e")
        
        # Entry field for setting the dwell time
        self.entry_e = tk.Entry(self.root, width=6)
        self.entry_e.grid(row=6, column=1, padx=5, pady=1, sticky="w")
        self.entry_e.insert(0, "3")  # Default value to show
        tk.Label(self.root, text="s").grid(row=6, column=2, padx=1, pady=5, sticky="w")

        # Entry field for specifying the file name to save data
        self.entry_f = tk.Entry(self.root, width=20)
        self.entry_f.grid(row=6, column=3, padx=5, pady=1, sticky="e")
        self.entry_f.insert(0, "PHA_spectrum.txt")  # Default filename to show
        tk.Button(self.root, text="Save data", command=self.save_data_to_file).grid(row=6, column=4, padx=5, pady=1, sticky="w")

        # Slider for adjusting the y-range of the plot
        self.yrangeSlider = tk.Scale(self.root, from_=5, to=1, length=320, orient=tk.VERTICAL, showvalue=0)
        self.yrangeSlider.grid(row=1, column=7, padx=5, pady=1, sticky="w", rowspan=6)
        
        # Arrange the widgets on the grid
        for i in range(0, 6):
            self.root.grid_rowconfigure(i, minsize=0)

        # Set up the initial plot
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=80)
        # Plot initialization
        self.points = self.ax.stem([0], [0], linefmt='red', markerfmt='-.')[0]
        self.ax.set_ylabel('Counts')
        self.ax.set_xlabel('Channel (0 to 255)')
        # Integrate the plot with the Tkinter GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=5, padx=10, pady=10, columnspan=2)

    ####################################################### 
    # Functions
    def connect_serial(self):
        # Attempt to connect to the serial port
        try:
            self.ser = serial.Serial(self.port, self.speed, timeout=1)
            self.label.config(text="Status: Connected to " + str(self.port))
        except serial.SerialException as e:
            self.ser = None
            self.label.config(text="Connection error")
            messagebox.showerror("Error", str(e))

    def disconnect_serial(self):
        # Disconnect the serial port
        if self.ser:
            self.ser.close()
            self.ser = None
            self.label.config(text="Status: Closed connection")
        else:
            self.label.config(text="Error: Connection lost.")

    def send_to_arduino(self, prefix, data):
        # Send data to the Arduino via serial communication
        if not self.ser:
            self.label.config(text="Error: Connection lost.")
            return

        try:
            self.ser.write(f'{prefix}{data}\n'.encode())
            respuesta = self.ser.readline().decode().strip()
            print(respuesta)
        except Exception as e:
            self.label.config(text="Communication error")

    def button_a_clicked(self):
        # Start data generation and notify the user
        self.generate_data()
        messagebox.showinfo("Info", "PHA will start now! The plot will be updated periodically")

    def button_b_clicked(self):
        # Send the upper level value to the Arduino
        try:
            numero = int(self.entry_b.get())
            self.send_to_arduino('U', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_c_clicked(self):
        # Send the lower level value to the Arduino
        try:
            numero = int(self.entry_c.get())
            self.send_to_arduino('L', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_d_clicked(self):
        # Send the time window value to the Arduino
        try:
            numero = int(self.entry_d.get())
            self.send_to_arduino('tw', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_e_clicked(self):
        # Send the dwell time value to the Arduino
        try:
            numero = int(self.entry_e.get())
            self.send_to_arduino('ts', numero * 1000)  # Convert to milliseconds
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def generate_data(self):
        # Start generating data by sending a start command to the Arduino
        self.ser.write(f'start\n'.encode())
        self.data_counter = 0  # To count the valid data (number of updates of the plot)
        self.label.config(text="PHA is running now")

    def save_data_to_file(self):
        # Flag to save data to file after data is received
        self.save_flag = True

    ####################################### 
    # Main function to update the plot periodically
    def update_plot(self):
        # Update the plot with new data received from the Arduino
        if self.ser and self.ser.in_waiting:
            data = self.ser.readline().decode().strip().split(',')

            if len(data) == 256:
                self.x_data_accumulative = list(range(256))  # X axis remains constant
                self.y_data_accumulative = list(map(int, data))  # Convert all values to integers
                self.ax.clear()
                self.ax.set_ylim(0, max(self.y_data_accumulative) * self.yrangeSlider.get())
                self.ax.set_xlim(0, 255)
                self.ax.set_ylabel('Counts')
                self.ax.set_xlabel('Channel (0 to 255)')
                self.points = self.ax.stem(self.x_data_accumulative, self.y_data_accumulative, linefmt='red', markerfmt='-.')[0]
                self.canvas.draw()
                
                self.data_counter += 1  # Increment the data counter to track the number of valid data received
                self.label.config(text=f"Received {self.data_counter} updates")

                if self.save_flag:
                    with open(self.entry_f.get(), 'w') as file:
                        for x, y in zip(self.x_data_accumulative, self.y_data_accumulative):
                            file.write(f"{x},{y}\n")
                    self.label.config(text="Data saved in: " + self.entry_f.get())
                    self.save_flag = False  # Reset the save flag

        # Call the update_plot function again after a short delay
        self.root.after(300, self.update_plot)

    def run(self):
        # Start the main loop of the GUI
        self.root.mainloop()

# Example usage
app = GUI(port='/dev/ttyUSB0', speed=9600)
app.run()
