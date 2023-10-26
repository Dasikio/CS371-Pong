# =================================================================================================
# Contributing Authors:	    Daniel Alvarado, Natalie O'Leary
# Email Addresses:          dal240@uky.edu, natalie.oleary@uky.edu
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create server

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #working on local host

server.bind(("127.0.0.1", 12321))

server.listen(5)

player1Socket, player1Address = server.accept()

server.listen(5)

player2Socket, player2Address = server.accept()

player1Socket.close()
player2Socket.close()
server.close()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games