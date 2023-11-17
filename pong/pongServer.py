# =================================================================================================
# Contributing Authors:	    Daniel Alvarado, Natalie O'Leary
# Email Addresses:          dal240@uky.edu, natalie.oleary@uky.edu
# Date:                     11/16/2023
# Purpose:                  This file is the programm to handle the server needed for the local network pong game to run. It handles client connections
#                           and synchronization to enable 2 clients to play together.
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
server.listen(100) 
print(f"Listening on {SERVER}") #Once the server starts listening, it shows the IPv4 to use to connect

#Initialize variables
side = ["left","right"] #List that specifies which side each player is on (list value 0 = left player, list value 1 = right player)
paddleDirection = ["",""] #Default direction for paddles
paddlePos_Y = [240,240]
ballPosition = [(320,240),(320,240)]
ballSpeed = [[0,0],[0,0]]
score = [[0,0], [0,0]]
playerSync = [0,0]



#Create event to check that both players are connected before starting
both_players_connected = threading.Event()


#Primary function that handles information exchange between client and server -> to be run in concurrent threads
def player_handle(playerSocket,playerNum)-> None:
    # =============================================================================================================================
    # Author:   Daniel Alvarado and Natalie O'Leary
    # Purpose:  This method handles new player connections such that both clients can exchange crutial data for the game to run. Additionally,
    #           it handles any connection or communications errors.
    # Pre:      All global variables that handle player information must be set to their initial values (most cases 0), additionally it requires clients
    #           to be assignd a number (0 or 1) as to determine which paddle they will be for the duration of the game.
    # Post:     This method changes global variables paddleDirection, ballPosition, playerSync, score, and ballSpeed. Additionally once it finished it
    #           closes the socket assigned to the client. 
    # =============================================================================================================================

    #Wait until both players are connected before proceeding
    both_players_connected.wait()

    start = (640,480,side[playerNum]) #Tuple that contains values to start client (width,length, side of player)
    playerSocket.send(pickle.dumps(start)) #Send information via pickle so client receives tuple with the correct format after sending through socket
    reply = [(320, 240), "", [0, 0], 0, [0, 0], 240] #Initialize reply variable with ball coordinates, empty string for paddle direction, int for score, int for sync, tuple ballspeed, tuple paddle y locations

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
            score[playerNum] = playerInfo[3]
            ballSpeed[playerNum] = playerInfo[5]
            paddlePos_Y[playerNum] = playerInfo[6]


            opponentNum = 0

            #Set the reply to equal the movement direction of the opponent's paddle
            opponentNum = 1 - playerNum
            reply[1] = paddleDirection[opponentNum]

            #Compare sync values to determine source of synchronization error

            #If current player sync less than opponent, changes values to match opponent
            if playerSync[playerNum] < playerSync[opponentNum] : 
                reply[0] = ballPosition[opponentNum] 
                reply[2] = score[opponentNum]
                reply[3] = playerSync[opponentNum]
                reply[4] = ballSpeed[opponentNum]
                reply[5] = paddlePos_Y[playerNum]

            #If the scoreboard on the player side does not match the scoreboard on the opponent side, set the reply
            #equal to the values of the side with the most recent score update
            elif score[0] != score[1]:
                if score[0][0] > score [1][0] or score[0][1] > score [1][1]:
                    reply[0] = ballPosition[0] 
                    reply[2] = score[0]
                    reply[3] = playerSync[0]
                    reply[4] = ballSpeed[0]
                    reply[5] = paddlePos_Y[1]
                else:
                    reply[0] = ballPosition[1] 
                    reply[2] = score[1]
                    reply[3] = playerSync[1]
                    reply[4] = ballSpeed[1]
                    reply[5] = paddlePos_Y[0]
            
            #Otherwise, return current player's values
            else: 
                reply[0] = ballPosition[playerNum] 
                reply[2] = score[playerNum]
                reply[3] = playerSync[playerNum]
                reply[4] = ballSpeed[playerNum]
                reply[5] = paddlePos_Y[opponentNum] #always send oponents paddle Y coord

                
            playerSocket.send(pickle.dumps(reply)) #Send updated ball position, paddle movement direction, current score, sync value, ball speed
       
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
        both_players_connected.clear() #Reset event so it waits for 2 new player to connect


#Close server
server.close()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
 # clients are and take actions to resync the games
#Slight difference in paddle position between clients might be due to packet loss. This also leads to the problem where the ball is not sync
#between players as the position of the paddle is different, causing a different movement from the ball. 