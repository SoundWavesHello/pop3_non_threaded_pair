'''
Author: Kevin Lane
Last Modified: 10/31/18

This is a simple example server for a POP3 protocol.
Only one inbox is implemented here (mine), although
it would be relatively straightforward to implement
more.

The actual inbox is a static entity.  As long as the
server is running, that is maintained.  In other words,
if the client makes changes to the inbox in one session
and then comes back in another session, those changes
are still present.
'''


import socket
import sys
import time


def my_server():

	# set host and port
	host = '0.0.0.0'
	port = int(sys.argv[1])
	
	# get the maximum inactivity timeout parameter
	if len(sys.argv) == 3:
		max_time = int(sys.argv[2]) * 60
	else:
		max_time = 10 * 60

	# establsih server socket
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.bind((host, port))
	serverSocket.listen(1)
	print('Listening on {}:{}'.format(host, port))

	# declare variables for server
	user = "kevdog"
	password = "password" # so secure!
	unread = ["Dear Kevin,\n It has been a pleasure to be of service here at the DMV.\nSincerely,\nSatan", "Hey Kevin,\nGive your mother a call; she needs to talk to you about something.\n -Dad", "Whoops, wrong email address"]
	length = 0
	deleted = []
	for email in unread:
		length += len(email)

	# keep track of which stage you're in
	auth_stage = True
	user_auth = False

	# while the server is running
	while True:

		# establish TCP connection (new client session)
		client_socket, address = serverSocket.accept()
		print('Accepted connection from {}:{}'.format(address[0], address[1]))

		# send greeting
		client_socket.send('Hello Kevin Lane'.encode())

		# while the session is still running
		while True:

			try:
				# set inactivity timer
				client_socket.settimeout(max_time)

				# get new client request
				request = client_socket.recv(1024).decode('utf8')

				# if in the authentication stage
				if auth_stage:
					# check if you need to quit
					if request == "QUIT":
						print("---------QUITTING---------")
						client_socket.send('+OK kevdog\'s POP3 server signing off'.encode())
						break

					# check if user matches
					elif request[0:4] == 'USER':
						if request[5:] == user:
							user_auth = True
							client_socket.send("+OK".encode())
						else:
							client_socket.send("-ERR sorry no mailbox for {} here".format(request[5:]).encode())

					# check if password matches (and if user has been specified yet)
					elif request[0:4] == 'PASS':
						if user_auth:
							if request[5:] == password:
								auth_stage = False
								client_socket.send("+OK {} successfully logged on".format(user).encode())
							else:
								client_socket.send("-ERR that's the wrong password".encode())
						else:
							client_socket.send("-ERR specify your username first".encode())

					# otherwise, the command given is a mistake
					else:
						client_socket.send("-ERR no such command available".encode())

				# transaction stage
				else:
					# get maildrop status
					if request == "STAT":
						client_socket.send("+OK {} {}".format(len(unread), length).encode())

					# list out all email info (or specific email info with optional parameter)
					elif request.startswith("LIST"):
						list_mail(client_socket, request, unread)
						

					# retrieve specific email
					elif request[0:4] == "RETR" and len(request) > 5:
						retrieve(client_socket, request, unread)

					# delete specific email
					elif request[0:4] == "DELE" and len(request) > 5:
						length = delete(client_socket, request, unread, length, deleted)

					# NOOP command (just to delay inactivity timeout)
					elif request == "NOOP":
						client_socket.send("+OK".encode())

					# reset inbox and reclaim emails deleted in the session
					elif request == "RSET":
						for email in deleted:
							unread.append(email)
							length += len(email)
						deleted = []
						client_socket.send("+OK maildrop has {} messages ({} octets)".format(len(unread), length).encode())

					# quit, and tell the user the state of their inbox
					elif request == "QUIT":
						print("--------QUITTING---------")
						if length == 0:
							client_socket.send("+OK {}\'s POP3 server signing off (no messages left)".format(user).encode())
						else:
							client_socket.send("+OK {}\'s POP3 server signing off ({} messages left)".format(user, len(unread)).encode())
						break

					# catch all error statement
					else:
						client_socket.send("-ERR no such command found".encode())

			# inactivity timout occurs
			except socket.timeout:
				print("Client inactive")
				client_socket.send("Inactivity Timeout".encode())
				break

		# close the TCP connection, reset the session variables
		client_socket.close()
		print("TCP connection torn down")
		auth_stage = True
		user_auth = False
		deleted = []



# Purpose:	Lists out the emails and their length, depending on request 
# Params:	The client socket, request, and mailbox
# Returns:	None
def list_mail(client_socket, request, unread):
	# check if any other params
	if len(request) == 4:
		# list all emails
		overall = ""
		for num, email in enumerate(unread):
			num += 1
			line = str(num) + " " + str(len(email)) + "\n"
			overall += line
		client_socket.send("+OK {} messages \n{}.".format(len(unread), overall).encode())

	# otherwise, just list the one email
	else:
		index = get_index(request, unread)
		if index == -1:
			client_socket.send("-ERR no such message".encode())
		else:
			email = unread[index]
			client_socket.send("+OK {} {}".format(index + 1, len(email)).encode())

# Purpose:	Retrieves and sends the client an email's contents
# Params:	The client socket, request, and email inbox
# Returns:	None
def retrieve(client_socket, request, unread):
	index = get_index(request, unread)
	if index == -1:	
		client_socket.send("-ERR no such message".encode())
	else:
		email = unread[index] + "\n."
		client_socket.send("+OK {} octets \n{}".format(len(email), email).encode())


# Purpose:	Delete an email from the server inbox
# Params:	The client socket, request, email inbox, size of inbox in email lengths,
#			and the emails deleted during this session
# Returns:	The new inbox size
def delete(client_socket, request, unread, size, deleted):
	index = get_index(request, unread)
	# check if the index is in range
	if index == -1:
		client_socket.send("-ERR no such message".encode())
		return size
	else:
		client_socket.send("+OK message deleted".encode())
		# remove the email from the inbox
		email = unread.pop(index)
		# keep track of it in the emails deleted this session
		deleted.append(email)
		return size - len(email)


# Purpose:	Gets the index of an email from a request
# Params:	The request and the inbox
# Returns:	-1 if the index is out of bounds, otherwise returns the index
def get_index(request, unread):
	index = int (request[5:]) - 1
	if index + 1 > len(unread):
		return -1
	else:
		return index


my_server()
