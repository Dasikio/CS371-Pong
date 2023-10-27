# =================================================================================================
# Contributing Authors:	    Daniel Alvarado, Natalie O'Leary
# Email Addresses:          dal240@uky.edu, natalie.oleary@uky.edu
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
import pickle


SERVER = socket.gethostbyname(socket.gethostname()) #Command to get server IPv4 addres (might change depending on network)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create server

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #working on local host

server.bind((SERVER, 12321))

server.listen(5)
print(f"Listening on {SERVER}") #Once server starts listening it shows IPv4 to use to connect

position = ["left","right"] #list to know what side each player is in (0 is left player, 1 is right player)

def player_handle(playerSocket,playerNum):
    start = (640,480,position[playerNum]) #tuple that contains values to start client (width,length,position of player)
    playerSocket.send(pickle.dumps(start)) #send command, uses pickle so client receives tuple with the correct format after sending through socket

# loop, get paddle and ball location

currPlayer = 0
while True:
    playerSocket, playerAddress = server.accept()
    playerThread = threading.Thread(target=player_handle, args=(playerSocket,currPlayer,))
    playerThread.start()
    currPlayer +=1

#server.listen(5)


#player1Thread.start()
#player2Thread.start()
#player1Thread.join()
#player2Thread.join()

#player1Socket.close()
#player2Socket.close()
server.close()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games