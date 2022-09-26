from asyncio.windows_events import NULL
from dataclasses import dataclass
import json
from msilib.schema import Error
from pickle import FALSE
from tkinter import W
from tkinter.ttk import Style
from turtle import update
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
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy import signal
from matplotlib.pyplot import figure
import scipy
import copy

accel_fig_agg = False
accel_pltFig = False
freq_fig_agg = False
freq_pltFig = False
gyro_fig_agg = False
gyro_pltFig = False
mag_fig_agg = False
mag_pltFig = False

window = False
dataSize = 1000
frequencies = [0] * 500

accel_graph = 0
frequency_graph = 1
gyro_graph = 2
mag_graph = 3



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
            values=[], enable_events=True, size=(25, 20), key="-COM LIST-"
        )
    ]
]

plot_collumn = [
    [
        sg.Button("TIME-FREQUENCY", key="-TIME FREQUENCY-")
    ],
    [
        sg.Canvas(key="-ACCELERATION-")
    ],
    [
        sg.Canvas(key="-GYRO-")
    ],
    [
        sg.Canvas(key="-MAG-")
    ],
    [
        sg.Canvas(key="-TIME FREQUENCY PLOT-")
    ],
]

layout = [
    [
        sg.Column(port_config_collumn),
        sg.VSeperator(),
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


duration = 0.01
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

accel_x_readings_size = dataSize
accel_x_readings = [0] * (accel_x_readings_size-1)
accel_y_readings_size = dataSize
accel_y_readings = [0] * (accel_y_readings_size-1)
accel_z_readings_size = dataSize
accel_z_readings = [0] * (accel_z_readings_size-1)

gyro_x_readings_size = dataSize
gyro_x_readings = [0] * (gyro_x_readings_size-1)
gyro_y_readings_size = dataSize
gyro_y_readings = [0] * (gyro_y_readings_size-1)
gyro_z_readings_size = dataSize
gyro_z_readings = [0] * (gyro_z_readings_size-1)


mag_x_readings_size = dataSize
mag_x_readings = [0] * (mag_x_readings_size-1)
mag_y_readings_size = dataSize
mag_y_readings = [0] * (mag_y_readings_size-1)
mag_z_readings_size = dataSize
mag_z_readings = [0] * (mag_z_readings_size-1)


def read_message(message):
    accel_x = 0
    accel_y = 0
    accel_z = 0

    gyro_x = 0
    gyro_y = 0
    gyro_z = 0

    mag_x = 0
    mag_y = 0
    mag_z = 0

    # ACCEL,  -0.03,   0.00,   1.01, GYRO,  -0.37,  -0.01,   0.09, MAG,   0.35,   0.13,   0.04,
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


        gyro_x = float(message_split[5])
        gyro_x_readings.append(gyro_x)
        if(len(gyro_x_readings) == gyro_x_readings_size):
            gyro_x_readings.pop(0) 
        
        gyro_y = float(message_split[6])
        gyro_y_readings.append(gyro_y)
        if(len(gyro_y_readings) == gyro_y_readings_size):
            gyro_y_readings.pop(0)

        gyro_z = float(message_split[7])
        gyro_z_readings.append(gyro_z)
        if(len(gyro_z_readings) == gyro_z_readings_size):
            gyro_z_readings.pop(0)


        mag_x = float(message_split[9])
        mag_x_readings.append(mag_x)
        if(len(mag_x_readings) == mag_x_readings_size):
            mag_x_readings.pop(0) 
        
        mag_y = float(message_split[10])
        mag_y_readings.append(mag_y)
        if(len(mag_y_readings) == mag_y_readings_size):
            mag_y_readings.pop(0)

        mag_z = float(message_split[11])
        mag_z_readings.append(mag_z)
        if(len(mag_z_readings) == mag_z_readings_size):
            mag_z_readings.pop(0)

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

def drawChart(chart):
    global accel_fig_agg
    global accel_pltFig
    
    global freq_fig_agg
    global freq_pltFig

    global gyro_fig_agg
    global gyro_pltFig

    global mag_fig_agg
    global mag_pltFig
    if(chart == 0):
        accel_pltFig = plt.figure(figsize=(10, 3))
        plt.plot(accel_x_readings,label='ac_Y')
        plt.plot(accel_y_readings,label='ac_Y')
        plt.plot(accel_z_readings,label='ac_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("G's")
        plt.ylim(0.5,1.5)
        plt.ylim(-2,2)
        plt.grid()
        accel_fig_agg = draw_figure(window["-ACCELERATION-"].TKCanvas, accel_pltFig)
    elif(chart == 1):
        freq_pltFig = plt.figure(figsize=(10, 3))
        plt.plot(frequencies)
        plt.xlabel('Frequency')
        plt.ylabel("Power")
        plt.xlim(0,500)
        plt.ylim(-0.1,50)
        plt.grid()

        freq_fig_agg = draw_figure(window["-TIME FREQUENCY PLOT-"].TKCanvas, freq_pltFig)
    elif(chart == 2):
        gyro_pltFig = plt.figure(figsize=(10, 3))
        plt.plot(gyro_x_readings,label='gy_Y')
        plt.plot(gyro_y_readings,label='gy_Y')
        plt.plot(gyro_z_readings,label='gy_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("R/s")
        plt.ylim(-360,360)
        plt.grid()
        gyro_fig_agg = draw_figure(window["-GYRO-"].TKCanvas, gyro_pltFig)
    
    elif(chart == 3):
        mag_pltFig = plt.figure(figsize=(4, 4))
        
        plt.scatter(mag_x_readings, mag_y_readings, label='mag_Y')
        # plt.plot(mag_x_readings,label='mag_X')
        # plt.plot(mag_y_readings,label='mag_Y')
        # plt.plot(mag_z_readings,label='mag_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("Gauss")
        plt.xlim(-200,200)
        plt.ylim(-200,200)

        plt.grid()
        mag_fig_agg = draw_figure(window["-MAG-"].TKCanvas, mag_pltFig)
    return

def updateChart(chart):
    global accel_fig_agg
    global accel_pltFig

    global freq_fig_agg
    global freq_pltFig

    global gyro_fig_agg
    global gyro_pltFig

    if(chart == 0):
            
        # Redrawing the plots works very good
        plt.figure(accel_pltFig.number)
        plt.clf()
        plt.plot(accel_x_readings,label='ac_X')
        plt.plot(accel_y_readings,label='ac_Y')
        plt.plot(accel_z_readings,label='ac_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("G's")
        plt.ylim(-2,2)
        # plt.ylim(0.5,1.5)
        plt.grid()
        accel_pltFig.canvas.draw()

    elif(chart == 1):
        plt.figure(freq_pltFig.number)

        plt.clf()
        plt.plot(frequencies)
        plt.xlabel('Frequency')
        plt.ylabel("Power")
        plt.xlim(0,500)
        plt.ylim(-0.1,50)
        plt.grid()

        freq_pltFig.canvas.draw()
    elif(chart == 2):
            
        # Redrawing the plots works very good
        plt.figure(gyro_pltFig.number)
        plt.clf()
        plt.plot(gyro_x_readings,label='gy_X')
        plt.plot(gyro_y_readings,label='gy_Y')
        plt.plot(gyro_z_readings,label='gy_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("R/s")
        plt.ylim(-360,360)
        plt.grid()
        gyro_pltFig.canvas.draw()

    elif(chart == 3):
            
        # Redrawing the plots works very good
        plt.figure(mag_pltFig.number)
        plt.clf()
        plt.scatter(mag_x_readings, mag_y_readings, label='mag_Y')

        # plt.plot(mag_x_readings,label='mag_X')
        # plt.plot(mag_y_readings,label='mag_Y')
        # plt.plot(mag_z_readings,label='mag_Z')
        plt.legend(loc='upper left', ncol=3)
        plt.xlabel('Time')
        plt.ylabel("Gauss")
        # plt.xlim(-16000,16000)
        # plt.ylim(-16000,16000)
        plt.xlim(-200,200)
        plt.ylim(-200,200)
        plt.grid()
        mag_pltFig.canvas.draw()

def make_frequency_graph():
    # global frequencies
    # frequencies = copy.deepcopy(accel_z_readings)
    # frequencies = np.abs(scipy.fft.fft(frequencies))**2
    # updateChart(frequency_graph)

    global frequencies
    frequencies = copy.deepcopy(gyro_z_readings)
    frequencies = np.abs(scipy.fft.fft(frequencies))**2
    updateChart(frequency_graph)



drawChart(accel_graph)
drawChart(frequency_graph)
drawChart(gyro_graph)
drawChart(mag_graph)

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

    elif event == "-TIME FREQUENCY-":
        make_frequency_graph()

    elif event == "-THREAD-":
        serial_ports = serial.tools.list_ports.comports()

        serial_ports_str = []
        for s in serial_ports:
            serial_ports_str.append(str(s))
        
        window["-COM LIST-"].update(serial_ports_str)
        
        if(started):
            while serialInst.in_waiting:
                read_message(serialInst.readline().decode('utf'))
            updateChart(accel_graph)
            updateChart(gyro_graph)
            updateChart(mag_graph)
    

window.close()
