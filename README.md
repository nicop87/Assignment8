# IOT Implementation 
By Leo Pan and Nicolas Piker for CECS 327

## Dependencies
For Linux we need to install psycopg2 for querying our database. Also used dotenv to read our env variables.

sudo apt install python3-psycopg2
sudo apt install python3-dotenv


## Opening a port
In order to use this code, first you need access to the router that you are currently using. When you are in the settings, you need to allows a port to forward to your computer. Make sure to use a port that is not in use for another task.

## Creating a server
To create a server, it will ask you for the IP address of your device running the code and a port number. You will use your private IP address and the port number that you opened in the pervious step. You also want to get the public IP address of your computer for the next step.

In order for your server to connect to a database, you will need a .env file in this structure:
```
NEON_DBNAME=    *Fill in*
NEON_USER=      *Fill in*
NEON_PASSWORD=  *Fill in*
NEON_HOST=      *Fill in*
```

## Starting the client
The code will ask you for a IP address and you will use the public IP of the device running the computer. You then input the same port number that you have been using and a message that you would like to send. The server will take your message and return it will in all capital letters. When it is ready it will prompt you on the console for which sensors info you would like to see, input the proper number 1-3 and the server will give you a response!
