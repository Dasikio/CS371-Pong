# =================================================================================================
# Contributing Authors:	    Daniel Alvarado, Natalie O'Leary
# Email Addresses:          dal240@uky.edu, natalie.oleary@uky.edu
# Date:                     11/17/2023
# Purpose:                  This file manages each client so that it can send and receive information to and from the server, thus enabling gameplay
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import pickle

from assets.code.helperCode import *

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0


    play_again = True

    while play_again:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements

        #Create a tuple for score that stores the player's score on the left and the opponent's score on the right
        score = [lScore, rScore]

        #Create a tuple for ball velocity
        ballSpeed = [ball.xVel, ball.yVel]

        #Store all of the necessary information into a tuple and send it to the server
        #In order: Ball x-coordinate, ball y-coordinate, direction of movement of the player paddle, current score, player's sync value, ball speed, and player's paddle location
        info = (ball.rect.x, ball.rect.y, playerPaddleObj.moving, score, sync, ballSpeed, playerPaddleObj.rect.y)
        client.send(pickle.dumps(info))

        #Receive updated information from the server: Current ball position, opponent's direction of movement, current score, opponent's sync value, opponent's ball speed, opponent's paddle position
        serverUpdate = client.recv(1024) 
        currentInfo = pickle.loads(serverUpdate) 

        #Loading data into corresponding client variables
        opponentPaddleObj.moving = currentInfo[1]
        ballPosition = currentInfo[0]
        ball.rect.x = ballPosition[0]
        ball.rect.y = ballPosition[1]
        receivedScore = currentInfo[2]
        sync = currentInfo[3]
        ballSpeed = currentInfo[4]
        
        #Update the position of the opponent's paddle
        opponentPaddleObj.rect.y = currentInfo[5]

        #Update the ball speed
        ball.xVel = ballSpeed[0]
        ball.yVel = ballSpeed[1]
        
        #Update scores
        lScore = receivedScore[0]
        rScore = receivedScore[1]

        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message and prompt for play again
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2-100)
            screen.blit(textSurface, textRect)

            #Included functionality for a "Play Again" feature below:

            #Each user is prompted to press "Y" to play again or "N" to exit
            play_again_text1 = "Press Y to play again"
            play_again_text2 = "or"
            play_again_text3 = "N to exit"
            play_again_surface1 = winFont.render(play_again_text1, False, WHITE, (0,0,0))
            play_again_surface2 = winFont.render(play_again_text2, False, WHITE, (0,0,0))
            play_again_surface3 = winFont.render(play_again_text3, False, WHITE, (0,0,0))
            play_again_rect1 = play_again_surface1.get_rect()
            play_again_rect2 = play_again_surface2.get_rect()
            play_again_rect3 = play_again_surface3.get_rect()
            play_again_rect1.center = ((screenWidth/2), screenHeight/2)
            play_again_rect2.center = ((screenWidth/2), screenHeight/2 + 50)
            play_again_rect3.center = ((screenWidth/2), screenHeight/2 + 90)
            screen.blit(play_again_surface1, play_again_rect1)
            screen.blit(play_again_surface2, play_again_rect2)
            screen.blit(play_again_surface3, play_again_rect3)

            pygame.display.flip()

            #Wait for user input
            #If a user presses Y, the game begins again, resetting the score and sending the ball left
            #If a user presses N, the server and the game window close
            #If a user closes the game window, the game ends
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            # Play again
                            waiting_for_input = False
                            play_again = True
                            lScore = 0
                            rScore = 0
                            ball.reset(nowGoing="left")
                        elif event.key == pygame.K_n:
                            # Exit
                            waiting_for_input = False
                            play_again = False

        else:

            # ==== Ball Logic =====================================================================
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.flip()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game



        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the required information from your server (screen width, height & player paddle, "left" or "right")
    client.connect((ip, int(port)))
    data = client.recv(1024) # Adjust the buffer size
    start = pickle.loads(data)

    # If you have messages you'd like to show the user use the errorLabel widget like so
    errorLabel.config(text=f"Some update text. You input: IP: {ip}, Port: {port}")
    # You may or may not need to call this, depending on how many times you update the label
    errorLabel.update()     

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(start[0], start[1], start[2], client)  # User will be either left or right paddle
    app.quit()         # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    startScreen()
    
    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))

