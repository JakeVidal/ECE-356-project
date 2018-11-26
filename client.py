import tkinter as tk
import pygame as pg
import math as m
import random as r
import os
import socket
import time

# Global variables
width, height, center = 500, 250, (150, 125)
first_iteration = True
xref_point = (50, 0, 0)
yref_point = (0, -50, 0)
zref_point = (0, 0, 50)
HOST = '127.0.0.1'
PORT = 10000 # this is arbitrary, must be >1024

# Define rotation functions
def rotate_point_yaxis(xcoord, ycoord, zcoord, theta):
    return (xcoord*m.cos(theta)+zcoord*m.sin(theta), ycoord, -1*xcoord*m.sin(theta)+zcoord*m.cos(theta))

def rotate_point_xaxis(xcoord, ycoord, zcoord, theta):
    return (xcoord, ycoord*m.cos(theta)-zcoord*m.sin(theta), ycoord*m.sin(theta)+zcoord*m.cos(theta))

def rotate_point_zaxis(xcoord, ycoord, zcoord, theta):
    return (xcoord*m.cos(theta)-ycoord*m.sin(theta), xcoord*m.sin(theta)+ycoord*m.cos(theta), zcoord)

def rotate_point_xyz(xcoord, ycoord, zcoord, thetax, thetay, thetaz):
    a = rotate_point_xaxis(xcoord, ycoord, zcoord, thetax)
    b = rotate_point_yaxis(a[0], a[1], a[2], thetay)
    return rotate_point_zaxis(b[0], b[1], b[2], thetaz)

# Add tkinter widgets placing pygame in embed
root = tk.Tk()
root.title("Client application")
#root.iconbitmap('icon.ico')
embed = tk.Frame(root, width=width, height=height)
embed.pack()
sliderz = tk.Scale(root, from_=-180, to=180, orient=tk.HORIZONTAL, label='Z-axis')
sliderz.pack(side=tk.RIGHT)
slidery = tk.Scale(root, from_=-180, to=180, orient=tk.HORIZONTAL, label='Y-axis')
slidery.pack(side=tk.RIGHT)
sliderx = tk.Scale(root, from_=-180, to=180, orient=tk.HORIZONTAL, label='X-axis')
sliderx.pack(side=tk.RIGHT)

# Tell pygame's SDL window which window ID to use    
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())

# Show the window so it's assigned an ID.
root.update()

# Usual pygame initialization
pg.display.init()
screen = pg.display.set_mode((width,height))

#connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

testnum = 0
# Main animation loop
while 1:

    # Update  screen background
    screen.fill((100, 100, 100))

    # Set slider input
    thetay = m.radians(sliderx.get())
    thetax = m.radians(slidery.get())
    thetaz = m.radians(sliderz.get())

    # Draw x, y and z axis reference
    x_point = rotate_point_xyz(xref_point[0], xref_point[1], xref_point[2], thetax, thetay, thetaz)
    y_point = rotate_point_xyz(yref_point[0], yref_point[1], yref_point[2], thetax, thetay, thetaz)
    z_point = rotate_point_xyz(zref_point[0], zref_point[1], zref_point[2], thetax, thetay, thetaz)
    pg.draw.line(screen, (255, 0, 0), (75, height-75), (75+x_point[0], height-75+x_point[1]), 3)
    pg.draw.line(screen, (0, 255, 0), (75, height-75), (75+y_point[0], height-75+y_point[1]), 3)
    pg.draw.line(screen, (0, 0, 255), (75, height-75), (75+z_point[0], height-75+z_point[1]), 3)
    pg.draw.circle(screen, (255, 255, 255), (75, height-75), 3)

    xcoord = sliderx.get()
    ycoord = slidery.get()
       
    cmd = 'xcoord:' + str(xcoord)
    s.sendall(cmd.encode('utf8'))
    playerdata = s.recv(1024).decode('utf8')

    cmd = 'ycoord:' + str(ycoord)
    s.sendall(cmd.encode('utf8'))
    playerdata = s.recv(1024).decode('utf8')

    print(playerdata)
    playerdata = playerdata.split(';')
    for player in playerdata:
        player = player.split(':')
        if player != ['']:
            pg.draw.circle(screen, (255, 255, 255), (int(player[0]), int(player[1])), 3)

    # Update pygame display
    pg.display.flip()

    # Update the Tk display
    root.update()
