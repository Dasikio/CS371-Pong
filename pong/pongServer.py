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

#Set up server
SERVER = socket.gethostbyname(socket.gethostname()) #Get server IPv4 address (might change depending on network)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create server
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Working on local host
server.bind((SERVER, 12321))

#Server begins to listen
server.listen(5) #find how to allow infinite #of players / maybe start listening in a bigger loop so it always listens for 2 connections then start listening again?
print(f"Listening on {SERVER}") #Once the server starts listening, it shows the IPv4 to use to connect

#Initialize variables
side = ["left","right"] #List that specifies which side each player is on (list value 0 = left player, list value 1 = right player)
paddleDirection = ["",""] #Default direction for paddles
ballPosition = [(320,240),(320,240)]
playerSync = [0,0]
score = [0, 0]

#Create event to check that both players are connected before starting
both_players_connected = threading.Event()

#Primary function that handles information exchange between client and server -> to be run in concurrent threads
def player_handle(playerSocket,playerNum):

    #Wait until both players are connected before proceeding
    both_players_connected.wait()

    start = (640,480,side[playerNum]) #Tuple that contains values to start client (width, length, side of player)
    playerSocket.send(pickle.dumps(start)) #Send information via pickle
    reply = [(320, 240), "", [0, 0], 0] #Initialize reply variable with ball coordinates, empty string for paddle direction, int for score, int for sync

    #Continuously get the paddle position from the client and reply with the paddle position of the opponent
    while True:

        #Try checks for error
        try:

            #Receive information from client
            #In order: Ball x-coord, ball y-coord, direction of paddle movement, current score, sync value
            msg = playerSocket.recv(1024)
            playerInfo = pickle.loads(msg)

            #Store information in server variables that correspond to player's position where index 0 = left player and index 1 = right player
            paddleDirection[playerNum] = playerInfo[2] #Store paddle movement
            ballPosition[playerNum] = (playerInfo[0],playerInfo[1]) #Store ball position
            playerSync[playerNum] = playerInfo[4] #Store sync value
            score = playerInfo[3]
            opponentNum = 0

            #Set the reply to equal the movement direction of the opponent's paddle
            if playerNum == 0:
                reply[1] = paddleDirection[1]
                opponentNum = 1
            else:
                reply[1] = paddleDirection[0]
                opponentNum = 0

            #Compare sync values to determine source of synchronization error
            if playerSync[playerNum] < playerSync[opponentNum] : #If current player sync less than opponent, changes value to match opponent
                reply[0] = ballPosition[opponentNum] 
                reply[2] = score
                reply[3] = playerSync[opponentNum]
            else: #Otherwise, return current player's values
                reply[0] = ballPosition[playerNum] 
                reply[2] = score
                reply[3] = playerSync[playerNum]
                
            playerSocket.send(pickle.dumps(reply)) #Send updated ball position, paddle movement direction, current score
       
       #If an error occurs, break loop
        except:
            break   
    
    #Close connection, end loop
    playerSocket.close()


currPlayer = 0 #Initialize variable to indicate current player

#The main loop that connects the client to the server and begins a thread to update paddle positions to interested parties,
#alternating between players
while True:

    #Establish client connection
    playerSocket, playerAddress = server.accept()

    #Begin communication thread for the client
    playerThread = threading.Thread(target=player_handle, args=(playerSocket,currPlayer,))
    playerThread.start()

    currPlayer +=1 #Update for next player

    if currPlayer == 2:
        both_players_connected.set() #Start game once 2 players have joined
        currPlayer = 0 #Reset player waitlist counter?
        both_players_connected.clear() #Reset event so it waits for 2 new players to connect


#Close server
server.close()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games