# Import the built-in socket and time modules
import socket
import time
import threading
import pickle
import csv

with open("Drone1.csv", 'r') as file:
  csvreader = csv.reader(file)
  for row in csvreader:
    print(row)


# Pickle code for reading from a txt file
# try:
#   with open("ip_fileDrone1.txt", "rb") as file_handler:
#     try:
#       userIPaddress1, portValue = pickle.load(file_handler)
#     except:
#       print("This file has no data")
#   with open("ip_fileDrone2.txt", "rb") as file_handler:
#     try:
#       userIPaddress2, portValue = pickle.load(file_handler)
#     except:
#       print("This file has no data")
# except:
#   print("File does not exist")
# input()

# IP and port of Tello
tello_address = (userIPaddress1, portValue)
tello2_address = (userIPaddress2, portValue)

# Create a UDP connection that we'll send the command to
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Let's be explicit and bind to a local port on our machine where Tello can send messages
sock.bind(('', 9000))
sock2.bind(('',9010))


# Function to send messages to Tello
def send(message):
  try:
    sock.sendto(message.encode(), tello_address)
    sock2.sendto(message.encode(), tello2_address)
    print("Sending message: " + message)
  except Exception as e:
    print("Error sending: " + str(e))

# Function that listens for messages from Tello and prints them to the screen
def receive():
  while True:
    try:
      response1, ip_address = sock.recvfrom(128)
      response2, ip_address = sock2.recvfrom(128)
      print("Received message from Tello Joseph: " + response1.decode(encoding='utf-8'))
      print("Received message from Tello Arvind: " + response2.decode(encoding='utf-8'))
    except Exception as e:
      sock.close()
      sock2.close()
      print("Error receiving: " + str(e))
      break

receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()


# Send Tello into command mode
send("command")

# Receive response from Tello
# Delay 3 seconds before we send the next command
time.sleep(3)

send("takeoff")

time.sleep(3)

send("land")

# # Ask Tello about battery status
# send("ap TP-Link_382E 84662019")

# # Receive battery response from Tello
# receive()
print("Connection successfully tested.")
# Close the UDP socket
sock.close()
sock2.close()