import socket
import asyncio

class Server():
	def __init__(self):
		self.clientlist = {}

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1', 10000))
		self.sock.listen(5)
		self.sock.setblocking(False)
		
		self.loop = asyncio.get_event_loop()
		self.loop.run_until_complete(self.run_server())

	async def run_server(self):
		while True:
			client, address = await self.loop.sock_accept(self.sock)
			self.loop.create_task(self.handle_client(client))
			clientdata = {'xcoord': 0, 'ycoord': 0, 'damage': 0, 'strength': 1, 'flag': 0}
			self.clientlist[client.fileno()] = clientdata

	async def handle_client(self, client):
		running = True

		while running:
			request = ['']
			request = await self.loop.sock_recv(client, 1024)
			request = request.decode('utf8').split(':')
			print(str(request) + '   ' + str(client.fileno()))

			if request[0] == 'quit':
				self.clientlist.pop(client.fileno())
				running = False

			elif request[0] == 'coord':
				await self.handle_player(client, int(request[1]), int(request[2]))

			elif request[0] == 'damage':
				await self.handle_monster(client, int(request[1]))

		client.close()

	async def handle_player(self, client, xcoord, ycoord):
		self.clientlist[client.fileno()]['xcoord'] = xcoord
		self.clientlist[client.fileno()]['ycoord'] = ycoord	

		response = ''
		for player in self.clientlist:	
			response += str(self.clientlist[player]['xcoord']) + ':' + str(self.clientlist[player]['ycoord']) + ';'

		await self.loop.sock_sendall(client, response.encode('utf8'))

	async def handle_monster(self, client, damage):
		self.clientlist[client.fileno()]['damage'] += damage * self.clientlist[client.fileno()]['strength']

		total = 0
		response = ''
		for player in self.clientlist:	
			total += self.clientlist[player]['damage']
			if self.clientlist[player]['damage'] > 50:
				if self.clientlist[player]['flag'] == 0: self.clientlist[player]['strength'] += 0.2
				self.clientlist[player]['flag'] = 1
		if total > 100:
			for player in self.clientlist:
				self.clientlist[player]['damage'] = 0
			self.clientlist[player]['flag'] = 0
			response = '100'
		else:
			response = str(total)

		await self.loop.sock_sendall(client, response.encode('utf8'))

server = Server()