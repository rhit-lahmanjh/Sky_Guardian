import socket 
import threading
import time

#beta_address = ('192.168.0.248',8889)
alpha_address = ('192.168.0.140',8889)


local1_address = ('192.168.0.245',9010)
#local2_address = ('192.168.0.146',9011)

sock1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock1.bind(local1_address)
#sock2.bind(local2_address)

def send(message,delay):
    try:
        sock1.sendto(message.encode(),alpha_address)
        #sock2.sendto(message.encode(),beta_address)
        print("Sending the message" + message)
    except Exception as e:
        print("error sending: " + str(e))

    time.sleep(delay)

def receive():
    while True:
        try:
            response1,ip_address = sock1.recvfrom(128)
            #response2,ip_address = sock2.recvfrom(128)
            print("Received message: from Alpha Edu: " + response1.decode(encoding='utf-8'))
            #print("Received message: from Beta Edu: " + response2.decode(encoding='utf-8'))
        except Exception as e:
            sock1.close()
            #sock2.close()
            print("Error receiving: " + str(e))
            break

receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

box_leg_distance = 100
yaw_angle = 90
yaw_direction = 'cw'
send("command",3)
send("battery?",3)
send("takeoff",8)
for i in range(4):
    send("forward " + str(box_leg_distance),4)
    send("cw " + str(yaw_angle), 3)
send("land",5)
print("Your mom sucks my cock")
send("battery?",3)
sock1.close()
#sock2.close()