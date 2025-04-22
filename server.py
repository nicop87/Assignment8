import ipaddress
import socket 

#creates a socket
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#asks for which port to connect to 
target_IP = input("What ip address would you like to connect to? ")
port = int(input("What port would you like to connect to? "))
#connects the socket to a specific port on the computer
myTCPSocket.bind((target_IP, port))

#waits for a connection to be initiated 
myTCPSocket.listen(5)

#when it gets a connection it accepts it 
incomingSocket, incomingAddress = myTCPSocket.accept()

#continuously waiting for a message
while True:

    #gets the message, have to use decode to get rid of the 'b'
    myData = str(incomingSocket.recv(500).decode())

    #once the client ends it on their side it will send empty messages to the server
    if myData == '':
        break


    print("UNCHANGED: ", myData)

    #changes the message to all capital letters
    myData = myData.upper()
    print("ALTERED: ", myData)

    #sends the message to the connected socket
    incomingSocket.send(bytearray(str(myData), encoding='utf-8'))


