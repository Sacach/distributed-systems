# Import socket module
import socket
 
def Main():
    
    # local host IP '127.0.0.1'
    host = socket.gethostname()
    # Define the port on which you want to connect
    port = 12345
    
    # Creates a socket for the client
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # connect to server on local computer
    try:    
        s.connect((host,port))
        sockport = s.getsockname()[1]
    
    #If main server is down connect to backup server
    except ConnectionRefusedError:
        port = 12346
        s.connect((host,port))
        sockport = s.getsockname()[1]

    while True:
        # Listen for message from the server
        try:
            data = str(s.recv(1024).decode('ascii'))
        
        # If server is down connect to backup
        except:
            s.close()
            print("finding new server")
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind(("",sockport))
            s.connect((host,12346))
            data = str(s.recv(1024).decode('ascii'))

        # Print the received message
        if data:
            print(data)

        
        # Check if it is your turn or if the game is over
        if "Your turn" in data:
            while True:
                # prompt the user for a move
                try:
                    message = int(input("Send a move (1-9): "))
                # if given input not a number repeat the above step
                except ValueError:
                    print("Not a number")
                    continue
                # If number is in the correct range continue execution normally
                if message > 0 and message < 10:
                    break
                # If number is out of bounds, print reminder and loop will repeat
                print("Number not in range (1-9)")
            
            # Send message to the server
            try:
                message = str(message)
                s.send(message.encode('ascii'))
            # If server is down connect to backup
            except:
                s.close()
                print("finding new server")
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.bind(("",sockport))
                s.connect((host,12346))
                print("new server found")
        
        # If game over message recieved from server, thank the player and prompt them to close the game
        if "Game over." in data:
            print("Thank you for playing!")
            input("Give any input to close: ")
            break
    # close the connection
    s.close()
 
if __name__ == '__main__':
    Main()