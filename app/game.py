from threading import Thread

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


def serial_init():
    ser = serial.Serial(
    #    port='/dev/ttyACM0',\
        port=config["device"],\
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

def parse_config_file():
    global config
    # Opening JSON file
    config_file = open("config.json", 'r' , encoding="utf-8")
    config = json.load(config_file)
    config_file.close()



def parse_questions_file(file):
    result =[]
    with open(file, encoding='utf8') as f:
        lines = f.readlines()

    for line in lines:
        if line == "":
            continue

        split_line = line.strip().split(':')
        entete = split_line[0].lower()
        if entete == "question":
            entry = [ ':'.join(split_line[1::]) ]
        elif entete == "bonne reponse":
            bonne_reponse = split_line[1].strip()
            entry.append(bonne_reponse)
            result.append(entry)
    return result

def print_scores():
    print("* Current Scores")
    for i in range(config["nb_players"]):
        print(player_names[i] + " : " + str(player_scores[i]))
    print("****")

def print_question(question):
    print("Question: " + question[0])
    print("Reponse: " + question[1])

class SerialThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8") 
                line = line.strip()

                if line.split(" ")[-1] == "pressed":

                    id_player = int(line.split(" ")[0][-1])
                    print("Button " + str(id_player) + " is pressed")
                    played_buttons.append(id_player)
            time.sleep(0.1)


class GameThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):

        global is_game_on, played_buttons
        for question in questions:

            print_scores()
            print_question(question)

            nb_current_players = config["nb_players"]
            is_correct = False
            played_buttons = []

            already_answer = []

            while not is_correct and nb_current_players > 0:

                if len(played_buttons) > 0:
                    id_player = played_buttons.pop()
                    if id_player >= 0:

                        nb_current_players -= 1
                        print(player_names[id_player]  + ", the answer is correct (y/n) ?")
                        reponse = str(input())

                        print("")
                        if reponse == "y":
                            is_correct = True
                        else:
                            already_answer.append(id_player)
                            print_question(question)

                    else:
                        print("ERROR : Did not recognize the player : " + str(id_player))

                    played_buttons = []

                if is_correct:
                    player_scores[id_player] += config["points_per_good_answer"]
                else:
                    player_scores[id_player] += config["points_per_wrong_answer"]

                time.sleep(0.1)
        is_game_on = False


parse_config_file()
questions = parse_questions_file(config["question_file"])


player_scores = [0] * config["nb_players"]
player_names = { k : "Player " + str(k) for k in range(config["nb_players"])}

played_buttons = []

ser = serial_init()
SerialThread()

# Launch a game
is_game_on = True
GameThread()

while is_game_on:
    time.sleep(0.1)

print("Score Final: ")
print_scores()

ser.close()