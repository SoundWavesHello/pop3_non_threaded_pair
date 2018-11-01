'''
Author: Kevin Lane
Last Modified: 10/31/18

This is a simple example client for a POP3 protocol.
It establishes a TCP connection with a server and
then proceeds to send user messages to the server.

For a list of valid commands, please see the README
'''


import socket
import sys

def my_client():
	# set server destination
	host = '0.0.0.0'
	port = sys.argv[1]

	# establish socket
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# this establishes on TCP connection for the session
	clientSocket.connect((host, int(port)))
	print(clientSocket.recv(1024).decode())

	# allow for multiple commands during the session
	while(True):
		# allow for user input
		command = input('')
		# send that input
		clientSocket.send(command.encode())

		# receive the response from the server
		response = clientSocket.recv(1024).decode()
		print(response)

		# only terminate the session due to QUIT command or 
		# client inactivity (signalled by server)
		if command == "QUIT" or  response == "Inactivity Timeout":
			break

	# end the session
	clientSocket.close()

my_client()