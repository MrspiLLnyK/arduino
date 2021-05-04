from tkinter import *
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import ttk
import serial
import time
import glob
import math
import sys



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
    global aviable_ports, ser, btn2, conected
    serial_loop_counter = 0
    aviable_ports = serial_ports()
    try:
        ser = serial.Serial(aviable_ports[port_index], 1000000)
        ser.timeout = 1
        while serial_loop_counter != 15: 
            time.sleep(0.1)
            ser.write(b'a;')
            time.sleep(0.1)
            arduino_serial_answer = ser.readline().decode('ascii')
            if arduino_serial_answer == '1':
                btn2.configure(bg="green", text="Connected", fg="white")
                conected = True
                break
            serial_loop_counter += 1
            time.sleep(0.1)

    except Exception as e:
        messagebox.showerror("Error", "Couldn't opden {} port.\n{}".format(aviable_ports[port_index], e))
        btn2.configure(bg="red")

def connect_button():
    global drop_down
    connecting(drop_down.current())

def protocol_construck(*data_for_construck , separator = ",", terminator = ";"):
    """
    form (0,123,56) to "0,123,56;"

    """
    return separator.join([ str(i) for i in data_for_construck]) + terminator    
   
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))   

def arduino_map(value, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)  
    new_range = (new_max - new_min)  
    new_value = (((value - old_min) * new_range) / old_range) + new_min    
    return int(new_value)

def update_drop_down():
    global btn2, drop_down
    drop_down["values"] = serial_ports()
    btn2.configure(bg="white", text="Connect", fg="black")
    
def breath():
    global breath_return, degr, color_code, allow_breath, ser, slider_selected, conected, restart_func
    if not allow_breath or restart_func:
        restart_func = False
        return
    degr +=1
    sin = 0.5 * math.sin(math.radians(degr)) + 0.5
    breath_return = protocol_construck(math.floor(sin*color_code[0]), math.floor(sin*color_code[1]), math.floor(sin*color_code[2]))
    try:
        print("breath: " + breath_return)
        ser.write(breath_return.encode())
    except Exception as e:
        messagebox.showerror("Error", e)  
        btn2.configure(bg="white", text="Connect", fg="black")
        conected = False  
        return
    window.after(arduino_map(slider_selected.get(), 0, 100, 130, 10), breath)
    
def static():
    global ser, slider_selected, color_code, btn2, conected, allow_staic, restart_func
    if not allow_staic or restart_func:
        restart_func = False
        return
    try:
        print('Static: ' + str(protocol_construck(int(color_code[0]*(slider_selected.get()/100)), int(color_code[1]*(slider_selected.get()/100)), int(color_code[2]*(slider_selected.get()/100)))))
        ser.write(protocol_construck(int(color_code[0]*(slider_selected.get()/100)), int(color_code[1]*(slider_selected.get()/100)), int(color_code[2]*(slider_selected.get()/100))).encode())
    except Exception as e:
        messagebox.showerror("Error", e)
        btn2.configure(bg="white", text="Connect", fg="black")
        conected = False    
        return
        
    window.after(50, static)

def set_led_hsv():
    global h, s, v, hsv_return, ser, selected_radio, allow_breath, slider_selected, btn2, conected, restart_func
    if not allow_hsv or restart_func:
        restart_func = False
        return
    
        
    if h == 360:
        h = 0

    r=0
    g=0
    b=0
    i = int(h/60)
    f = h/60 - i
    pv = v * (1 - s)
    qv = v * (1 - s*f)
    tv = v * (1 - s * (1 - f))

    if i == 0:
        r = v
        g = tv
        b = pv    
    elif i == 1:
        r = qv
        g = v
        b = pv
    elif i == 2:
        r = pv
        g = v
        b = tv
    elif i == 3:
        r = pv
        g = qv
        b = v
    elif i == 4:
        r = tv
        g = pv
        b = v
    elif i == 5:
        r = v
        g = pv
        b = qv
    
    h += 1
    hsv_return = protocol_construck(math.floor(constrain(r*255, 0, 255)), math.floor(constrain(g*255, 0, 255)), math.floor(constrain(b*255, 0, 255)))
    
    try:
        ser.write(hsv_return.encode()) 
        print("hsv: " + str(hsv_return))   
    except Exception as e:
        messagebox.showerror("Error", e)
        btn2.configure(bg="white", text="Connect", fg="black")
        conected = False  
        return
    window.after(arduino_map(slider_selected.get(), 0, 100, 100, 10), set_led_hsv)

def radio_clicked():
    global breath_return, degr, color_code, h, s, v, conected, allow_breath, allow_hsv, allow_staic, restart_func, selected_radio_list
    if len(selected_radio_list) > 1:
        selected_radio_list.pop(0)

    selected_radio_list.append(selected_radio.get())
    if selected_radio_list[len(selected_radio_list) - 1] == selected_radio_list[len(selected_radio_list) - 2] and len(selected_radio_list) > 1:
        restart_func = not restart_func
    
    if selected_radio.get() == 0 and conected:
        allow_breath = True
        allow_staic = False
        allow_hsv = False
        degr = 0
        color_code = colorchooser.askcolor(title ="Choose color")[0]
        if color_code is None:
            pass
        else:    
            breath() 
    elif selected_radio.get() == 1 and conected:
        allow_breath = False
        allow_staic = True
        allow_hsv = False
        color_code = colorchooser.askcolor(title ="Choose color")[0]   
        if color_code is None:
            pass
        else:    
            static()
    elif selected_radio.get() == 2 and conected:
        allow_breath = False
        allow_staic = False
        allow_hsv = True
        set_led_hsv()           
    else:
        pass

    
 
window = Tk()
window.title('LED')
window.geometry('400x250')

selected_radio = IntVar()
selected_radio_list = []

slider_selected = IntVar()
aviable_ports = serial_ports()
conected = False
allow_breath = False
allow_staic = False
allow_hsv = False
restart_func = False
drop_down = None
breath_return = None
hsv_return = None
ser = None
degr = 0
ser = None
color_code = []
h = 0
s = 1
v = 1



rad1 = Radiobutton(window, text='Дихання', value=0, variable=selected_radio)  
rad2 = Radiobutton(window, text='Статичний', value=1, variable=selected_radio)  
rad3 = Radiobutton(window, text='Колесо', value=2, variable=selected_radio)  
btn1 = Button(window, text="click", command=radio_clicked)
btn2 = Button(window, text="Connect", command=connect_button)
slider = Scale(window, from_=0, to=100, orient=HORIZONTAL, variable=slider_selected)
drop_down = ttk.Combobox(window, values=aviable_ports, postcommand=update_drop_down)


try:
    drop_down.current(1)
except:
    drop_down.current(0)

  
slider.grid(column=1, row=6)
btn1.grid(column=1, row=7)
btn2.grid(column=1, row=0)
rad1.grid(column=0, row=4)  
rad2.grid(column=1, row=4)  
rad3.grid(column=2, row=4) 
drop_down.grid(column=0, row=0)

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

