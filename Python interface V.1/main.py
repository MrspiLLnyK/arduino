import serial
import time
from tkinter import *
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import ttk

import sys
import glob




def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
  
    return result



def connecting(port_index):
    global aviable_ports, ser, btn3
    serial_loop_counter = 0
    ser = serial.Serial(aviable_ports[port_index], 9600)  # open serial port
    ser.timeout = 1
    print(aviable_ports[port_index])
    while serial_loop_counter != 15:
        try:
            ser.write(b'1229')
            time.sleep(0.3)
            arduino_serial_answer = ser.readline().decode('ascii')
            print(arduino_serial_answer)
            if arduino_serial_answer == '1':
                print("good")
                btn3.configure(bg="green", text="Connected", fg="white")
                break
            else:
                print("bad")
            serial_loop_counter += 1
            time.sleep(0.3)
        except Exception as e:
            print("Serial error")
            btn3.configure(bg="red")
            print(e)
            serial_loop_counter += 1
    
    
color = None
been_clicked = False
drop_down = None

def radio_clicked():
    global color, been_clicked
    
    if been_clicked or selected.get() == 2:
        if selected.get() == 2:
            mode = str(selected.get())
            slider = str(slider_selected.get())
            if len(slider) != 3:
                slider = '0'*(3-len(slider)) + slider
            print(mode + slider)
            i = mode + slider
            ser.write(i.encode())
            time.sleep(0.3)
            

        else:     
            mode = str(selected.get())
            slider = str(slider_selected.get())
            if len(slider) != 3:
                slider = '0'*(3-len(slider)) + slider
            print(mode + slider + color)
            i = mode + slider + color
            ser.write(i.encode())
            time.sleep(0.3)
    else:
        messagebox.showerror("Title", "Firstly choise LED color")

    
    

def choose_color():
    global color, been_clicked
    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title ="Choose color")
    
    

    if color_code[0] is None:
        pass   
    else:
        red = str(int(color_code[0][0]))
        if len(red) != 3:
            red = '0'*(3- len(red)) + red

        green = str(int(color_code[0][1]))
        if len(green) != 3:
            green = '0'*(3- len(green)) + green

        blue = str(int(color_code[0][2]))
        if len(blue) != 3:
            blue = '0'*(3- len(blue)) + blue

        color = red + green + blue
        been_clicked = True   

def connect_button():
    global drop_down
    print(drop_down.current())
    connecting(drop_down.current())
      
window = Tk()
window.title('LED')
window.geometry('400x250')  
selected = IntVar()
slider_selected = IntVar()
aviable_ports = serial_ports()

rad1 = Radiobutton(window, text='Дихання', value=0, variable=selected)  
rad2 = Radiobutton(window, text='Статичний', value=1, variable=selected)  
rad3 = Radiobutton(window, text='Колесо', value=2, variable=selected)  
drop_down = ttk.Combobox(window, values=aviable_ports)
try:
    drop_down.current(1)
except:
    drop_down.current(0)
btn = Button(window, text="click", command=radio_clicked)
btn2 = Button(window, text="color", command=choose_color)
btn3 = Button(window, text="Connect", command=connect_button)

w = Scale(window, from_=0, to=100, orient=HORIZONTAL, variable=slider_selected)
  

w.grid(column=1, row=6)

btn.grid(column=1, row=7)
btn2.grid(column=1, row=8)
btn3.grid(column=1, row = 0)

rad1.grid(column=0, row=4)  
rad2.grid(column=1, row=4)  
rad3.grid(column=2, row=4) 

drop_down.grid(column = 0, row=0)
window.mainloop()

# ser = serial.Serial('COM9', 9600)  # open serial port
# ser.timeout = 1

# # while True:
#     # i = input('ON/OFF: ').strip()
#     # print(i)      # check which port was really used
#     # print(ser.readline().decode('ascii'))
    
#     # if i == 'asd':
#     #     p = 1255
#     #     # ser.write(p.encode())
#     #     ser.write(b'1259')
#     #     time.sleep(2)
#     #     # print(ser.readline().decode('ascii'))
#     # else:
#     #     ser.write(i.encode())
#     #     time.sleep(5)
#     #     print(ser.readline().decode('ascii'))


# while True:
#     i = input("ON/OFF: ").strip()
#     ser.write(i.encode())
#     time.sleep(1)
#     print(i.encode())
#     print(ser.readline().decode('ascii'))
#     asd = ser.readline().decode('ascii')
#     print(type(asd))
    
    


# ser.close()

