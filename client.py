import ipaddress
import socket 


if __name__ == "__main__":
    # recieves input from client which contains the IP address, port number of the server, and a message to send to that server
    target_IP = input("Target IP address: ")
    target_port = int(input("Target Port: "))
    validMessage = ['What is the average moisture inside my kitchen fridge in the past three hours?',
                    'What is the average water consumption per cycle in my smart dishwasher?',
                    'Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?']
    print("Here are the valid questions: ")
    num=1
    for i in validMessage:
        print(str(num) + '. ' + i)
        num+=1
    try:
        message = int(input())
    except:
        message = int(input('Please choose either 1, 2, or 3: '))
    while (message > 4 and message < 0):
        print('Sorry, this query cannot be processed. Please try one of the following:')
        num = 1
        for i in validMessage:
            print(str(num) + '. ' + i)
            num+=1
        message = int(input())

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

    #loop to send and recieve the messages 
    while True:
        #sends the message and encodes it
        myTCPSocket.send(bytearray(str(message), encoding='utf-8'))
        
        #recieves and prints the response
        response = myTCPSocket.recv(500).decode()
        if message == 1:
            print("The average moisture inside the kitchen is " + response)
        elif message == 2:
            print("The average water consumption per cycle in your dishwasher is " + response)
        else:
            print("The device that consumed the most electricity is " + response)

        #checks to see if the client would want to continue
        if input("Would you like to change your message? (Y/n)").lower() == 'y':
            print()
            message = int(input("What is your new message?"))
        else:
            break

    #closes the socket
    myTCPSocket.close()