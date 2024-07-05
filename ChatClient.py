# ChatClient.py
# Jennifer Bonda

from socket import *
import sys
import datetime
import json
import threading

args = sys.argv
messageCounter = 0
charCounter = 0
messagesReceived = 0
charactersReceived = 0

#Checking for correct number of arguments
if len(args) != 5:
    print ("Usage: python3 ChatClient.py hostname/IP port nickname clientID")
    exit()
IP = args[1] 
nickname = args[3]
currentDateTime = datetime.datetime.now()

#Function receiveMessage allows for broadcasting of other clients' messages
def receiveMessage(client_socket, nickname):
    global messagesReceived
    global charactersReceived

    while True:
        try:
            message = client_socket.recv(1024).decode()
            messagesReceived = messagesReceived + 1 #Finding number of messages received

            messageParsed = json.loads(message)
            message = messageParsed["message"]

            charactersReceived = charactersReceived + len(message) #Finding number of characters received
            
            if messageParsed["type"] == "broadcast" and messageParsed["nickname"] != nickname:
                sender_nickname = messageParsed["nickname"]
                message_content = messageParsed["message"]
                timestamp = messageParsed["timestamp"]
                print(f"{timestamp} :: {sender_nickname}: {message_content}") #Printing the sent messages of other clients
                
            else:
                print(f"{messageParsed['timestamp']} :: {messageParsed['nickname']}: {messageParsed['message']}")
        
    
        except Exception as e:
            print("") #Disregarding errors that happen when client has disconnected
            break
    
#Only two possible IP addresses and hosts 
#If given the hostname, then assign it to the IP address
if IP == 'egr-v-cmsc440-2':
    IP = '10.0.0.2'
if IP == 'egr-v-cmsc440-1':
    IP = '10.0.0.1'

#Error Handling Section:

#Only two possible IP addresses
if IP != '10.0.0.1' and IP!= '10.0.0.2':
    print("ERR -arg 1")
    exit()

#Checking if port number is between 10000-11000 and if it is correct type
try:
    if int(args[2]) > 9999 and int(args[2]) < 11001:
        port = int(args[2])
        pass
    else:
        print("ERR -arg 2")
        exit()    
except ValueError:
    print("ERR -arg 2")
    exit()

#Checking if clientID positive and correct type
try:
    if int(args[4]) >= 0:
        clientID = int(args[4])
        pass
    else:
        print("ERR -arg 4")
        exit()
except ValueError:
    print("ERR -arg 4")
    exit()

#Create socket and connect to server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((IP, port))

#Nickname message dictionary
message = {
    "type": "nickname",
    "nickname": nickname,
    "clientID": clientID,
    "timestamp": str(currentDateTime),
    "ip": IP
}

#Sending nickname message dictionary to server
json_message = json.dumps(message)
encoded_message = json_message.encode()
clientSocket.send(encoded_message)

#Receive and process the response from server
errorResponse = clientSocket.recv(1024).decode()
errorResponseParsed = json.loads(errorResponse)

#If the type of message received is "error" then get new nickname input
if "type" in errorResponseParsed and errorResponseParsed["type"] == "error":
    print("Error:", errorResponseParsed["message"])

    while True:
        new_nickname = input("Please enter a different nickname: ")
        if new_nickname != nickname:  #New nickname is different from old nickname
            
            
            newNicknameMessage = {
                "nickname": new_nickname
            }
            #Sending new nickname to the server to check
            jsonNewNicknameMessage = json.dumps(newNicknameMessage)
            encodedNewNicknameMessage = jsonNewNicknameMessage.encode()
            clientSocket.send(encodedNewNicknameMessage)

            serverResponse = clientSocket.recv(1024).decode()
            serverResponseParsed = json.loads(serverResponse)

            #New nickname is valid
            if "type" in serverResponseParsed and serverResponseParsed["type"] == "noError":
                nickname = new_nickname
                break
            else:
                
                print("Error:", serverResponseParsed["message"])
        else:
            print("Error: New nickname should be different from the old one.")

else:
    #No error so the chat starts
    print(f"ChatClient started with server IP: {IP}, port: {port}, nickname: {nickname}, client ID: {clientID}, Date/Time: {currentDateTime}")

disconnected = False

#Threading starts
threading.Thread(target=receiveMessage, args=(clientSocket, nickname)).start()

print('Enter message:')
while True:
    clientSentence = input('') #Reading input
    messageCounter = messageCounter + 1 #Increment the number of messages sent
    charCounter = len(clientSentence) + charCounter #Increment the number of characters sent
    
    if clientSentence == "disconnect":

        newCurrentDateTime = datetime.datetime.now()

        #Disconnect message dictionary
        disconnectMessage = {
            "type": "disconnect",
            "nickname": nickname,
            "clientID": clientID,
            "timestamp": str(newCurrentDateTime)
        }

        #Sending disconnect message to server
        jsonMessage = json.dumps(disconnectMessage)
        encodedMessage = jsonMessage.encode()
        clientSocket.send(encodedMessage)

        messageCounter = messageCounter - 1 #"disconnect" is not counted as a message
        charCounter = charCounter - len(clientSentence)#"disconnect" is not counted as a message
        disconnected = True
        newCurrentDateTime = datetime.datetime.now()
        #Printing the summary after disconnect
        print(f"Summary: start: {currentDateTime}, end: {newCurrentDateTime}, msg sent: {messageCounter}, msg rcv: {messagesReceived}, char sent: {charCounter}, char rcv: {charactersReceived}")
        break

    mostCurrentDateTime = datetime.datetime.now()

    #Type message dictionary
    message2 = {
        "type": "message",
        "nickname": nickname,
        "message": clientSentence,
        "timestamp": str(mostCurrentDateTime)
    }

    #Sending type message dictionary to server
    jsonMessage = json.dumps(message2)
    encodedMessage = jsonMessage.encode()
    clientSocket.send(encodedMessage)

#Close the socket
clientSocket.close()
