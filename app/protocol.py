import time
import serial


##### Config 
max_player = 4
nb_question = 10
player_scores = [0] * max_player

################# 

ser = serial.Serial(
    port='/dev/ttyACM0',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

print("connected to: " + ser.portstr)
count=1



def switch_led(button_index , turn_off = True):
    if ser.is_open:

        if turn_off:
            cmd = ("/set Led" + str(button_index) + " on").encode()
        else:
            cmd = ("/set Led" + str(button_index) + " off").encode()
    
        time.sleep(.1)
        print(cmd)
        ser.write(cmd)
        ser.flushOutput()

while True:
    i = i + 1
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8") 
        line = line.strip()

        if line.split(" ")[-1] == "pressed":

            id_player = int(line.split(" ")[0][-1])
            print("Button " + str(id_player) + " is pressed")

            if id_player >= max_player:
                print("Error index player = " , id_player)

 
    time.sleep(0.1)

ser.close()



