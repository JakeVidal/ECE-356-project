import socket
import asyncio

clientlist = {}

async def handle_client(client):

	cn = client.fileno()

	while True:
		request = ['']
		request = await loop.sock_recv(client, 1024)
		request = request.decode('utf8').split(':')
		print(str(request) + '   ' + str(cn))

		if request[0] == 'xcoord':
			clientlist[cn]['xcoord'] = int(request[1])
		if request[0] == 'ycoord':
			clientlist[cn]['ycoord'] = int(request[1])	
		if request[0] == 'damage':
			clientlist[cn]['damage'] += int(request[1])		

		response = ''
		for player in clientlist:	
			response += str(clientlist[player]['xcoord']) + ':' + str(clientlist[player]['ycoord']) + ';'

		await loop.sock_sendall(client, response.encode('utf8'))

	client.close()

async def run_server():
	while True:
		client, address = await loop.sock_accept(server)
		loop.create_task(handle_client(client))
		clientdata = {'xcoord': 0, 'ycoord': 0, 'damage': 0}
		clientlist[client.fileno()] = clientdata

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 10000))
server.listen(5)
server.setblocking(False)

loop = asyncio.get_event_loop()
loop.run_until_complete(run_server())