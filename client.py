import ipaddress
import socket 


if __name__ == "__main__":
    # recieves input from client which contains the IP address, port number of the server, and a message to send to that server
    target_IP = input("Please enter the target ip address: ")
    target_port = int(input("Please enter the target port number of the server: "))
    message = input("What is your message? ")

    # creates the socket for our communication
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #attempts to connect to the server
    while True:
        try:
            myTCPSocket.connect((target_IP, target_port))
            break

        #if there is an error with connecting
        except:
            print("An error has occurred please try again")
            target_IP = input("Please enter the target ip address: ")
            target_port = int(input("Please enter the target port number of the server: "))
            message = input("What is your message? ")

    #loop to send and recieve the messages 
    while True:
        #sends the message and encodes it
        myTCPSocket.send(bytearray(str(message), encoding='utf-8'))
        
        #recieves and prints the response
        response = myTCPSocket.recv(500).decode()
        print("Returned message: ", response)

        #checks to see if the client would want to continue
        if input("Would you like to change your message? (Y/n)").lower() == 'y':
            print()
            message = input("What is your new message?")
        else:
            break

    #closes the socket
    myTCPSocket.close()