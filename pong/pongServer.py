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


SERVER = socket.gethostbyname(socket.gethostname()) #Get server IPv4 address (might change depending on network)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create server

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Working on local host

server.bind((SERVER, 12321))

server.listen(5)
print(f"Listening on {SERVER}") #Once the server starts listening, it shows the IPv4 to use to connect

side = ["left","right"] #List that specifies which side each player is on (list value 0 = left player, list value 1 = right player)
paddleDirection = ["",""] #Default direction for paddles

#Handles information exchange between client and server 
def player_handle(playerSocket,playerNum):
    start = (640,480,side[playerNum]) #Tuple that contains values to start client (width,length, side of player)
    playerSocket.send(pickle.dumps(start)) #Send information via pickle so client receives tuple with the correct format after sending through socket
    reply = "" #Initialize reply variable

    #Continuously get the paddle position from the client and reply with the paddle position of the opponent
    while True:

        #Try checks for error
        try:
            #msg = playerSocket.recv(1024).decode() #Retrieve paddle position message from client
            #paddleDirection[playerNum] = msg #Update position of the player calling the handle

            msg = playerSocket.recv(1024)
            playerInfo = pickle.loads(msg)
            # ball x, ball y, paddle moving, score, sync
            paddleDirection[playerNum] = playerInfo[2]

            #Set the reply to equal the position of the opponent's paddle
            if playerNum == 0:
                reply = paddleDirection[1]
            else:
                reply = paddleDirection[0]
            
            playerSocket.send(reply).encode() #Send opponent's paddle position
       
       #If an error occurs, break loop
        except:
            break   
    
    #Close connection, end loop
    playerSocket.close()


currPlayer = 0 #Initialize variable to indicate current player

#The main loop that connects the client to the server and begins a thread to update paddle positions to interested parties,
#alternating between players
while True:
    playerSocket, playerAddress = server.accept()
    playerThread = threading.Thread(target=player_handle, args=(playerSocket,currPlayer,))
    playerThread.start()
    playerThread.join()
    currPlayer +=1 #Update for next player

#server.listen(5)

#Close server
server.close()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games