# TCP-Chat-Application

Source Programs: ChatClient.py and ChatServer.py

- How to run and compile the chat application:
    * Log into your account on the two VCU VM host machines through a terminal
    * Run ChatServer.py first on SSH: 10.0.0.2 with command "python3 ChatServer.py <port>"
        - Port must be a positive integer less than 65536
    * Run ChatClient.py second on SSH: 10.0.0.1 with command "python3 ChatClient.py <IP/HostName> <port> <nickname> <clientID>"
        - IP must be either 10.0.0.1 or 10.0.0.2
        - HostName must be "egr-v-cmsc440-1" or "egr-v-cmsc440-2"
        - Port must be integer between 10000-11000
        - Nickname can be made up of any characters
        - clientID must be a positive integer
    * Type messages into terminal to chat and "disconnect" to disconnect clients
    * CTRL-C gracefully terminates ChatServer.py

