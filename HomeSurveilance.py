from tkinter import *
import numpy as np

import pickle
import sys
import math
import os
import numpy as np
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

''' Path to where the Objects.txt, LOGS.txt and Homesurveilance.py files are located. '''
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

object_counter = 0
wall_counter = 0
door_counter = 0
window_counter = 0
light_counter = 0
gpio_counter = -1
object_id = "-1"
object_tags = []
objects_file = {}
edit_allowed = True

''' Edit this list to use with other models of Raspberry PI '''
gpio_list = ['None','GPIO2','GPIO3','GPIO4','GPIO5',
             'GPIO6','GPIO7','GPIO8','GPIO12',
             'GPIO13','GPIO14','GPIO15','GPIO16',
             'GPIO17','GPIO18','GPIO19','GPIO20',
             'GPIO21','GPIO22','GPIO23','GPIO24',
             'GPIO25','GPIO26','GPIO27']

def interupt(pin):
    ''' Function that interupts on falling and rising edges and deals with the object accordingly. '''
    ''' Future edit note. Can remove this function and plug directly into activate_object(). '''
    
    if GPIO.input(pin) == GPIO.HIGH:
        activate_object(pin)
    elif GPIO.input(pin) == GPIO.LOW:
        activate_object(pin)


def initialize_pins():
    ''' Initializes each pin as an input with rising/falling interupts to an object that is selected. '''
    
    pin_num = 0

    for objects in list(layout.find_all()):
        tags = list(layout.gettags(objects))

        try:
            if 'GPIO' in tags[3] and ('dc' in tags[1] or 'lc' in tags[1] or 'vb' in tags[1]):
                pin_num = tags[3][4:]
                print("Setting pin " + str(tags[3]) + " as input pin for " + str(tags[1]))
                GPIO.setup( int(pin_num), GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
                GPIO.add_event_detect(int(pin_num), GPIO.BOTH, callback = interupt, bouncetime = 300)
                
        except IndexError:
            pass

''' Was meant to work with a 240x320 LCD display. Can adjust to any size desired. '''
canvas_sizex = 240
canvas_sizey = 320
window_sizex = 320
window_sizey = 384


root = Tk()
root.title("Surveillance")
root.geometry(str(window_sizex) + "x" + str(window_sizey))
layout = Canvas(root, width=canvas_sizex, height=canvas_sizey, bg="black")
layout.place(x=0,
             y=0)

pins = StringVar(root)
pins.set(gpio_list[0])

def add_wall():
    ''' Wall ID is given as in object_tags - 'w1'                  [0]
                                           - 'wc1'                 [1]
                                           - 'horizontal/vertical' [2]
    Use object_id to get tags of the objects
    Similar format applies to door, window and light objects
    ''' 
    global object_counter
    global wall_counter
    global object_id
    global object_tags

    ''' Counters keep track of all current wall_objects and total objects on the layout. '''
    wall_counter = wall_counter + 1
    object_counter = object_counter + 1
    wall_list = []
    exist_wall_counter = 1

    x = 120
    y = 160

    ''' Get all the current wall_objects on the layout '''
    for walls in list(layout.find_all()):
        if list(layout.gettags(walls))[1][0:2] == 'wc':
            wall_list.append(int(list(layout.gettags(walls))[1][2:]))

    if len(wall_list) == 0:
        wall_counter = 1

    ''' Check current wall_id's so that a new wall with a consecutive ID is created. Prevent gaps in the ID's '''
    for walls in sorted(wall_list):
        if exist_wall_counter == int(walls):
            #print("w" + str(exist_wall_counter) + " exist")
            exist_wall_counter = exist_wall_counter + 1
            wall_counter = exist_wall_counter
        else:
            #print("w" + str(exist_wall_counter) + " no exist")
            wall_counter = exist_wall_counter
            #print("Adding " + "w" + str(exist_wall_counter))
            break

    wall_coords = [x - 20,
                   y,
                   x + 20,
                   y]

    wall_id = "w" + str(wall_counter)
    wall_idc = "wc" + str(wall_counter)

    layout.create_line(wall_coords,
                       fill="White",
                       width=2,
                       tags=[wall_id, wall_idc, 'horizontal'])

    object_id = wall_id
    print()
    print("Added Wall:")
    print("Object ID:  " + str(object_id))
    object_tags = list(layout.gettags(object_id))
    print("Object tags: " + str(object_tags))
    layout.tag_raise(object_id)

    update_gui()


def add_door():
    '''
      Each door object has three components  to represent door on layout.
      Main door ID is represented in object_tags - 'd1'                  [0]
                                                 - 'dc1'                 [1]
                                                 - 'open/closed'         [2]
                                                 - 'pin assigned'        [3]
                                                 - 'horizontal/vertical' [4]
                                                 - 'time activated'      [5]
      Sub components ID's (left piece)  - 'd1'  [0]
                                        - 'dl1' [1]
                          (right piece) - 'd1' [0]
                                        - 'dr1' [1]
    Use object_id to get tags of the objects
    Similar format applies to window and light objects
    ''' 
    global object_counter
    global door_counter
    global object_id
    global object_tags
    global gpio_list
    global gpio_counter

    door_counter = door_counter + 1
    object_counter = object_counter + 1
    gpio_counter = gpio_counter + 1
    door_list = []
    exist_door_counter = 1

    x = 120
    y = 160

    for doors in list(layout.find_all()):
        if list(layout.gettags(doors))[1][0:2] == 'dc':
            door_list.append(int(list(layout.gettags(doors))[1][2:]))

    if len(door_list) == 0:
        door_counter = 1

    for doors in sorted(door_list):
        if exist_door_counter == int(doors):
            exist_door_counter = exist_door_counter + 1
            door_counter = exist_door_counter
        else:
            door_counter = exist_door_counter
            break

    doorl_coords = [x - 10,
                    y - 4,
                    x - 10,
                    y + 4]
    doorc_coords = [x - 10,
                    y,
                    x + 10,
                    y]
    doorr_coords = [x + 10,
                    y - 4,
                    x + 10,
                    y + 4]

    door_idl = "dl" + str(door_counter)
    door_idc = "dc" + str(door_counter)
    door_idr = "dr" + str(door_counter)
    door_id = "d" + str(door_counter)

    layout.create_line(doorc_coords,
                       fill="White",
                       width=2,
                       tags=[door_id, door_idc, 'closed', gpio_list[gpio_counter], 'horizontal', 'N/A'])
    layout.create_line(doorl_coords,
                       fill="White",
                       width=2,
                       tags=[door_id, door_idl])
    layout.create_line(doorr_coords,
                       fill="White",
                       width=2,
                       tags=[door_id, door_idr])

    object_id = door_id
    print()
    print("Added Door:")
    print("Object ID:  " + str(object_id))
    object_tags = list(layout.gettags(object_id))
    print("Object tags: " + str(object_tags))
    layout.tag_raise(object_id)
    update_gui()


def add_window():
    '''
      Each door object has four components  to represent window on layout.
      Main window ID is represented in object_tags - 'v1'                  [0]
                                                   - 'vb1'                 [1]
                                                   - 'open/closed'         [2]
                                                   - 'pin assigned'        [3]
                                                   - 'horizontal/vertical' [4]
                                                   - 'time activated'      [5]
      Sub components ID's (left piece)  - 'v1'  [0]
                                        - 'vl1' [1]
                          (right piece) - 'v1' [0]
                                        - 'vr1' [1]
                          (top piece)   - 'v1' [0]
                                        - 'vt1' [1]
    Use object_id to get tags of the objects
    ''' 
    global object_counter
    global window_counter
    global object_id
    global object_tags
    global gpio_list
    global gpio_counter

    object_counter = object_counter + 1
    window_counter = window_counter + 1
    gpio_counter = gpio_counter + 1
    exist_window_counter = 1
    window_list = []

    x = 120
    y = 160

    for windows in list(layout.find_all()):
        if list(layout.gettags(windows))[1][0:2] == 'vb':
            window_list.append(int(list(layout.gettags(windows))[1][2:]))

    if len(window_list) == 0:
        window_counter = 1

    for windows in sorted(window_list):
        if exist_window_counter == int(windows):
            exist_window_counter = exist_window_counter + 1
            window_counter = exist_window_counter
        else:
            window_counter = exist_window_counter
            break

    window_idl = "vl" + str(window_counter)
    window_idt = "vt" + str(window_counter)
    window_idr = "vr" + str(window_counter)
    window_idb = "vb" + str(window_counter)
    window_id = "v" + str(window_counter)


    windowl_coords = [x - 12,
                      y - 4,
                      x - 12,
                      y + 4]
    windowt_coords = [x - 12,
                      y - 2,
                      x + 12,
                      y - 2]
    windowr_coords = [x + 12,
                      y - 4,
                      x + 12,
                      y + 4]
    windowb_coords = [x - 12,
                      y,
                      x + 12,
                      y]

    layout.create_line(windowb_coords,
                       fill="White",
                       width=1,
                       tags=[window_id, window_idb, 'closed', gpio_list[gpio_counter], 'horizontal', 'N/A'])
    layout.create_line(windowt_coords,
                       fill="White",
                       width=1,
                       tags=[window_id, window_idt])
    layout.create_line(windowl_coords,
                       fill="White",
                       width=2,
                       tags=[window_id, window_idl])
    layout.create_line(windowr_coords,
                       fill="White",
                       width=2,
                       tags=[window_id, window_idr])

    object_id = window_id
    print()
    print("Added Window:")
    print("Object ID:  " + str(object_id))
    object_tags = list(layout.gettags(object_id))
    print("Object tags: " + str(object_tags))
    layout.tag_raise(object_id)
    update_gui()


def add_light():
  '''
      Each light object has one component  to represent light on layout.
      Light ID is represented in object_tags - 'l1'                  [0]
                                             - 'lc1'                 [1]
                                             - 'off/on'              [2]
                                             - 'pin assigned'        [3]
                                             - 'time activated'      [4]
    Use object_id to get tags of the objects
    ''' 
    global object_counter
    global light_counter
    global object_id
    global object_tags
    global gpio_list
    global gpio_counter

    object_counter = object_counter + 1
    light_counter = light_counter + 1
    gpio_counter = gpio_counter + 1
    light_list = []
    exist_light_counter = 1

    x = 120
    y = 160

    for lights in list(layout.find_all()):
        if list(layout.gettags(lights))[1][0:2] == 'lc':
            light_list.append(int(list(layout.gettags(lights))[1][2:]))

    if len(light_list) == 0:
        light_counter = 1

    for lights in sorted(light_list):
        if (exist_light_counter == int(lights)):
            exist_light_counter = exist_light_counter + 1
            light_counter = exist_light_counter
        else:
            light_counter = exist_light_counter
            break


    light_idc = "lc" + str(light_counter)
    light_id = "l" + str(light_counter)

    lightc_coords = [x - 6,
                     y - 6,
                     x + 6,
                     y + 6]
    layout.create_oval(lightc_coords,
                       outline="Cyan",
                       fill="Black",
                       width=1,
                       tags=[light_id, light_idc, 'off', gpio_list[gpio_counter], 'N/A'])

    object_id = light_id
    print()
    print("Added Light:")
    print("Object ID:  " + str(object_id))
    object_tags = list(layout.gettags(object_id))
    print("Object tags: " + str(object_tags))
    layout.tag_raise(object_id)
    update_gui()


def delete_object():
  ''' Straight forward function, gets id and removes from layout. '''
    global object_counter
    global object_id
    global gpio_counter

    print("Deleted object ID: " + str(object_id))

    if "w" or "v" or "l" in object_id:
        if gpio_counter >= 0:
            gpio_counter = gpio_counter - 1

    layout.delete(object_id)
    object_id = "-1"
    if (object_counter != 0):
        object_counter = object_counter - 1

    update_gui()


def motion(event):
  ''' Get position of mouse on the layout '''
    global object_id
    global canvas_sizex
    global canvas_sizey

    abs_coord_x = root.winfo_pointerx() - root.winfo_rootx()
    abs_coord_y = root.winfo_pointery() - root.winfo_rooty()
    if (abs_coord_y <= canvas_sizey and abs_coord_x <= canvas_sizex):
        xy_label.config(text=str(abs_coord_x) + "," + str(abs_coord_y))

    update_gui()

def mouse_clicked(event):
  ''' Checks whether mouse clicked was on top of an object on the layout and selects the object '''
    global edit_allowed
    global object_id
    global object_tags

    if edit_allowed:
        try:
            object_id = list(layout.gettags(event.widget.find_withtag("current")))[0]
        except (IndexError, AttributeError):
            pass
    else:
            object_id = "-1"

    print()
    print("Mouse clicked:")
    print("Object ID:  " + str(object_id))
    object_tags = list(layout.gettags(object_id))
    print("Object tags: " + str(object_tags))

    update_gui()

def move_object(event):
    global object_id

    if "w" in str(object_id):
        try:
            move_wall(event)
        except IndexError:
            print()

    if "d" in str(object_id):
        try:
            move_door(event)
        except IndexError:
            print()

    if "v" in str(object_id):
        try:
            move_window(event)
        except IndexError:
            print()

    if "l" in str(object_id):
        try:
            move_light(event)
        except IndexError:
            print()

    update_gui()

def move_wall(event):
    object_position = list(layout.coords(object_id))
    x_len = object_position[2] - object_position[0]
    y_len = object_position[3] - object_position[1]

    if (event.x > object_position[0] - 5):
        if (event.x < object_position[2] + 5):
            if (event.y > object_position[1] - 5):
                if (event.y < object_position[3] + 5):
                    layout.coords(object_id,
                                  event.x - x_len / 2,
                                  event.y - y_len / 2,
                                  event.x + x_len / 2,
                                  event.y + y_len / 2)
    update_gui()

def move_door(event):
    global object_id
    global object_tags

    door_num = object_id[1:len(object_id)]

    centre_piece = list(layout.gettags(list(layout.find_withtag("dc" + str(door_num)))[0]))[1]
    left_piece = list(layout.gettags(list(layout.find_withtag("dl" + str(door_num)))[0]))[1]
    right_piece = list(layout.gettags(list(layout.find_withtag("dr" + str(door_num)))[0]))[1]

    object_position = list(layout.coords(centre_piece))
    x_len = object_position[2] - object_position[0]
    y_len = object_position[3] - object_position[1]

    if (event.x > object_position[0] - 5):
        if (event.x < object_position[2] + 5):
            if (event.y > object_position[1] - 5):
                if (event.y < object_position[3] + 5):
                    if (object_tags[4] == 'vertical'):
                        layout.coords(centre_piece,
                                      event.x - int(x_len / 2),
                                      event.y - int(y_len / 2),
                                      event.x + int(x_len / 2),
                                      event.y + int(y_len / 2))
                        centre_coords = object_position
                        layout.coords(left_piece,
                                      centre_coords[0] - 4,
                                      centre_coords[1],
                                      centre_coords[0] + 4,
                                      centre_coords[1])
                        layout.coords(right_piece,
                                      centre_coords[0] - 4,
                                      centre_coords[1] + 20,
                                      centre_coords[0] + 4,
                                      centre_coords[1] + 20)

                    elif (object_tags[4] == 'horizontal'):
                        layout.coords(centre_piece,
                                      event.x - int(x_len / 2),
                                      event.y - int(y_len / 2),
                                      event.x + int(x_len / 2),
                                      event.y + int(y_len / 2))
                        centre_coords = object_position
                        layout.coords(left_piece,
                                      centre_coords[0],
                                      centre_coords[1] - 4,
                                      centre_coords[0],
                                      centre_coords[1] + 4)
                        layout.coords(right_piece,
                                      centre_coords[0] + 20,
                                      centre_coords[1] - 4,
                                      centre_coords[0] + 20,
                                      centre_coords[1] + 4)

    update_gui()

def move_window(event):
    global object_id
    global object_tags

    window_num = object_id[1:len(object_id)]

    base_piece = list(layout.gettags(list(layout.find_withtag("vb" + str(window_num)))[0]))[1]
    left_piece = list(layout.gettags(list(layout.find_withtag("vl" + str(window_num)))[0]))[1]
    right_piece = list(layout.gettags(list(layout.find_withtag("vr" + str(window_num)))[0]))[1]
    top_piece = list(layout.gettags(list(layout.find_withtag("vt" + str(window_num)))[0]))[1]

    object_position = list(layout.coords(base_piece))
    x_len = object_position[2] - object_position[0]
    y_len = object_position[3] - object_position[1]

    if (event.x > object_position[0] - 5):
        if (event.x < object_position[2] + 5):
            if (event.y > object_position[1] - 5):
                if (event.y < object_position[3] + 5):
                    if (object_tags[4] == 'vertical'):
                        layout.coords(base_piece,
                                      event.x - int(x_len / 2),
                                      event.y - int(y_len / 2),
                                      event.x + int(x_len / 2),
                                      event.y + int(y_len / 2))

                        base_coords = object_position
                        layout.coords(top_piece,
                                      event.x - int(x_len / 2) - 2,
                                      event.y - int(y_len / 2),
                                      event.x + int(x_len / 2) - 2,
                                      event.y + int(y_len / 2))
                        layout.coords(left_piece,
                                      base_coords[0] - 4,
                                      base_coords[1],
                                      base_coords[0] + 4,
                                      base_coords[1])
                        layout.coords(right_piece,
                                      base_coords[0] - 4,
                                      base_coords[1] + 24,
                                      base_coords[0] + 4,
                                      base_coords[1] + 24)
                    elif (object_tags[4] == 'horizontal'):
                        layout.coords(base_piece,
                                      event.x - int(x_len / 2),
                                      event.y - int(y_len / 2),
                                      event.x + int(x_len / 2),
                                      event.y + int(y_len / 2))

                        base_coords = object_position
                        layout.coords(top_piece,
                                      event.x - int(x_len / 2),
                                      event.y - int(y_len / 2) - 2,
                                      event.x + int(x_len / 2),
                                      event.y + int(y_len / 2) - 2)
                        layout.coords(left_piece,
                                      base_coords[0],
                                      base_coords[1] - 4,
                                      base_coords[0],
                                      base_coords[1] + 4)
                        layout.coords(right_piece,
                                      base_coords[0] + 24,
                                      base_coords[1] - 4,
                                      base_coords[0] + 24,
                                      base_coords[1] + 4)


def move_light(event):
    object_position = list(layout.coords(object_id))
    x_len = object_position[2] - object_position[0]
    y_len = object_position[3] - object_position[1]

    if (event.x > object_position[0] - 5):
        if (event.x < object_position[2] + 5):
            if (event.y > object_position[1] - 5):
                if (event.y < object_position[3] + 5):
                    layout.coords(object_id,
                                  event.x - x_len / 2,
                                  event.y - y_len / 2,
                                  event.x + x_len / 2,
                                  event.y + y_len / 2)

def increase_size():
    global object_id
    global object_tags

    object_position = list(layout.coords(object_id))
    if (object_tags[2] == 'vertical'):
        layout.coords(object_id,
                      object_position[0],
                      object_position[1] - 2,
                      object_position[2],
                      object_position[3] + 2)
    elif (object_tags[2] == 'horizontal'):
        layout.coords(object_id,
                      object_position[0] - 2,
                      object_position[1],
                      object_position[2] + 2,
                      object_position[3])
    update_gui()

def decrease_size():
    global object_id
    global object_tags

    object_position = list(layout.coords(object_id))
    if (object_tags[2] == 'vertical'):
        layout.coords(object_id,
                      object_position[0],
                      object_position[1] + 2,
                      object_position[2],
                      object_position[3] - 2)
    elif (object_tags[2] == 'horizontal'):
        layout.coords(object_id,
                      object_position[0] + 2,
                      object_position[1],
                      object_position[2] - 2,
                      object_position[3])

    update_gui()

def rotate_object():
    global object_id
    global object_tags

    print()
    print("Rotating object:")
    print("Object ID:  " + str(object_id))

    if "w" in str(object_id):
        object_position = list(layout.coords(object_id))
        #object_tags = list(layout.gettags(object_id))

        layout.coords(object_id, rotate_line(object_position))

        if (object_tags[2] == 'horizontal'):
            layout.dtag(object_id, 'horizontal')
            layout.addtag_withtag('vertical', object_id)
        elif (object_tags[2] == 'vertical'):
            layout.dtag(object_id, 'vertical')
            layout.addtag_withtag('horizontal', object_id)

    elif "d" in str(object_id):
        door_num = object_id[1:len(object_id)]

        centre_piece = list(layout.gettags(list(layout.find_withtag("dc" + str(door_num)))[0]))[1]
        left_piece = list(layout.gettags(list(layout.find_withtag("dl" + str(door_num)))[0]))[1]
        right_piece = list(layout.gettags(list(layout.find_withtag("dr" + str(door_num)))[0]))[1]

        centre_coords = list(layout.coords(centre_piece))
        left_coords = list(layout.coords(left_piece))
        right_coords = list(layout.coords(right_piece))

        layout.coords(centre_piece, rotate_line(centre_coords))
        layout.coords(left_piece, rotate_line(left_coords))
        layout.coords(right_piece, rotate_line(right_coords))

        left_coords = list(layout.coords(left_piece))
        right_coords = list(layout.coords(right_piece))
        cen_coords = list(layout.coords(centre_piece))

        if (object_tags[4] == 'horizontal'):

            layout.dtag(object_id, object_tags[5])
            layout.dtag(object_id, 'horizontal')
            layout.addtag_withtag('vertical', object_id)
            layout.addtag_withtag(object_tags[5], object_id)
            
        elif (object_tags[4] == 'vertical'):
            
            layout.dtag(object_id, object_tags[5])
            layout.dtag(object_id, 'vertical')
            layout.addtag_withtag('horizontal', object_id)
            layout.addtag_withtag(object_tags[5], object_id)
            

        if (object_tags[4] == 'vertical'):
            side_len = np.abs(left_coords[3] - left_coords[1])
            main_cen = np.abs(cen_coords[3] + cen_coords[1]) / 2

            layout.coords(left_piece,
                          cen_coords[0],
                          main_cen - side_len / 2,
                          cen_coords[0],
                          main_cen + side_len / 2)
            layout.coords(right_piece,
                          cen_coords[2],
                          main_cen - side_len / 2,
                          cen_coords[2],
                          main_cen + side_len / 2)
        elif (object_tags[4] == 'horizontal'):
            side_len = np.abs(left_coords[2] - left_coords[0])
            main_cen = np.abs(cen_coords[2] + cen_coords[0]) / 2

            layout.coords(left_piece,
                          main_cen - side_len / 2,
                          cen_coords[1],
                          main_cen + side_len / 2,
                          cen_coords[1])
            layout.coords(right_piece,
                          main_cen - side_len / 2,
                          cen_coords[3],
                          main_cen + side_len / 2,
                          cen_coords[3])

    elif "v" in str(object_id):
        window_num = object_id[1:len(object_id)]
        object_tags = list(layout.gettags(object_id))

        centre_piece = list(layout.gettags(list(layout.find_withtag("vb" + str(window_num)))[0]))[1]
        left_piece = list(layout.gettags(list(layout.find_withtag("vl" + str(window_num)))[0]))[1]
        right_piece = list(layout.gettags(list(layout.find_withtag("vr" + str(window_num)))[0]))[1]
        top_piece = list(layout.gettags(list(layout.find_withtag("vt" + str(window_num)))[0]))[1]

        centre_coords = list(layout.coords(centre_piece))
        left_coords = list(layout.coords(left_piece))
        right_coords = list(layout.coords(right_piece))

        layout.coords(centre_piece, rotate_line(centre_coords))
        layout.coords(left_piece, rotate_line(left_coords))
        layout.coords(right_piece, rotate_line(right_coords))

        left_coords = list(layout.coords(left_piece))
        right_coords = list(layout.coords(right_piece))
        cen_coords = list(layout.coords(centre_piece))

        if (object_tags[4] == 'horizontal'):

            layout.dtag(object_id, object_tags[5])
            layout.dtag(object_id, 'horizontal')
            layout.addtag_withtag('vertical', object_id)
            layout.addtag_withtag(object_tags[5], object_id)

        elif (object_tags[4] == 'vertical'):

            layout.dtag(object_id, object_tags[5])
            layout.dtag(object_id, 'vertical')
            layout.addtag_withtag('horizontal', object_id)
            layout.addtag_withtag(object_tags[5], object_id)

        if (object_tags[4] == 'vertical'):
            side_len = np.abs(left_coords[3] - left_coords[1])
            main_cen = np.abs(cen_coords[3] + cen_coords[1]) / 2

            layout.coords(left_piece,
                          cen_coords[0],
                          main_cen - side_len / 2,
                          cen_coords[0],
                          main_cen + side_len / 2)
            layout.coords(right_piece,
                          cen_coords[2],
                          main_cen - side_len / 2,
                          cen_coords[2],
                          main_cen + side_len / 2)
            layout.coords(top_piece,
                          cen_coords[0],
                          cen_coords[1] - 2,
                          cen_coords[2],
                          cen_coords[3] - 2)
        elif (object_tags[4] == 'horizontal'):
            side_len = np.abs(left_coords[2] - left_coords[0])
            main_cen = np.abs(cen_coords[2] + cen_coords[0]) / 2

            layout.coords(left_piece,
                          main_cen - side_len / 2,
                          cen_coords[1],
                          main_cen + side_len / 2,
                          cen_coords[1])
            layout.coords(right_piece,
                          main_cen - side_len / 2,
                          cen_coords[3],
                          main_cen + side_len / 2,
                          cen_coords[3])
            layout.coords(top_piece,
                          cen_coords[0] - 2,
                          cen_coords[1],
                          cen_coords[2] - 2,
                          cen_coords[3])

    print("Object tags: " + str(object_tags))
    update_gui()

def rotate_line(coords):
    xlen = np.abs(coords[2] - coords[0])
    ylen = np.abs(coords[3] - coords[1])
    xcen = np.abs(coords[2] + coords[0]) / 2
    ycen = np.abs(coords[3] + coords[1]) / 2

    coords = [xcen - ylen / 2,
              ycen - xlen / 2,
              xcen + ylen / 2,
              ycen + xlen / 2]

    return coords

def copy_object():
    global object_id
    global object_tags
    global object_counter
    global wall_counter

    centre_x = 120
    centre_y = 160

    if "w" in str(object_id):
        object_coords = list(layout.coords(object_id))
        xlen = np.abs(object_coords[2] - object_coords[0])
        ylen = np.abs(object_coords[3] - object_coords[1])

        wall_counter = wall_counter + 1
        object_counter = object_counter + 1
        wall_list = []
        exist_wall_counter = 1

        x = 120
        y = 160

        for walls in list(layout.find_all()):
            if (list(layout.gettags(walls))[1][0:2] == 'wc'):
                wall_list.append(int(list(layout.gettags(walls))[1][2:]))
        if (len(wall_list) == 0):
            wall_counter = 1

        for walls in sorted(wall_list):
            if (exist_wall_counter == int(walls)):
                exist_wall_counter = exist_wall_counter + 1
                wall_counter = exist_wall_counter
            else:
                wall_counter = exist_wall_counter
                break

        wall_id = 'w' + str(wall_counter)
        wall_idc = 'wc' + str(wall_counter)

        layout.create_line(centre_x - xlen / 2,
                           centre_y - ylen / 2,
                           centre_x + xlen / 2,
                           centre_y + ylen / 2,
                           fill="White",
                           width=2,
                           tags= [wall_id, wall_idc, object_tags[2]])

        object_id = wall_id
        print()
        print("Copying Wall:")
        print("Object ID:  " + str(object_id))
        object_tags = list(layout.gettags(object_id))
        print("Object tags: " + str(object_tags))
        layout.tag_raise(object_id)

    '''
    Not adding copying for doors as they all have standard size that cant
    be changed
    '''
    update_gui()

def update_gui():
    global object_id
    global object_counter
    global object_tags

    object_tags = list(layout.gettags(object_id))

    if object_id == "-1":
        objectid_label.config(text="ID: None")
    else:
        if 'w' in object_id:
            print("update walls")
            objectid_label.config(text="ID: " + str(object_id))
            objectactivity_label.config(text = "Last activity: N/A")
        elif 'l' in object_id:
            print("update lights")
            objectid_label.config(text="ID: " + str(object_id) + ' - ' + str(object_tags[2]) + " (" +  str(object_tags[3]) + ")")
            objectactivity_label.config(text = "Last activity: " + str(object_tags[4]))    
        else:
            print("update doors and windows")
            print(object_tags)
            objectid_label.config(text="ID: " + str(object_id) + ' - ' + str(object_tags[2]) + " (" +  str(object_tags[3]) + ")")
            objectactivity_label.config(text = "Last activity: " + str(object_tags[5]))

    ''' Selection Check '''
    for objects in list(layout.find_all()):
        tags = list(layout.gettags((objects)))
        if (tags[0] != object_id):
            if (tags[0][0] == "l"):
                if (tags[2] == 'on'):
                    layout.itemconfig(objects, fill="Cyan", outline="Cyan")
                else:
                    layout.itemconfig(objects, fill= "Black", outline ="Cyan")
            else:
                layout.itemconfig(objects, fill="Cyan")

        else:
            if (tags[0][0] == "l"):
                if (tags[2] == 'on'):
                    layout.itemconfig(objects, fill="White", outline="White")
                else:
                    layout.itemconfig(objects, fill ="Black", outline ="White")
            else:
                layout.itemconfig(objects, fill="White")
        '''
        if (layout.gettags(objects)[0][0] == "l"):
            if list(layout.gettags(objects))[2] == 'on':
                layout.itemconfig(objects, fill="Cyan", outline="Cyan")
        '''
    
    objectcount_label.config(text="Objects: " + str(object_counter))


def activate_object(pin_num):
    global object_id
    object_time = time.localtime(time.time())

    object_time = str(object_time[0]) + "/" + str(object_time[1]) + "/" + str(object_time[2]) + " " + str(object_time[3]) + ":" + str(object_time[4]) + ":" + str(object_time[5])
    print(object_time)
    gpio_num = "GPIO" + str(pin_num)
    object_tags = list(layout.gettags(gpio_num))
    object_id = object_tags[0]
    
    coords = list(layout.coords(object_id))
    if "d" in object_id:
        
        layout.dtag(object_id, object_tags[5])
        layout.dtag(object_id, object_tags[4])
        layout.dtag(object_id, object_tags[3])
        layout.dtag(object_id, object_tags[2])
        
        object_tags[5] = object_time

        print(layout.gettags(object_id))
        
        if object_tags[2] == 'closed':
            layout.addtag_withtag('open', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)
            layout.addtag_withtag(object_tags[5], object_id)

            print(layout.gettags(object_id))

            if object_tags[4] == 'horizontal':
                coords[2] = coords[2] - 5
                coords[3] = coords[3] - 15
                layout.coords(object_id, coords)
            elif object_tags[4] == 'vertical':
                coords[0] = coords[0] - 15
                coords[1] = coords[1] + 5
                layout.coords(object_id, coords)

        elif object_tags[2] == 'open':
            layout.addtag_withtag('closed', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)
            layout.addtag_withtag(object_tags[5], object_id)

            print(layout.gettags(object_id))

            if object_tags[4] == 'horizontal':
                coords[2] = coords[2] + 5
                coords[3] = coords[3] + 15
                layout.coords(object_id, coords)
            elif object_tags[4] == 'vertical':
                coords[0] = coords[0] + 15
                coords[1] = coords[1] - 5
                layout.coords(object_id, coords)

    if "v" in object_id:
        window_num = object_id[1:len(object_id)]

        base_piece = list(layout.gettags(list(layout.find_withtag("vb" + str(window_num)))[0]))[1]
        top_piece = list(layout.gettags(list(layout.find_withtag("vt" + str(window_num)))[0]))[1]

        layout.dtag(object_id, object_tags[5])
        layout.dtag(object_id, object_tags[4])
        layout.dtag(object_id, object_tags[3])
        layout.dtag(object_id, object_tags[2])

        object_tags[5] = object_time

        if object_tags[2] == 'closed':
            layout.addtag_withtag('open', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)
            layout.addtag_withtag(object_tags[5], object_id)

            if object_tags[4] == 'horizontal':
                coords[2] = coords[2] - 15
                layout.coords(base_piece, coords)
                coords = layout.coords(top_piece)
                coords[2] = coords[2] - 15
                layout.coords(top_piece, coords)
            elif object_tags[4] == 'vertical':
                coords[1] = coords[1] + 15
                layout.coords(base_piece, coords)
                coords = layout.coords(top_piece)
                coords[1] = coords[1] + 15
                layout.coords(top_piece, coords)

        elif object_tags[2] == 'open':
            layout.addtag_withtag('closed', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)
            layout.addtag_withtag(object_tags[5], object_id)

            if object_tags[4] == 'horizontal':
                coords[2] = coords[2] + 15
                layout.coords(base_piece, coords)
                coords = layout.coords(top_piece)
                coords[2] = coords[2] + 15
                layout.coords(top_piece, coords)
            elif object_tags[4] == 'vertical':
                coords[1] = coords[1] - 15
                layout.coords(base_piece, coords)
                coords = layout.coords(top_piece)
                coords[1] = coords[1] - 15
                layout.coords(top_piece, coords)

    if "l" in object_id:
        
        layout.dtag(object_id, object_tags[4])
        layout.dtag(object_id, object_tags[3])
        layout.dtag(object_id, object_tags[2])

        object_tags[4] = object_time
        
        if object_tags[2] == 'off':
            layout.addtag_withtag('on', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)
        elif object_tags[2] == 'on':
            layout.addtag_withtag('off', object_id)
            layout.addtag_withtag(object_tags[3], object_id)
            layout.addtag_withtag(object_tags[4], object_id)

    object_tags = list(layout.gettags(object_id))
    object_id = object_tags[0]

    print("To: " + str(object_tags))

    with open(os.path.join(__location__, 'LOGS.txt'), 'a') as file:
        file.write(str(object_tags) + "\n")


        
    
    update_gui()
    
    

def assign_object():
    global object_id
    global object_tags

    pin_num = pins.get()
    previous_pin_num = object_tags[3]

    if "d" in object_id or "v" in object_id:
        layout.dtag(object_id, object_tags[5])
        layout.dtag(object_id, object_tags[4])
        layout.dtag(object_id, object_tags[3])

        layout.addtag_withtag(pin_num, object_id)
        layout.addtag_withtag(object_tags[4], object_id)
        layout.addtag_withtag(object_tags[5], object_id)

    elif "l" in object_id:
        layout.dtag(object_id, object_tags[4])
        layout.dtag(object_id, object_tags[3])
        layout.addtag_withtag(pin_num, object_id)
        layout.addtag_withtag(object_tags[4], object_id)
    
   
    object_tags = list(layout.gettags(object_id))
    update_gui()

    if pin_num != "None":
        gpio_pin = int(pin_num[4:])
        print()
        print("Assigning " + str(pin_num) + " to " + object_id)
        GPIO.setup( int(gpio_pin), GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback = interupt, bouncetime = 300)
    elif pin_num == "None":
        gpio_pin = int(previous_pin_num[4:])
        print("pin num = none")
        print()
        print("Removing " + str(object_tags[3]) + " assigment from " + object_id)
        GPIO.remove_event_detect(gpio_pin)
    
    

def load_file():
    global objects_file
    global object_id
    global object_counter
    global wall_counter
    global door_counter
    global window_counter
    global light_counter

    object_counter = 0
    wall_counter = 0
    door_counter = 0
    window_counter = 0
    light_counter = 0
    object_id = "-1"

    for objects in list(layout.find_all()):
        layout.delete(objects)

    with open(os.path.join(__location__, 'Objects.txt'), 'rb') as picklefile:
        try:
            objects_file = pickle.load(picklefile)
        except EOFError:
            print("EOF")
            objects_file = {}

    walls_tags = []
    walls_coords = []
    doors_tags = []
    doors_coords = []
    windows_tags = []
    windows_coords = []
    lights_tags = []
    lights_coords = []

    for object_type, object_detail in objects_file.items():
        if object_type == 'walls':
            walls_tags = objects_file[object_type][0]
            walls_coords = objects_file[object_type][1]
        elif object_type == 'doors':
            doors_tags = objects_file[object_type][0]
            doors_coords = objects_file[object_type][1]
        elif object_type == 'windows':
            windows_tags = objects_file[object_type][0]
            windows_coords = objects_file[object_type][1]
        elif object_type == 'lights':
            lights_tags = objects_file[object_type][0]
            lights_coords = objects_file[object_type][1]

    for i in range(0, len(walls_tags)):
        layout.create_line(walls_coords[i],
                           fill="Cyan",
                           width=2,
                           tags=walls_tags[i])

    wall_counter = len(walls_tags)

    for i in range(0, len(doors_tags)):
        layout.create_line(doors_coords[i],
                           fill="Cyan",
                           width=2,
                           tags=doors_tags[i])

    door_counter = int(len(doors_tags) / 3)

    for i in range(0, len(windows_tags)):
        object_counter = object_counter + 1

        if ( str(windows_tags[i][1]).find("vb") != -1 or str(windows_tags[i][1]).find("vt") != -1 ):
            layout.create_line(windows_coords[i],
                               fill="Cyan",
                               width=1,
                               tags=windows_tags[i])
        else:
            layout.create_line(windows_coords[i],
                               fill="Cyan",
                               width=2,
                               tags=windows_tags[i])
    window_counter = int(len(windows_tags) / 4)

    for i in range(0, len(lights_tags)):
        layout.create_oval(lights_coords[i],
                           fill="Black",
                           outline="Cyan",
                           width=1,
                           tags=lights_tags[i])

    light_counter = len(lights_tags)

    object_counter = door_counter + wall_counter + window_counter + light_counter

    for objects in list(layout.find_all()):
        tags = list(layout.gettags(objects))
        if 'dc' in tags[1] or 'vb' in tags[1] or 'lc' in tags[1]:
            ob_id = tags[0]
            pin_num = tags[3]
            if pin_num != 'None':
                gpio_pin = int(tags[3][4:])
                GPIO.setup( gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
                GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback = interupt, bouncetime = 300)
                print("Assigning " + str(pin_num) + " to " + tags[0])

    update_gui()
    print("Loaded")

def save_file():
    global objects_file

    walls_tags = []
    walls_coords = []
    doors_tags = []
    doors_coords = []
    windows_tags = []
    windows_coords = []
    lights_tags = []
    lights_coords = []

    objects_file.clear()

    for objects in list(layout.find_all()):

        if (list(layout.gettags(objects))[0][0] == 'w'):
            walls_tags.append(list(layout.gettags(objects)))
            walls_coords.append(list(layout.coords(objects)))

        if (list(layout.gettags(objects))[0][0] == 'd'):
            doors_tags.append(list(layout.gettags(objects)))
            doors_coords.append(list(layout.coords(objects)))

        if (list(layout.gettags(objects))[0][0] == 'v'):
            windows_tags.append(list(layout.gettags(objects)))
            windows_coords.append(list(layout.coords(objects)))

        if (list(layout.gettags(objects))[0][0] == 'l'):
            lights_tags.append(list(layout.gettags(objects)))
            lights_coords.append(list(layout.coords(objects)))

    objects_file['walls'] = [walls_tags, walls_coords]
    objects_file['doors'] = [doors_tags, doors_coords]
    objects_file['windows'] = [windows_tags, windows_coords]
    objects_file['lights'] = [lights_tags, lights_coords]

    with open(os.path.join(__location__, 'Objects.txt'), 'wb') as picklefile:
        pickle.dump(objects_file, picklefile)

    print()
    print("Saved")

def edit_mode():
    global edit_allowed
    global object_id

    if not edit_allowed:
        edit_allowed = True
        edit_button.config(fg="White", activeforeground = "White")
        add_wall_button.config(state=NORMAL)
        add_door_button.config(state=NORMAL)
        add_window_button.config(state=NORMAL)
        add_light_button.config(state=NORMAL)
        print()
        print("Edit mode enabled")
    


    else:
        edit_allowed = False
        object_id = "-1"
        edit_button.config(fg="Cyan",activeforeground = "Cyan")
        add_wall_button.config(state=DISABLED)
        add_door_button.config(state=DISABLED)
        add_window_button.config(state=DISABLED)
        add_light_button.config(state=DISABLED)
        print()
        print("Edit mode disabled")



    update_gui()
    
def quit_app(): 
    GPIO.cleanup()    
    root.destroy()

root.bind('<Motion>', motion)
root.bind('<Button-1>', mouse_clicked)
root.bind('<B1-Motion>', move_object)

x_start = 2
y_start = 2
x_space = 82
y_space = 30

add_wall_button = Button(root,
                         text="Wall",
                         width=8,
                         command=add_wall,
                         bg="Black",
                         fg="Cyan",
                         font="Courier 10 bold",
                         relief="groove",
                         bd=3)
add_wall_button.place(x=1 * canvas_sizex + x_start + 0 * x_space,
                      y=0 * canvas_sizey + y_start + 0 * y_space)
add_door_button = Button(root,
                         text="Door",
                         width=8,
                         command=add_door,
                         bg="Black",
                         fg="Cyan",
                         font="Courier 10 bold",
                         relief="groove",
                         bd=3)
add_door_button.place(x=1 * canvas_sizex + x_start + 0 * x_space,
                      y=0 * canvas_sizex + y_start + 1 * y_space)
add_window_button = Button(root,
                           text="Window",
                           width=8,
                           command=add_window,
                           bg="Black",
                           fg="Cyan",
                           font="Courier 10 bold",
                           relief="groove",
                           bd=3)
add_window_button.place(x=1 * canvas_sizex + x_start + 0 * x_space,
                        y=0 * canvas_sizey + y_start + 2 * y_space)
add_light_button = Button(root,
                          text="Light",
                          width=8,
                          command=add_light,
                          bg="Black",
                          fg="Cyan",
                          font="Courier 10 bold",
                          relief="groove",
                          bd=3)
add_light_button.place(x=1 * canvas_sizex + x_start + 0 * x_space,
                       y=0 * canvas_sizey + y_start + 3 * y_space)
rotate_object_button = Button(root,
                              text="Rotate",
                              width=8,
                              command=rotate_object,
                              bg="Black",
                              fg="Cyan",
                              font="Courier 10 bold",
                              relief="groove",
                              bd=3)
rotate_object_button.place(x=0 * canvas_sizex + x_start + 0 * x_space,
                           y=1 * canvas_sizey + y_start + 0 * y_space)
copy_object_button = Button(root,
                            text="Copy",
                            width=8,
                            command=copy_object,
                            bg="Black",
                            fg="Cyan",
                            font="Courier 10 bold",
                            relief="groove",
                            bd=3)
copy_object_button.place(x=0 * canvas_sizex + x_start + 1 * x_space,
                         y=1 * canvas_sizey + y_start + 0 * y_space)
increase_button = Button(root,
                         text="+",
                         width=3,
                         command=increase_size,
                         bg="Black",
                         fg="Cyan",
                         font="Courier 10 bold",
                         relief="groove",
                         bd=3)
increase_button.place(x=0 * canvas_sizex + x_start + 2 * x_space,
                      y=1 * canvas_sizey + y_start + 0 * y_space)
decrease_button = Button(root,
                         text="-",
                         width=3,
                         command=decrease_size,
                         bg="Black",
                         fg="Cyan",
                         font="Courier 10 bold",
                         relief="groove",
                         bd=3)
decrease_button.place(x=0 * canvas_sizex + x_start + 2.5 * x_space - 1,
                      y=1 * canvas_sizey + y_start + 0 * y_space)
delete_button = Button(root,
                       text="Delete",
                       width=8,
                       command=delete_object,
                       bg="Black",
                       fg="Cyan",
                       font="Courier 10 bold",
                       relief="groove",
                       bd=3)
delete_button.place(x=0 * canvas_sizex + x_start + 0 * x_space,
                    y=1 * canvas_sizey + y_start + 1 * y_space)
save_button = Button(root,
                     text="Save",
                     width=8,
                     command=save_file,
                     bg="Black",
                     fg="Cyan",
                     font="Courier 10 bold",
                     relief="groove",
                     bd=3)
save_button.place(x=0 * canvas_sizex + x_start + 1 * x_space,
                  y=1 * canvas_sizey + y_start + 1 * y_space)
load_button = Button(root,
                     text="Load",
                     width=8,
                     command=load_file,
                     bg="Black",
                     fg="Cyan",
                     font="Courier 10 bold",
                     relief="groove",
                     bd=3)
load_button.place(x=0 * canvas_sizex + x_start + 2 * x_space,
                  y=1 * canvas_sizey + y_start + 1 * y_space)

assign_button = Button(root,
                       text="Assign",
                       width=8,
                       command=assign_object,
                       bg="Black",
                       fg="Cyan",
                       font="Courier 10 bold",
                       relief="groove",
                       bd=3)
assign_button.place(x=1 * canvas_sizex + x_start + 0 * x_space,
                    y=0 * canvas_sizey + y_start + 4* y_space)
pin_menu = OptionMenu(root, pins, *gpio_list)
pin_menu.place(x=1 * canvas_sizex + x_start + 0 * x_space ,
               y=0 * canvas_sizey + y_start + 5 * y_space)
pin_menu.config(bg="Black",
                fg="Cyan",
                width=5,
                bd=1,
                height=1,
                relief="groove",
                activebackground = "Black",
                activeforeground = "Cyan",
                font="Courier 8 bold")
edit_button = Button(root,
                    text="Edit Mode",
                    width=8,
                    command=edit_mode,
                    bg="Black",
                    fg="White",
                    font="Courier 7 bold",
                    relief="flat",
                    bd=0,
                    activebackground = "Black",
                    activeforeground = "White")
edit_button.place(x=0 * canvas_sizex + x_start + 0 * x_space + 5 ,
                  y=0 * canvas_sizey + y_start + 0 * y_space + 5)
quit_button = Button(root,
                     text="Exit",
                     width=8,
                     command=quit_app,
                     bg="Black",
                     fg="Cyan",
                     font="Courier 10 bold",
                       relief="groove",
                       bd=3)
quit_button.place(x=0 * canvas_sizex + x_start + 3 * x_space - 4,
                    y=1 * canvas_sizey + y_start + 1* y_space)
                     
xy_label = Label(root,
                 bg="Black",
                 fg="Cyan",
                 font="Courier 7 bold")
xy_label.place(x=180,
               y=300)
objectcount_label = Label(root,
                          bg="Black",
                          fg="Cyan",
                          font="Courier 7 bold",
                          text="Objects: 0")
objectcount_label.place(x=5,
                        y=300)
objectid_label = Label(root,
                       bg="Black",
                       fg="Cyan",
                       font="Courier 7 bold",
                       text="ID: None")
objectid_label.place(x=5,
                     y=270)
objectactivity_label = Label(root,
                       bg="Black",
                       fg="Cyan",
                       font="Courier 7 bold",
                       text="Last activity: N/A ")
objectactivity_label.place(x=5,
                            y =285)

root.mainloop()
