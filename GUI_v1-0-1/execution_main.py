from GUI import GUI

if __name__ == "__main__":
    print('Ejecutando main')

    port = 'COM10'
    speed = 9600

    gui = GUI(port,speed)
    gui.start()

    