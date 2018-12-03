import tkinter as tk
import pygame as pg
import os
import socket

# Global variables
width, height, center = 500, 250, (250, 125)
HOST = '127.0.0.1'
PORT = 10000 # this is arbitrary, must be >1024
xcoord, ycoord = center

# Add tkinter widgets placing pygame in embed
root = tk.Tk()
root.title("Client application")
#root.iconbitmap('icon.ico')
embed = tk.Frame(root, width=width, height=height)
embed.pack()
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

# Connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Create a clock for loop timing
clock = pg.time.Clock()

# Set screen background
background = pg.image.load('background.png').convert()
background = pg.transform.scale(background, (width,height))
screen.blit(background, (0,0))

class Character(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('character.png').convert_alpha()
		self.image = pg.transform.scale(self.image, (32,32))
		self.rect = self.image.get_rect()

	def update(self, xcoord, ycoord):
		self.rect.center = (xcoord,ycoord)

class Monster(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('monster.png').convert_alpha()
		self.image = pg.transform.scale(self.image, (128,128))
		self.rect = self.image.get_rect()
		self.rect.center = (150,125)
		self.hp = 100

	def damaged(self):
		if self.rect.collidepoint((xcoord, ycoord)):
			cmd = 'damage:1'
			return cmd
		else:
			cmd = 'damage:0'
			return cmd

# create a sprite group
sprites = pg.sprite.Group()
monsters = pg.sprite.Group()

monster = Monster()
monsters.add(monster)

# Main animation loop
while 1:

    clock.tick(60)

#    xcoord = int((sliderx.get() + 180)*1.39)
#    ycoord = int((slidery.get() + 180)*0.69)

    key = pg.key.get_pressed()
    if key[pg.K_LEFT]:
        if xcoord > 0:
            xcoord -= 10
    if key[pg.K_RIGHT]:
        if xcoord < 500:
            xcoord += 10
    if key[pg.K_UP]:
        if ycoord > 0:
            ycoord -= 10
    if key[pg.K_DOWN]:
        if ycoord < 250:
            ycoord += 10

    cmd = 'coord:' + str(xcoord) + ':' + str(ycoord)
    s.sendall(cmd.encode('utf8'))
    playerdata = s.recv(1024).decode('utf8')

    print(playerdata)
    playerdata = playerdata.split(';')
    playerdata = playerdata[0:len(playerdata)-1]

    numplayers = len(playerdata)
    while len(sprites) != numplayers:
    	if len(sprites) < numplayers:
    		p = Character()
    		sprites.add(p)
    	elif len(sprites) > numplayers:
    		p = Character()
    		sprites.remove()

    location = []

    for player in playerdata:
        player = player.split(':')
        location += [(int(player[0]), int(player[1]))]            

    num = 0
    for sprite in sprites:
        sprite.update(location[num][0], location[num][1])
        num += 1

    cmd = monster.damaged()
    s.sendall(cmd.encode('utf8'))
    monsterdata = s.recv(1024).decode('utf8')

    monster.hp = 100 - int(monsterdata)
    
    # Clear screen before next frame
    screen.blit(background, (0, 0))

    # Draw HP to screen
    pg.draw.line(screen, (0,255,0), (100, 50), (100+monster.hp, 50), 10)

    # Draw sprites to screen
    if monster.hp > 0:
    	monsters.draw(screen)	
    sprites.draw(screen)

    # Update pygame display
    pg.display.flip()

    # Update the Tk display
    root.update()
