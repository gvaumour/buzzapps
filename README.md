# Buzzer App 

A small blind test arcade game
Several modes are planned: 
    - blind test game: this is the main 
    - 

# Description 

![image](schema.png)

The project is composed of several parts: 
    - The arduino board
    - The python server 
    - The web interface

## The arduino board 

I have used an arduino board, but you can use any board that you have available. 
The board has 5 push buttons connected to it and send a message through serial each time a button is pressed.
The program here is voluntary kept as simple as possible to increase flexibility on the game.

## The python server 

The python server acts as the back-end of the game.
It centralized the information about the game and take decision. 
    - It handles serial messages coming from the Arduino board
    - It runs a websocket server that the game master interface connects to


## The game master interface 

The game master interface:
    - It allows to configure and launch a game
    - Loading blindtest playlists: an example can be found in the interface subfolder

# Install



# Running 

1) Flash the arduino code and connect it to 
To launch the game master 