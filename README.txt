Contact Info
============

Group Members & Email Addresses:

    Natalie O'Leary, natalie.oleary@uky.edu
    Daniel Alvarado, dal240@uky.edu

Versioning
==========

Github Link: https://github.com/Dasikio/CS371-Pong.git

General Info
============
This file describes how to install/run your program and anything else you think the user should know

1. To install this program you must have the most up-to date version of pongClient.py and pongServer.py inside the pong folder provided by the TA.
2. To run the program you must open a command terminal in your code editor of choice, make sure your terminal is in the pong folder which contains pongClient.py and pongServer.py.
3. In the terminal you want to first run pongServer.py with the following command: python3 pongServer.py | you will know it is running as it will display the message "Listening on 'IPv4 address'"
4. Followed by the server, you want to run pongClient.py with the following command: python3 pongClient.py
5. Once the client is running, input the IPv4 address displayed in the server, as well as the port number 12321.

Note: In order for the game to run there must be 2 clients connected to the server, as the server will wait for 2 connections to start the game.


Install Instructions
====================

Run the following line to install the required libraries for this project:

`pip3 install -r requirements.txt`

Known Bugs
==========
- The server doesn't work because the logic isn't yet written.
- The client doesn't speak to the server

