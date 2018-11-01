Running the server:

Params: Server Port, Inactive Timer (optional)
	- The Server Port needs to fall inside the range of dedicated ports
	- The Inactive Timer gives the number of minutes of inactivity 
	  before a session is terminated (the default is 10 minutes)

Examples:
	python3 server.py 8000 1
		Inactive Timer set to 1
	python3 server.py 8888
		Inactive Timer set to 10



Running the client:

Params: Server Port
	- The Server Port should be the port number for the POP3 server that
	  the client will be connecting with



Stages of a session:
	
	Authentication:
		- Needed to access the inbox
		- Valid commands:
			- USER (your username here) gives the server your username
			- PASS (your password here) gives the server your password
			- QUIT ends the session

	Transaction:
		- Allowed to access the inbox
		- Valid commands:
			- LIST (optional email index here) gives the information of all
			  emails in the inbox (index and character count, or just the 
			  one email, if optional param is given
			- STAT gives the status of the whole inbox (number of emails, 
			  total inbox size in characters)
			- RETR (email index here) gives the contents of an email
			- DELE (email index here) deletes an email from the inbox
			- RSET recovers all emails deleted during the current session;
			  emails deleted in prior sessions are lost
			- NOOP does nothing, except reset the inactivity clock
			- QUIT leaves the session