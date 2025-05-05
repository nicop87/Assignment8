import socket
import psycopg2
import os
import time
from dotenv import load_dotenv

def refresh_cache(fridge_names, dishwasher_names, fridge_cache, dishwasher_cache):
    # connect to neon database and make cursor to query
    conn = psycopg2.connect(
    dbname=os.getenv("NEON_DBNAME"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    host=os.getenv("NEON_HOST"),
    port=5432,
    sslmode="require"
    )

    cur = conn.cursor()

    f_recent_row = 0 # remembers the last row it queried in the fridges_virtual table so it doesn't query them again
    d_recent_row = 0 # remembers the last row it queried in the dishwashers_virtual table so it doesn't query them again

    # first grabs all names of appliances and matches them to their UID from the metadata for lookup later
    cur.execute("""
    SELECT "assetUid", "customAttributes"->>'name'
    FROM fridges_metadata;
    """)
    entry = cur.fetchone()
    while(entry != None):
        fridge_names[entry[0]] = entry[1]
        entry = cur.fetchone()

    cur.execute("""
    SELECT "assetUid", "customAttributes"->>'name'
    FROM dishwashers_metadata;
    """)
    entry = cur.fetchone()
    while(entry != None):
        dishwasher_names[entry[0]] = entry[1]
        entry = cur.fetchone()

    # Now we fetch all the relevant data we need from the database and cache it
    # First it filters and retrieves all fridge data
    cur.execute("""
    SELECT
        f.id,
        "payload"->>'parent_asset_uid',
        ammeter.value AS ammeter_value,
        moisture.value AS moisture_value,
        "payload"->>'timestamp'
    FROM fridges_virtual f
    LEFT JOIN json_each(f."payload") AS ammeter(key, value)
        ON ammeter.key ILIKE '%Ammeter%'
    LEFT JOIN json_each(f."payload") AS moisture(key, value)
        ON moisture.key ILIKE '%MoistureMeter%';
    """)

    entry = cur.fetchone()
    while(entry != None):
        f_recent_row = entry[0]
        # caches the UID, Ammeter value, Moisture Value, and Unix timestamp
        row = [entry[1], entry[2], entry[3], entry[4]]
        fridge_cache.append(row)
        entry = cur.fetchone()

    # Next it filters and retrieves all dishwasher data
    cur.execute("""
    SELECT
        d.id,
        "payload"->>'parent_asset_uid',
        ammeter.value AS ammeter_value,
        flow.value AS flow_value,
        "payload"->>'timestamp'
    FROM dishwashers_virtual d
    LEFT JOIN json_each(d."payload") AS ammeter(key, value)
        ON ammeter.key ILIKE '%Ammeter%'
    LEFT JOIN json_each(d."payload") AS flow(key, value)
        ON flow.key ILIKE '%CurrentFlow%';
    """)

    entry = cur.fetchone()
    while(entry != None):
        d_recent_row = entry[0]
        # caches the UID, Ammeter value, and Current Flow in gallons per cycle, Unix timestamp
        row = [entry[1], entry[2], entry[3], entry[4]]
        dishwasher_cache.append(row)
        entry = cur.fetchone()
    
    # close and free up connection
    cur.close()
    conn.close()

    # all recent data is now cached on the server, we can start interacting with the user after returning these and storing them
    return f_recent_row, d_recent_row

# only queries fridge table for new rows
def update_f_cache(f_recent_row, fridge_cache):
    # connect to neon database and get cursor
    conn = psycopg2.connect(
    dbname=os.getenv("NEON_DBNAME"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    host=os.getenv("NEON_HOST"),
    port=5432,
    sslmode="require"
    )
    cur = conn.cursor()

    cur.execute(f"""
    SELECT
        f.id,
        "payload"->>'parent_asset_uid',
        ammeter.value AS ammeter_value,
        moisture.value AS moisture_value,
        "payload"->>'timestamp'
    FROM fridges_virtual f
    LEFT JOIN json_each(f."payload") AS ammeter(key, value)
        ON ammeter.key ILIKE '%Ammeter%'
    LEFT JOIN json_each(f."payload") AS moisture(key, value)
        ON moisture.key ILIKE '%MoistureMeter%';
    WHERE f.id > {f_recent_row}
    """)

    entry = cur.fetchone()
    while(entry != None):
        f_recent_row = entry[0]
        # caches the UID, Ammeter value, Moisture Value, and Unix Timestamp
        row = [entry[1], entry[2], entry[3], entry[4]]
        fridge_cache.append(row)
        entry = cur.fetchone()

    # close and free up connection
    cur.close()
    conn.close()
    
    return f_recent_row

def update_d_cache(d_recent_row, dishwasher_cache):
    # connect to neon database and get cursor
    conn = psycopg2.connect(
    dbname=os.getenv("NEON_DBNAME"),
    user=os.getenv("NEON_USER"),
    password=os.getenv("NEON_PASSWORD"),
    host=os.getenv("NEON_HOST"),
    port=5432,
    sslmode="require"
    )
    cur = conn.cursor()

    cur.execute(f"""
    SELECT
        d.id,
        "payload"->>'parent_asset_uid',
        ammeter.value AS ammeter_value,
        flow.value AS flow_value,
        "payload"->>'timestamp'
    FROM dishwashers_virtual d
    LEFT JOIN json_each(d."payload") AS ammeter(key, value)
        ON ammeter.key ILIKE '%Ammeter%'
    LEFT JOIN json_each(d."payload") AS flow(key, value)
        ON flow.key ILIKE '%CurrentFlow%';
    WHERE d.id > {d_recent_row}
    """)

    entry = cur.fetchone()
    while(entry != None):
        d_recent_row = entry[0]
        # caches the UID, Ammeter value, and Current Flow in gallons per cycle, Unix timestamp
        row = [entry[1], entry[2], entry[3], entry[4]]
        dishwasher_cache.append(row)
        entry = cur.fetchone()

    # close and free up connection
    cur.close()
    conn.close()
    
    return d_recent_row


# main function for Server driver
if __name__ == "__main__":
    # load profile and passwords from env file
    load_dotenv()

    # read metadata to match the names of all the devices to their uid's
    fridge_names = {}
    dishwasher_names = {}

    # two caches in memory to keep reduce redundant queries 
    f_recent_row = 0 # remembers the last row it queried in the fridges_virtual table so it doesn't query them again
    d_recent_row = 0 # remembers the last row it queried in the dishwashers_virtual table so it doesn't query them again
    fridge_cache = []
    dishwasher_cache = []

    # full refresh local caches of data and query the database 
    f_recent_row, d_recent_row = refresh_cache(fridge_names, dishwasher_names, fridge_cache, dishwasher_cache)
    
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

    # Makes sure to query the database for new data once every minute max so we keep a unix timestamp here, then later check if 60 seconds have elapsed
    timestamp = int(time.time())

    # continuous loop to listen and respond to connections
    while True:
        # recieves data from client
        myData = str(incomingSocket.recv(100).decode())

        # message to send back to client
        msg = ""

        # also checks if the message sent is an empty array
        # to see if the client closed the connection normally, it will error if it was abrupt
        if myData == "":
            print("Client ended session, terminating connection")
            break
        

        match myData:
            case "1":   # Find average moisture in fridges
                # if 60 seconds have passed query database for new rows
                if(int(time.time()) - timestamp > 60):
                    timestamp = int(time.time())
                    f_recent_row = update_f_cache(f_recent_row, fridge_cache)

                # Add up all the moisture readings in the past 3 hours and divide by the count
                moisture = 0
                count = 0
                for row in reversed(fridge_cache):
                    # checks if the entry was actually in the last 3 hours
                    time_elapsed = int(time.time()) - int(row[3])
                    if time_elapsed < (60 * 60 * 3):
                        moisture += float(row[2])
                        count += 1
                    else:
                        # if it's not in the last three hours looks like thats it, end for loop and calculate
                        # checks if divide by zero
                        if count == 0:
                            msg = "N/A."
                        else:
                            msg = f"{moisture/count}% Relative Humidity"
                        break


            case "2":   # Find average water consumption per cycle for dishwashers
                # if 60 seconds have passed query database for new rows
                if(int(time.time()) - timestamp > 60):
                    timestamp = int(time.time())
                    d_recent_row = update_d_cache(d_recent_row, dishwasher_cache)

                # Add up all the water flow readings and divides by the count
                gallons_p_cycle = 0
                count = 0
                for row in dishwasher_cache:
                    gallons_p_cycle += float(row[2])
                    count += 1

                # checks if divide by zero
                if count == 0:
                    msg = "N/A."
                else:
                    msg = f"{gallons_p_cycle/count} Gallons/Cycle"
                


            case "3":   # Find which appliance uses the most electricity
                # dictionary to store all the power consumption levels
                power_use = {}
                counts = {}

                # add all fridges to the dict
                for fridge in list(fridge_names.keys()):
                    power_use[fridge] = 0
                    counts[fridge] = 0

                for dishwasher in list(dishwasher_names.keys()):
                    power_use[dishwasher] = 0
                    counts[dishwasher] = 0

                # now go through all the ammeter readings in the caches, query database if a minute has passed since last update
                if(int(time.time()) - timestamp > 60):
                    timestamp = int(time.time())
                    f_recent_row = update_f_cache(f_recent_row, fridge_cache)
                    d_recent_row = update_d_cache(d_recent_row, dishwasher_cache)
                
                # first we go through and find the average amp draw in each fridge
                for row in fridge_cache:
                    power_use[row[0]] += float(row[1])
                    counts[row[0]] += 1

                # then we go through and find the average amp draw in each dishwasher
                for row in dishwasher_cache:
                    power_use[row[0]] += float(row[1])
                    counts[row[0]] += 1
                
                # calculate average and check if division by zero
                for appliance in list(power_use.keys()):
                    if counts[appliance] == 0:
                        power_use[appliance] = 0
                    else:
                        # now we have the average amperes, we need to convert to kilowatt hours
                        power_use[appliance] /= counts[appliance]
                        # first multiply by 120 volts as that is the standard residential housing voltage supply
                        power_use[appliance] *= 120
                        # then divide by 1000 to get kilowatts
                        power_use[appliance] /= 1000
                        
                # now to find actual consumption, a fridge would run 24 hours a day, while a dishwasher runs maybe once a day for an hour.
                # so we now multiple all fridge kilowatt averages by 24 hours a day
                # and then we multiple all dishwashers by the rate of one hour a day
                current_time = int(time.time())

                for fridge in list(fridge_names.keys()):
                    power_use[fridge] *= 24

                # and we don't need to multiply the dishwashers by 1 to change anything, so now power_use has all the kilowatt hours in a day 
                # now just find out which one has the highest kilowatt hour consumption with max
                most_usage = max(power_use.values())
                most_appliance = [key for key, value in power_use.items() if value == most_usage]
                if(most_appliance[0] in list(fridge_names.keys())):
                    msg = f"{fridge_names[most_appliance[0]]}: {most_usage} kilowatt hours in a day"
                elif(most_appliance[0] in list(dishwasher_names.keys())):
                    msg = f"{dishwasher_names[most_appliance[0]]}: {most_usage} kilowatt hours in a day"
                else:
                    msg = "error"
            
            # bad message gets through gets caught here
            case _:
                msg = "bad message error"

        # prints the incoming message
        print("CLIENT: ", f"Recieved Choice: {myData}")

        # converts recieved message into all upper case and sends it back to sender
        incomingSocket.send(bytearray(str(msg), encoding='utf-8'))
        print(f"SENDING RESPONSE...{msg}")
        print()

    # terminate connection safely, although this code won't reach here due to the infinite loop
    incomingSocket.close()

