import time
import serial
from threading import Thread


ser = serial.Serial(
#    port='/dev/ttyACM0',\
    port='COM7',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

print("connected to: " + ser.portstr)
 


def switch_led(button_index , is_turn_on):
    if ser.is_open:

        if is_turn_on:
            cmd = ("/set Led" + str(button_index) + " on").encode()
        else:
            cmd = ("/set Led" + str(button_index) + " off").encode()
    
        time.sleep(.1)
        ser.write(cmd)
        ser.flushOutput()

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

def clean_player_answers():
    global played_buttons
    played_buttons = []

def print_scores(): 
    print("* Current Scores")
    for i in range(nb_players):
        print("Player "+ str(i) + " : " + str(player_scores[i]))
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

        global is_game_on

        index = 0

        while index < len(questions):
            question = questions[index]
            print_scores()
            print_question(question)

            nb_current_players = nb_players
            is_correct = False
            clean_player_answers()

            already_answer = []


            while is_correct == False and nb_current_players > 0: 

                if len(played_buttons) > 0:
                    id_player = played_buttons.pop()
                    if id_player >= 0:

                        nb_current_players -= 1
                        print("For player " + str(id_player)  + ", the answer is correct (y/n) ?")
                        reponse = str(input())

                        print("")
                        if reponse == "y":
                            is_correct = True
                        else: 
                            already_answer.append(id_player)
                            print_question(question)
        
                        clean_player_answers()
                    else:
                        print("ERROR : Did not recognize the player : " + str(id_player))

                time.sleep(0.1)
                if is_correct == True:
                   player_scores[id_player] += QUESTION_SCORE
            index += 1
        is_game_on = False


##### Config 
nb_players = 4 
nb_question = 10
player_scores = [0] * nb_players
QUESTION_SCORE = 1

played_buttons = []

questions = parse_questions_file("questions.txt")

SerialThread()
GameThread()
is_game_on = True

while is_game_on:
    time.sleep(0.1)

print("Score Final: ")
print_scores()

ser.close()

