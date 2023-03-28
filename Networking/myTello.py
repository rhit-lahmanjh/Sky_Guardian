
# Import the built-in socket and time modules
import socket
import time
import threading

# IP and port of Tello
tello_address = ('192.168.0.248', 8889)
tello2_address = ('192.168.0.140',8889)

# Create a UDP connection that we'll send the command to tello drone
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
      print("Received message from Tello One: " + response1.decode(encoding='utf-8'))
      print("Received message from Tello Two: " + response2.decode(encoding='utf-8'))
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
print("Mission accomplished my dudes")
# Close the UDP socket
sock.close()
sock2.close()