from threading import Thread
from websocket_server import WebsocketServer


import sys
import time
import json
import serial


##### Default Config
config = {
    "device" : "COM7",
    "question_file" : "questions.txt",
    "nb_players" : 4,
    "points_per_good_answer" : 1,
    "points_per_wrong_answer" : 0
}

during_question = False

def serial_init():
    ser = serial.Serial(
        port='/dev/ttyACM1',\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=0)

    if ser.isOpen():
        print("connected to: " + ser.portstr)
    else:
        print("ERROR: Could not connect to the Arduino board on the device:" + config["device"])
        sys.exit()
    return ser

def switch_led(button_index , is_turn_on):
    if ser.is_open:

        if is_turn_on:
            cmd = ("/set Led" + str(button_index) + " on").encode()
        else:
            cmd = ("/set Led" + str(button_index) + " off").encode()

        time.sleep(.1)
        ser.write(cmd)
        ser.flushOutput()

class SerialThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global played_buttons
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8") 
                line = line.strip()

                if line.split(" ")[-1] == "pressed":

                    id_player = int(line.split(" ")[0][-1])
                    print(line)
                    played_buttons.append(id_player)
            time.sleep(0.1)

def new_client(client, server):
	print("New client connected and was given id %d" % client['id'])

def client_left(client, server):
	print("Client(%d) disconnected" % client['id'])

def message_received(client, server, message):
    global during_question, nb_players, nb_questions, players,questions

    print("Received message from Client(%d): %s" % (client['id'], message))
    data = json.loads(message)
    if data["action"] == "connection": 
        print("New Client " + str(data["client_type"] + " : " + str(data["client_name"])))
    elif data["action"] == "startQuestion":
        during_question = True
    elif data["action"] == "stopQuestion":
        during_question = False
    elif data["action"] == "initGame":
        nb_players = int(data["nb_players"])
        nb_questions = int(data["nb_questions"])
        players = data["players"]
        questions = data["questions"]
        during_question = False

PORT=9001
server = WebsocketServer(port = PORT)

class WSServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(slef):
        server.set_fn_new_client(new_client)
        server.set_fn_client_left(client_left)
        server.set_fn_message_received(message_received)
        server.run_forever()

played_buttons = []

WSServerThread()

ser = serial_init()
SerialThread()

nb_players = 0

while True:
    if len(played_buttons) > 0: 
        if during_question:
            player_id = played_buttons.pop()
            if player_id >= 0 and player_id < nb_players:

                message = json.dumps({
                    "action" : "button_pressed",
                    "player_id" : player_id
                })
                server.send_message_to_all(message)
                print(message)
        else:
            played_buttons = []

    time.sleep(0.1)

ser.close()