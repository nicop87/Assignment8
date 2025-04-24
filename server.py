import socket
import ipaddress
import psycopg2
import os
from dotenv import load_env

# main function for Server driver
if __name__ == "__main__":

    # creates the TCP socket
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # prompts user for the current ip address the server is on, and what port to open to TCP connections
    myIP = input("FIX ME")
    myPort = int(input("FIX ME"))

    # binds my socket to the given ip and port number of the machine
    myTCPSocket.bind((myIP, myPort))

    # tells it to listen for any connections, sets backlog to 5
    myTCPSocket.listen(5)

    # logs the socket and ip address of any accepted connections
    incomingSocket, incomingAddress = myTCPSocket.accept()

    # continuous loop to listena nd respond to connections
    while True:
        # recieves data from client
        myData = incomingSocket.recv(100).decode()

        # also checks if the message sent is an empty array
        # to see if the client closed the connection normally, it will error if it was abrupt
        if myData == "":
            print("Client ended session, terminating connection")
            break

        # prints the incoming message
        print("CLIENT: ", myData)

        # converts recieved message into all upper case and sends it back to sender
        new_msg = myData.upper()
        incomingSocket.send(bytearray(str(new_msg), encoding='utf-8'))
        print("SENDING RESPONSE...")
        print()

    # terminate connection safely, although this code won't reach here due to the infinite loop
    incomingSocket.close()

