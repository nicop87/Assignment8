import socket
import psycopg2
import os
from dotenv import load_dotenv

# main function for Server driver
if __name__ == "__main__":
    # load profile and passwords from env file
    load_dotenv()

    # connect to neon database
    conn = psycopg2.connect(
    dbname=os.getenv("NEON_DBNAME"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    host=os.getenv("NEON_HOST"),
    port=5432,
    sslmode="require"
    )

    # two caches in memory to keep reduce redundant queries 
    fridge_cache = []
    dishwasher_cache = []

    # set up cursor to query database
    # this will fetch all fresh data at once at startup of server
    cur = conn.cursor()
    # cur.execute('SELECT * FROM "SmartDevices_virtual";')
    # print(cur.fetchall())

    # cur.close()
    # conn.close()


    # creates the TCP socket
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # prompts user for the current ip address the server is on, and what port to open to TCP connections
    myIP = input("Current IP address: ")
    myPort = int(input("Port to open: "))

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

