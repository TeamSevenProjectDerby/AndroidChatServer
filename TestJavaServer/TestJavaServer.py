import socket	
import random
import select
import sys
import ssl
import urllib.request as urllibReq

#Class which stores the socket and name of a user
class User:
    def __init__(self, connection, name):
        self.name = name
        self.connection = connection

#Sends a message to each user stored in the userDictionary
def broadcastMessage(message, userDictionary, sender):
    if (message != ''):
        message = sender.name + ": " + message
        print(message);
        for user in userDictionary:   
            name = user.name
            address = user.connection                                 
            address.send((message + "\r\n").encode())    

#Sends the name of each user to the client
def returnUserList(userDictionary, sender):
    connection = sender.connection
    print("-User List Sent to " + sender.name)
    connection.send(("End Thread\r\n").encode())   #Flush message used to end the thread loop
    for user in userDictionary:
        connection.send(("0" + user.name + "\r\n").encode())
    connection.send(("1\r\n").encode())


#Main Program starts here -------------------------


host = "10.233.130.84"  #Change to computers IP address (open cmd - ipconfig - IPv4 Address)
port = 9000  #Make sure its some random large number (less than 37k) so its not used by another application
print(host)
clientConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates the player socket
clientConnection.bind((host, port))	
clientConnection.listen(10)	

inputs = [clientConnection] #Accepts connections from predetermined sockets
userDictionary = {}


while inputs:   
    
    (read, write, excep) = select.select(inputs, [], [])
    for sock in read: #procceses each incoming socket
        try:
            if sock is clientConnection:  #Accepts connection from player socket and creates random num
                (client, address) = clientConnection.accept()        
                print("User Connected " + address[0] + " " + str(address[1]))      
                inputs.append(client)                      
                name = client.recv(1024).decode()
                user = User(client, name)   
                userDictionary[user] = user;     
            else:                
                data = sock.recv(1024).decode()
                #The request code is the first char of the string to represent the request type
                requestCode = data[:1]
                #If the requet code is '0', the sender requests for the message to be broadcast to users
                if (requestCode == "0"):
                    for recipient in userDictionary:
                        if sock == recipient.connection:
                            sender = recipient
                            break;
                    broadcastMessage(data[1:], userDictionary, sender)
                #If the request code is '1', the sender requests the user list to be sent to them
                elif (requestCode == "1"):
                    for recipient in userDictionary:
                        if sock == recipient.connection:
                                sender = recipient
                                break;
                    returnUserList(userDictionary, sender)
                #If the request code is '2' the sender wants requests their name to be set
                elif (requestCode == "2"):
                    user.name = data[1:]
        #If a socket exception is raised, the connection is removed from the dictionary      
        except:   
            print("User Disconnected") 
            for user in userDictionary:
                if user.connection == sock:
                    del userDictionary[user]  
                    break               
            inputs.remove(sock)              
            sock.close()       

