from threading import Thread
import argparse
import sys
import time
import json
import serial
import termios
import select
import tty

from websocket_server import WebsocketServer

nb_players = 0
during_question = False
played_buttons = []
allowed_colors = ["red", "yellow" , "white" , "blue" , "green"]

# Keyboard mapping for the interactive mode, type r will simulate a red button pressed event
color_inputs = {'r': "red" , 'y': "yellow" , 'w' : "white" , 'g' : "green" , 'b' : "blue" }

PORT=9001
server = WebsocketServer(port = PORT)

def serial_init(device):
    ser = serial.Serial(
        port=device,\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=0)

    if ser.isOpen():
        print("connected to: " + ser.portstr)
    else:
        print("ERROR: Could not connect to the Arduino board on the device: " + config["device"])
        sys.exit()
    return ser


def switch_led(color, is_turn_on, all_leds):
    if ser.is_open:
        if is_turn_on:
            if all_leds:
                cmd = ("/set allLeds on\n").encode()
            else:
                cmd = ("/set " + color + "Led on\n").encode()
        else:
            if all_leds:
                cmd = ("/set allLeds off\n").encode()
            else:
                cmd = ("/set " + color + "Led off\n").encode()

        time.sleep(.05)
        ser.write(cmd)
        ser.flushOutput()



class SerialThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global played_buttons

        switchLeds(False)
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8") 
                line = line.strip()

                if line.split(" ")[-1] == "pressed":

                    player_color = line.split(" ")[0]
                    played_buttons.append(player_color)
            time.sleep(0.1)


def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def switchLeds(on):
    if on:
        for color in allowed_colors:
            switch_led(color, True , False)
    else:
        switch_led("red", False, True)
        

def ws_new_client(client, server):
	print("New client connected and was given id %d" % client['id'])

def ws_client_left(client, server):
	print("Client(%d) disconnected" % client['id'])

def ws_message_received(client, server, message):
    global during_question, nb_players, nb_questions, players,questions, allowed_colors

    print("Received message from Client(%d): %s" % (client['id'], message))
    data = json.loads(message)
    if data["action"] == "connection": 
        print("New Client " + str(data["client_type"] + " : " + str(data["client_name"])))
   
    elif data["action"] == "startQuestion":
        switchLeds(True)
        during_question = True
    elif data["action"] == "resumeQuestion":
        switchLeds(False)
        colors = data["colors"]
        for color in colors:
            switch_led(color, True, False)
        during_question = True
        
    elif data["action"] == "stopQuestion":
        during_question = False
        switchLeds(False)

    elif data["action"] == "initGame":

        print("Init GAME ")
        print(data)
        nb_players = int(data["nb_players"])
        nb_questions = int(data["nb_questions"])
        players = data["players"]
        questions = data["questions"]
        during_question = False

        allowed_colors = []
        for player in players:
            allowed_colors.append(player["color"])
        
    elif data["action"] == "setOneColor":
        # Only one buzzer led is on
        color = data["color"]
        switch_led("red", False, True)
        switch_led(color, True, False)
    
    elif data["action"] == "turnLedsOff":
        switchLeds(False)


class WSServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(slef):
        server.set_fn_new_client(ws_new_client)
        server.set_fn_client_left(ws_client_left)
        server.set_fn_message_received(ws_message_received)
        server.run_forever()


parser = argparse.ArgumentParser(description="Back-end for the buzzer quiz game")
parser.add_argument("-i", "--interactive", help = "Interactive Mode", action="store_true")
parser.add_argument("-d", "--device", help = "Linux Device for arduino", default="/dev/ttyACM0")

args = parser.parse_args()
if args.interactive: 
    print("Interactive Mode, arduino is not used")
else:
    ser = serial_init(args.device)
    SerialThread()

WSServerThread()

# We switch stdin into character mode to get non blocking inputs
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())


while True:

    # Input management (for interactive mode)
    if isData():
        c = sys.stdin.read(1)
        if c == '\x1b':
            break

        if args.interactive:
            if c in color_inputs.keys():
                played_buttons.append(color_inputs[c])
                print(played_buttons)

    # Button pressed management
    if len(played_buttons) > 0: 
        if during_question:
            player_color = played_buttons.pop()

            if player_color in allowed_colors:

                message = json.dumps({
                    "action" : "button_pressed",
                    "player_color" : player_color
                })
                server.send_message_to_all(message)
                print(message)
        else:
            played_buttons = []

    time.sleep(0.1)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
ser.close()
