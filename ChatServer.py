# ChatServer.py
# Jennifer Bonda

from socket import *
import sys
import json
import threading

#List that contains all currently connected clients
clientsConnected = []
welcomingSocket = None

#Function broadcasting determines which clients get sent broadcasted messages
def broadcasting(senderNickname, message, timestamp):
    #Broadcast message dictionary
    broadcastMessage = {
        "type": "broadcast",
        "nickname": senderNickname,
        "message": message,
        "timestamp": timestamp
    }
    jsonBroadcast = json.dumps(broadcastMessage)
    encodedBroadcast = jsonBroadcast.encode()

    #Loops through all connected clients to send messages
    for connectionSocket in clientsConnected:
        connectionSocket.send(encodedBroadcast)

#Function handleClient that handles the unique nickname logic and disconnection logic
def handleClient(connectionSocket, address):
    clientSentence = connectionSocket.recv(1024)
    clientSentence = clientSentence.decode()
    messageParsed = json.loads(clientSentence)

    #Pulling data from the nickname type message
    nickname = messageParsed['nickname']
    senderNickname = nickname
    timestamp = messageParsed['timestamp']
    clientID = messageParsed['clientID']
    IPAddress = messageParsed['ip']

    while True:
        #If the nickname is already used, send error message to client
        if nickname in (client["nickname"] for client in clientsConnected):
            
            print("error: Nickname already taken.")
            errorMessage = { "type": "error", 
                            "message": "Nickname already taken" }
            jsonErrorMessage = json.dumps(errorMessage)
            encodedErrorMessage = jsonErrorMessage.encode()
            connectionSocket.send(encodedErrorMessage)

            newNicknameMessage = connectionSocket.recv(1024).decode()
            newNickname = json.loads(newNicknameMessage)["nickname"]
            
            if newNickname in (client["nickname"] for client in clientsConnected):
                continue #Prompt again if nickname still used
            
            nickname = newNickname    

        else:
            #If the nickname is unique, then add client info to list of connected clients
            clientsConnected.append({"nickname": nickname, "clientID": clientID, "socket": connectionSocket, "raddr": address[1]})
            nonErrorMessage = { "type": "noError", 
                                "message": "Nickname is valid" }
            jsonNonErrorMessage = json.dumps(nonErrorMessage)
            encodedNonErrorMessage = jsonNonErrorMessage.encode()
            connectionSocket.send(encodedNonErrorMessage)
            #Print that the client is connected
            print(timestamp, "::", nickname, ": connected.")
            break

    while True:
        client = connectionSocket.recv(1024)
        client = client.decode()
        clientMessage = json.loads(client)
        
        #Checking if message type is disconnect to disconnect client
        if clientMessage['type'] == "disconnect":
            timestamp = clientMessage['timestamp']
            print(timestamp,"::", nickname,": disconnected.")
            clientsConnected.remove({"nickname": nickname, "clientID": clientID, "socket": connectionSocket, "raddr": address[1]})
            break
        #Checking if message type is message to print out client message data
        elif clientMessage['type'] == "message":
            message = clientMessage['message']
            messageSize = len(clientMessage['message'])
            timestamp = clientMessage['timestamp']
            
            print(f"Received: IP: {IPAddress}, Port: {address[1]}, Client-Nickname: {nickname}, ClientID: {clientID}, Date/Time: {timestamp}, Msg-Size: {messageSize}")

            #Broadcast message dictionary
            broadcastMessage = {
                "type": "broadcast",
                "nickname": senderNickname,
                "message": message,
                "timestamp": timestamp
            }


            broadcastedToString = ""
            for client in clientsConnected:

                #Broadcasting messages to all clients that are not the sender
                if client["nickname"] != senderNickname:
                    jsonBroadcast = json.dumps(broadcastMessage)
                    encodedBroadcastMessage = jsonBroadcast.encode()
                    client['socket'].send(encodedBroadcastMessage)
                    broadcastedToString += client['nickname'] + ", "
                    #print(f"broadcasted to: {client['nickname']}")
            broadcastedToString = broadcastedToString.rstrip(", ") 
            print(f"Broadcasted: {broadcastedToString}")

    connectionSocket.close()
#End of handleClient function

#Function closingServer that exits the program
def closingServer():
    global welcomingSocket
    if welcomingSocket:
        welcomingSocket.close()
    for client in clientsConnected:
        client['socket'].close()
    sys.exit(0)

#Checking if correct number of arguments given
args = sys.argv
if len(args) != 2:
    print ("Usage: python3 ChatServer.py port")
    exit()
try:    
    if int(args[1]) > 0 and int(args[1]) < 65536:
        port = int(args[1])
    else:
        print("ERR -arg x")
        exit()
except ValueError:
    print("ERR -arg x")
    exit()
    
try:
    #Create welcoming socket using the given port
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.bind(('', port))
    welcomeSocket.listen(1)

    #Catches the error of using same port number
except OSError as e:
    print(f"ERR - cannot create ChatServer socket using port number {port}")
    exit()


while True:
    try:
        #Checking if server should continue running
        connectionSocket, address = welcomeSocket.accept()

        client_thread = threading.Thread(target=handleClient, args=(connectionSocket, address))
        client_thread.start()
    #Handles Ctrl-C
    except KeyboardInterrupt:
        print("\n")
        closingServer()

