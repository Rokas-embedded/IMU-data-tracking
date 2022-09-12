from asyncio.windows_events import NULL
from dataclasses import dataclass
import json
from msilib.schema import Error
from pickle import FALSE
from tkinter import W
from tkinter.ttk import Style
import numpy as np
import PySimpleGUI as sg
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import threading
from random import randint
import time
import serial.tools.list_ports
import json 

# matplotlib.use("TkAgg")
style.use("ggplot")
fig_agg = False
pltFig = False
window = False
dataSize = 1000
x_accel_graph = False
y_accel_graph = False
z_accel_graph = False

# Define the window layout
port_config_collumn = [
    [
        sg.Text("Selected: ", key="-SELECTED-"),
    ],
    [
        sg.Text("Baud rate"),
        sg.In(size=(10, 1), enable_events=False, key="-BAUD-"),
        sg.Button("Start", key="-START BUTTON-"),
    ],
    [
        sg.Text("Available COM ports"),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-COM LIST-"
        )
    ]
]

plot_collumn = [
    [
        sg.Canvas(key="-CANVAS-")
    ],
    # [
    #     sg.Canvas(key="-CANVAS-")
    # ],
    
]

layout = [
    [
        sg.Column(port_config_collumn),
        sg.VSeperator(),
        sg.Column(plot_collumn),
        sg.Column(plot_collumn),
    ],
]

# Create the form and show it without the plot
window = sg.Window(
    "Matplotlib Single Graph",
    layout,
    location=(0, 0),
    finalize=True,
    font="Helvetica 18",
)


duration = 0.1
def the_thread(window):

    global duration

    time_start = time.time()
    while True:
        time.sleep(0.01)
        if time.time()-time_start >= duration:
            time_start = time.time()
            data = (randint(0, 1000), randint(0, 1000))
            window.write_event_value('-THREAD-', data)

threading.Thread(target=the_thread, args=(window,), daemon=True).start()

selected_port_full_name = ""
selected_port = ""
started = False
baud_rate = 0
serialInst = serial.Serial()

accel_x_readings_size = 500
accel_x_readings = [0] * (accel_x_readings_size-1)
accel_y_readings_size = 500
accel_y_readings = [0] * (accel_y_readings_size-1)
accel_z_readings_size = 500
accel_z_readings = [0] * (accel_z_readings_size-1)


def read_message(message):
    accel_x = 0
    accel_y = 0
    accel_z = 0

    # ACCEL, 3.44, 464.5, 46461, 
    try:
        message_split = message.split(', ')

        accel_x = float(message_split[1])
        accel_x_readings.append(accel_x)
        if(len(accel_x_readings) == accel_x_readings_size):
            accel_x_readings.pop(0) 
        

        accel_y = float(message_split[2])
        accel_y_readings.append(accel_y)
        if(len(accel_y_readings) == accel_y_readings_size):
            accel_y_readings.pop(0)


        accel_z = float(message_split[3])
        accel_z_readings.append(accel_z)
        if(len(accel_z_readings) == accel_z_readings_size):
            accel_z_readings.pop(0)

    except:
        print("error serial")
    
    
    
    return

old_port_baud_rates = []
with open('ports.txt') as f:
    old_port_baud_rates = f.read().splitlines()
    f.close()

for index, old in enumerate(old_port_baud_rates):
    old_values = old.split(';')
    old_port_baud_rates[index] = (old_values[0], old_values[1])

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def makeSynthData():
    xData = np.random.randint(100, size=dataSize)
    yData = np.linspace(0, dataSize, num=dataSize, dtype=int)
    return (xData, yData)

def drawChart():
    global fig_agg
    global pltFig
    global x_accel_graph
    global y_accel_graph
    global z_accel_graph


    pltFig = plt.figure()
    x_accel_graph = plt.plot(accel_x_readings)
    y_accel_graph = plt.plot(accel_y_readings)
    z_accel_graph = plt.plot(accel_z_readings)
    plt.ylim(-2,2)

    fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, pltFig)
    return

def updateChart():
    global fig_agg
    global pltFig
    global x_accel_graph
    global y_accel_graph
    global z_accel_graph

    # Redrawing the plots works very good
    plt.clf()
    x_accel_graph = plt.plot(accel_x_readings)
    x_accel_graph = plt.plot(accel_y_readings)
    x_accel_graph = plt.plot(accel_z_readings)
    plt.ylim(-2,2)

    # this is too slow

    # pltFig.canvas.draw_idle()
    # fig_agg.get_tk_widget().forget()
    # fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, pltFig)
    pltFig.canvas.draw()


drawChart()
# Run the Event Loop
while True:

    event, values= window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-START BUTTON-":
        if(started):
            window["-START BUTTON-"].update("Start")
            started = False
            serialInst.close()
        else:
            if(window["-BAUD-"] != ""):
                baud_rate_value = values["-BAUD-"]
                is_int = False
                try:
                    val = int(baud_rate_value)
                    if val > 0:
                        is_int = True
                        baud_rate = val
                except ValueError:
                    is_int = False 

                if(is_int):
                    window["-BAUD-"].update(background_color='white')
                    window["-START BUTTON-"].update("Stop")
                    started = True

                    with open('ports.txt', 'w') as f:
                        f.write(selected_port_full_name + ";" + str(baud_rate) + "\n")
                        f.close()

                    serialInst.baudrate = baud_rate
                    serialInst.port = selected_port
                    serialInst.open()
            else:
                window["-BAUD-"].update(background_color='red')
    elif event == "-COM LIST-":
        selected_port = values["-COM LIST-"][0].split(' -')[0]
        selected_port_full_name = values["-COM LIST-"][0]
        window["-SELECTED-"].update("Selected: " + selected_port)
        for old in old_port_baud_rates:
            if(old[0] == values["-COM LIST-"][0]):
                baud_rate = old[1]
                window["-BAUD-"].update(str(baud_rate))
                break

    elif event == "-THREAD-":
        serial_ports = serial.tools.list_ports.comports()

        serial_ports_str = []
        for s in serial_ports:
            serial_ports_str.append(str(s))
        
        window["-COM LIST-"].update(serial_ports_str)
        
        if(started):
            while serialInst.in_waiting:
                read_message(serialInst.readline().decode('utf'))
            updateChart()

    

window.close()
