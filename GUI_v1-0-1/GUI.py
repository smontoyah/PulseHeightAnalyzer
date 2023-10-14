#All the functions has been tested
#Pending: Colorize, make a version compatible with raspberry PI display
#Add the possibility to change the yrange even if the serial connection is finished.
#Would be nice to have the possibility of stopping the spectra without closing the port.

import tkinter as tk
from tkinter import messagebox
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI:
    def __init__(self, port, speed):
        self.port = port
        self.speed = speed
        self.generating_data = False
        self.ser = None
        self.x_data_accumulative = []
        self.y_data_accumulative = []
        self.save_flag = False

        self.root = tk.Tk()
        self.root.title("PHA UdeA 1.0.1")
        self.root.geometry("740x450")

        self.label = tk.Label(self.root, text="Status: OK") 
        self.label.grid(row=0, column=0, padx=10, pady=10, columnspan=4)

        self.create_widgets()
        self.update_plot()

################################################### Main function to create the widgets
    def create_widgets(self):
        # Buttons
        button_connect = tk.Button(self.root, text="Connect", command=self.connect_serial)
        button_connect.grid(row=1, column=0, padx=5, pady=1)

        button_disconnect = tk.Button(self.root, text="Disconnect", command=self.disconnect_serial)
        button_disconnect.grid(row=1, column=1, padx=5, pady=1, columnspan=2)

        tk.Button(self.root, text="Run PHA", command=self.button_a_clicked).grid(row=2, column=0, padx=5, pady=1)
        tk.Button(self.root, text="Upper level", command=self.button_b_clicked).grid(row=3, column=0, padx=5, pady=1, sticky="e")
        self.entry_b = tk.Entry(self.root, width=6)
        self.entry_b.grid(row=3, column=1, padx=4, pady=1, sticky="w")
        self.entry_b.insert(0, "255") #default value to show
        tk.Label(self.root, text="0 to 255").grid(row=3, column=2, padx=5, pady=1, sticky="w")

        tk.Button(self.root, text="Lower level", command=self.button_c_clicked).grid(row=4, column=0, padx=5, pady=1, sticky="e")
        self.entry_c = tk.Entry(self.root, width=6)
        self.entry_c.grid(row=4, column=1, padx=5, pady=1, sticky="w")
        self.entry_c.insert(0, "0") #default value to show
        tk.Label(self.root, text="0 to 255").grid(row=4, column=2, padx=5, pady=1, sticky="w")

        tk.Button(self.root, text="Time window", command=self.button_d_clicked).grid(row=5, column=0, padx=5, pady=1, sticky="e")
        self.entry_d = tk.Entry(self.root, width=6)
        self.entry_d.grid(row=5, column=1, padx=5, pady=1, sticky="w")
        self.entry_d.insert(0, "10") #default value to show
        tk.Label(self.root, text="ms").grid(row=5, column=2, padx=1, pady=5, sticky="w")

        tk.Button(self.root, text="Dwell time", command=self.button_e_clicked).grid(row=6, column=0, padx=5, pady=1, sticky="e")
        self.entry_e = tk.Entry(self.root, width=6)
        self.entry_e.grid(row=6, column=1, padx=5, pady=1, sticky="w")
        self.entry_e.insert(0, "3") #default value to show
        tk.Label(self.root, text="s").grid(row=6, column=2, padx=1, pady=5, sticky="w")

        self.entry_f = tk.Entry(self.root, width=20)
        self.entry_f.grid(row=6, column=3, padx=5, pady=1, sticky="e")
        self.entry_f.insert(0, "PHA_spectrum.txt") #default filename to show
        tk.Button(self.root, text="Save data", command=self.save_data_to_file).grid(row=6, column=4, padx=5, pady=1, sticky="w")

        self.yrangeSlider = tk.Scale(self.root, from_= 5, to= 1, length=320, orient=tk.VERTICAL, showvalue=0)
        self.yrangeSlider.grid(row=1, column=7, padx=5, pady=1, sticky="w", rowspan=6)
        #arrange the widgets on grid
        for i in range(0, 6):
            self.root.grid_rowconfigure(i, minsize=0)

        # Set up the initial plot
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=80)
        #self.points = self.ax.plot([], [], '.')[0]
        self.points = self.ax.stem([0], [0], linefmt ='red', markerfmt ='-.')[0]
        self.ax.set_ylabel('Counts')
        self.ax.set_xlabel('Channel (0 to 255)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, column=3, rowspan=5, padx=10, pady=10, columnspan=2)

####################################################### Functions
    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.speed, timeout=1)
            self.label.config(text="Status: Connected to "+str(self.port))
        except serial.SerialException as e:
            self.ser = None
            self.label.config(text="Connection error")
            messagebox.showerror("Error", str(e))

    def disconnect_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.label.config(text="Status: Clossed connection")
        else:
            self.label.config(text="Error: Connection lost.")

    def send_to_arduino(self, prefix, data):
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
        self.generate_data()
        messagebox.showinfo("Info", "PHA will start now!. The plot will be updated periodacally")

    def button_b_clicked(self):
        try:
            numero = int(self.entry_b.get())
            self.send_to_arduino('U', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_c_clicked(self):
        try:
            numero = int(self.entry_c.get())
            self.send_to_arduino('L', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_d_clicked(self):
        try:
            numero = int(self.entry_d.get())
            self.send_to_arduino('tw', numero)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def button_e_clicked(self):
        try:
            numero = int(self.entry_e.get())
            self.send_to_arduino('ts', numero*1000)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def generate_data(self):
        self.ser.write(f'start\n'.encode())
        self.data_counter=0 #To count the valid data (# of updates of the plot)
        self.label.config(text="PHA is running now")

    def save_data_to_file(self):
        self.save_flag=True

####################################### Main function to update the plot periodically
    def update_plot(self):
        if self.ser:
            try:
                datos=self.ser.readline().decode().strip()
                if(len(datos)>0):
                    print('datos: '+datos) #for debugging
                    if(datos[1]=="*"):
                        self.data_counter=self.data_counter+1 #To count the valid data (# of updates of the plot)
                        self.label.config(text="Valid data received ["+str(self.data_counter)+"]")
                        elementos = datos.split(',')
                        self.x_data, self.y_data = zip(*(map(int, elem.split('*')) for elem in elementos if len(elem.split('*')) == 2))
                        self.points.set_xdata(self.x_data)
                        self.points.set_ydata(self.y_data)
                        self.ax.set_ylim(bottom=0, top=10**int(self.yrangeSlider.get()))
                        self.ax.relim()
                        self.ax.autoscale_view()
                        self.canvas.draw()
                    elif datos == 'finished':
                        self.label.config(text="All the PHA data has been received")
                        self.data_counter=0

                if self.save_flag == True:
                    file_name=self.entry_f.get()
                    file = open(file_name,'w')
                    for line in self.y_data:
                        file.write(str(line)+"\n")
                    file.close()
                    self.label.config(text="Data saved to file")
                    self.save_flag=False

                # Append new data to the cumulative data
                #self.x_data_accumulative.extend(x_data)
                #self.y_data_accumulative.extend(y_data)

                ##self.points.set_xdata(self.x_data_accumulative) #Grafica los acumulados
                ##self.points.set_ydata(self.y_data_accumulative)

            except Exception as e:
                self.label.config(text=e)

        self.root.after(2000, self.update_plot)

    def start(self):
        self.root.mainloop()

##Serial connection paramerters. Pending: change "COM6" with an user selectable variable
if __name__ == "__main__":
    gui = GUI("COM18", 115200)
    gui.start()
