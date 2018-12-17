import tkinter as tk
import pygame as pg
import os
import socket

global running

class Client():
	def __init__(self):
		self.width, self.height = 500, 200
		self.center = (int(self.width/2), int(self.height/2))
		self.xcoord, self.ycoord = self.center

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(('127.0.0.1', 10000))

		self.clock = pg.time.Clock()
		
		self.application = Application(self.width, self.height)

		self.sprites = pg.sprite.Group()
		self.monsters = pg.sprite.Group()

		self.monster = Monster()
		self.monsters.add(self.monster)

		self.game_loop()

	def game_loop(self):
		running = True 

		while running:
			self.clock.tick(60)

			self.get_coords()
			self.handle_characters()
			self.handle_monster()
			
			self.application.clear_screen()
			self.application.draw_objects(self.monster.hp, self.sprites, self.monsters)
			self.application.update_screen()

		cmd = 'quit'
		self.sock.sendall(cmd.encode('utf8'))
		self.application.root.destroy()

	def get_coords(self):
		key = pg.key.get_pressed()

		if key[pg.K_LEFT]:
			if self.xcoord > 0:
				self.xcoord -= 10
		if key[pg.K_RIGHT]:
			if self.xcoord < self.width:
				self.xcoord += 10
		if key[pg.K_UP]:
			if self.ycoord > 0:
				self.ycoord -= 10
		if key[pg.K_DOWN]:
			if self.ycoord < self.height:
				self.ycoord += 10

	def handle_characters(self):
		cmd = 'coord:' + str(self.xcoord) + ':' + str(self.ycoord)
		self.sock.sendall(cmd.encode('utf8'))
		playerdata = self.sock.recv(1024).decode('utf8')
		print(playerdata)

		playerdata = playerdata.split(';')
		playerdata = playerdata[0:len(playerdata)-1]
		numplayers = len(playerdata)

		while len(self.sprites) != numplayers:
			if len(self.sprites) < numplayers:
				p = Character()
				self.sprites.add(p)
			elif len(self.sprites) > numplayers:
				self.sprites.remove()

		location = []
		for player in playerdata:
			player = player.split(':')
			location += [(int(player[0]), int(player[1]))]            

		num = 0
		for sprite in self.sprites:
			sprite.update(location[num][0], location[num][1])
			num += 1

	def handle_monster(self):
		cmd = self.monster.damaged(self.xcoord, self.ycoord)
		self.sock.sendall(cmd.encode('utf8'))
		monsterdata = self.sock.recv(1024).decode('utf8')
		self.monster.hp = 100 - float(monsterdata)

def quit_program():
	running = False

class Application():
	def __init__(self, width, height):
		self.root = tk.Tk()
		self.root.title('Client application')
		self.root.iconbitmap('icon.ico')
		self.root.protocol('WM_DELETE_WINDOW', quit_program)
		self.embed = tk.Frame(self.root, width = width, height = height)
		self.embed.pack()

		os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
		self.root.update()

		pg.display.init()
		self.screen = pg.display.set_mode((width, height))

		self.background = pg.image.load('background.png').convert()
		self.background = pg.transform.scale(self.background, (width, height))
		self.screen.blit(self.background, (0, 0))

	def clear_screen(self):
		self.screen.blit(self.background, (0, 0))

	def draw_objects(self, hp, sprites, monsters):
		pg.draw.line(self.screen, (0,255,0), (100, 50), (100+hp, 50), 10)
		monsters.draw(self.screen)	
		sprites.draw(self.screen)

	def update_screen(self):
		pg.display.flip()
		self.root.update()

class Character(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('character.png').convert_alpha()
		self.image = pg.transform.scale(self.image, (64, 64))
		self.rect = self.image.get_rect()

	def update(self, xcoord, ycoord):
		self.rect.center = (xcoord,ycoord)

class Monster(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		self.image = pg.image.load('monster.png').convert_alpha()
		self.image = pg.transform.scale(self.image, (128, 128))
		self.rect = self.image.get_rect()
		self.rect.center = (150, 125)
		self.hp = 100

	def damaged(self, xcoord, ycoord):
		if self.rect.collidepoint((xcoord, ycoord)): return 'damage:1'
		else: return 'damage:0'

client = Client()