import tkinter as tk
import pygame as pg
import os
import socket

# Global variables
width, height, center = 500, 250, (150, 125)
HOST = '127.0.0.1'
PORT = 10000 # this is arbitrary, must be >1024

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
background = pg.Surface((width,height)).convert()
background.fill((100,100,100))
screen.blit(background, (0,0))

class Character(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('character.png').convert()
		self.image = pg.transform.scale(self.image, (32,32))
		self.rect = self.image.get_rect()

	def update(self, xcoord, ycoord):
		self.rect.center = (xcoord,ycoord)

class Monster(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('monster.png').convert()
		self.image = pg.transform.scale(self.image, (128,128))
		self.rect = self.image.get_rect()
		self.rect.center = center

	def damaged(self):
		if self.rect.collidepoint((xcoord, ycoord)):
			cmd = 'damage:5'
			s.sendall(cmd.encode('utf8'))
			playerdata = s.recv(1024).decode('utf8')

# create a sprite group
sprites = pg.sprite.Group()
monsters = pg.sprite.Group()

# Main animation loop
while 1:

    clock.tick(60)

    xcoord = int((sliderx.get() + 180)*1.39)
    ycoord = int((slidery.get() + 180)*0.69)
       
    cmd = 'xcoord:' + str(xcoord)
    s.sendall(cmd.encode('utf8'))
    playerdata = s.recv(1024).decode('utf8')

    cmd = 'ycoord:' + str(ycoord)
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

    monster = Monster()
    monsters.add(monster)
    monster.damaged()

    # Clear screen before next frame
    screen.blit(background, (0, 0))

    # Draw sprites to screen
    sprites.draw(screen)
    monsters.draw(screen)	

    # Update pygame display
    pg.display.flip()

    # Update the Tk display
    root.update()
