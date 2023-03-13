# import socket programming library
import socket
import time
from _thread import start_new_thread
# Global lists
#list of plaer pairs socket objects
connection_list = []
# keep track of the clients connected to server1
port_order = []
# global dictionary
gamedict =  {}

def format_board(board):
    """
    This function formats the string which is the board state
    """
    return '{}|{}|{}\n-+-+-\n{}|{}|{}\n-+-+-\n{}|{}|{}'.format(*board)

def check_winner(board, current_player):
    """
    This function checks if there is a winning combination on the board
    function call is check_winner(board, current_player), 
    where board is the list of the board and current player is the symbol of the player who last added a said symbol to the board (X or O)
    """
    #loop for cheking the three rows and columns
    for i in range(3):
            # creates the row and column variables for the win condition check for i
            row = board[i*3:(i+1)*3]
            col = board[i::3]
            # creates the variables for the diagonal win condition check
            diag1 = board[0::4]
            diag2 = board[2:7:2]
            # check if any of the win conditions are true
            if all([x == current_player for x in row]) \
                    or all([x == current_player for x in col]) \
                    or all([x == current_player for x in diag1]) \
                    or all([x == current_player for x in diag2]):
                # if at least one of the conditions was true set winner to current_player
                winner = current_player
                # return the winner
                return winner
    # if no winner was found return None
    return None

def threaded(p1):
    """
    This function is the thread for a game between a player pair
    """
    #initialize variables
    current_player = 'X'
    # set a clean board
    board = [' '] * 9
    # set winner to None
    winner = None
    # valid game moves
    valid_moves = [i for i in range(1,10)]
    # port of the p1
    port1 = str(p1.getpeername()[1])

    # finds the index of p1 in connection_list
    for i, pair in enumerate(connection_list):
            if p1 in pair:
                index = i
                break
    # cretes the message
    message = "you are connected\n Waiting for players"
    # sends the message to p1
    p1.send(message.encode('ascii'))
    # loop for waiting for another player
    while connection_list[index][1] == "empty":
        #stay in loop until p2 is not empty
        pass
    # sets p2
    p2 = connection_list[index][1]
    # try except for creating a game try finding
    try:
        # port of the p2
        port2 = str(p2.getpeername()[1])
        # creates the key search dictionary
        key = str(port1 + port2)
        # get the value from gamedict with the key and transform a part of the string in the dictionary in to the board list
        # if there is no such key (the players do not have an unfinished game from server 1) a new gam,e is created in the except line
        board = eval(gamedict[key][0])
        # set current player to the one recorded in to the dictionary
        current_player = gamedict[key][1]
        # update the valid moves according to the board gotten from the dictionary
        valid_moves = [i+1 for i, j in enumerate(board) if j == ' ']
        # send the information to the player that their game has been restored in the new server.
        p1.send("Game restored".encode('ascii'))
        p2.send("Game restored".encode('ascii'))
        # wait so the messages do not end up into the same buffer
        time.sleep(0.1)
        # send the board state as a reminder for the players
        p1.send(("Board:\n" + format_board(board)).encode('ascii'))
        p2.send(("Board:\n" + format_board(board)).encode('ascii'))
        # wait so the messages do not end up into the same buffer
        time.sleep(0.1)
    except:
        # print to see that the server created a new game
        print("game started", i)
        # creates the message to be sent to the players that an opponent has been found
        message = ("player found\nBoard:\n" + format_board(board)).encode('ascii')
        # try except for sending the messages this avoids the error if one of the players disconnects before coming from crashed server1
        try:
            # send the messages
            p1.send(message)
            p2.send(message)
        except ConnectionResetError:
            # if p1 disconnected declare p2 the winner and send the message to p2
            p2.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
            # close the ports if they are still active
            p1.close()
            p2.close()
            return 0
        except:
            # if p1 disconnected declare p2 the winner and send the message to p2
            p1.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
            # close the ports if they are still active
            p1.close()
            p2.close()
            return 0
        # if no errors happened tell p2 to wait for their turn
        msg = "wait for your turn"
        p2.send(msg.encode('ascii'))
    # game loop which continues until a winner is found 
    while not winner:
        # try except to handle errors (disconnects)
        try:
            # check who is the current player
            if current_player == 'X':
                # tell the player that it is their turn
                message = "Your turn"
                p1.send(message.encode('ascii'))
                # receive the play from the player
                move = int(p1.recv(1024).decode('ascii'))
                # tell the player if the move is not valid 
                if move not in valid_moves:
                    p1.send("Not a valid move, choose another one".encode('ascii'))
                    continue
            else:
                # tell the player that it is their turn
                message = "Your turn"
                p2.send(message.encode('ascii'))
                # receive the play from the player
                move = int(p2.recv(1024).decode('ascii'))
                # tell the player if the move is not valid 
                if move not in valid_moves:
                    p2.send("Not a valid move, choose another one".encode('ascii'))
                    continue
            # if nothing is received break the loop
            if not move:
                print('Bye')
                break
            # if the move was valid remove it from the valid moves list
            valid_moves.remove(move)
            # add the symbol to the board
            board[move - 1] = current_player
            # Check for a winner
            winner = check_winner(board, current_player)
            #check if there was a tie
            if len(valid_moves) == 0 and winner == None:
                p1.send(('Game over. Draw').encode('ascii'))
                p2.send(('Game over. Draw').encode('ascii'))
                p1.close()
                p2.close()

            # switch the current player (change the turn)
            if current_player == 'X':
                current_player = 'O'
            else:
                current_player = 'X'
            # send the updated board to both players
            p1.send(("Board:\n" + format_board(board)).encode('ascii'))
            p2.send(("Board:\n" + format_board(board)).encode('ascii'))
            
        except Exception as e:
            # in the case of a disconnection declare the remaining player as winner
            try:
                # try to send the message for p1
                p1.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
            except ConnectionResetError:
                # if the message could not be sent for p2
                p2.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
            except OSError:
                # if both sends fail we just continue and close both sockets
                pass
            p1.close()
            p2.close()
            return 0
    try:
        # if winner was found tell it to the players
        p1.send(('Game over. Winner: ' + winner).encode('ascii'))
        p2.send(('Game over. Winner: ' + winner).encode('ascii'))
    except:
        # in case of error pass
        pass
    # close the sockets
    p1.close()
    p2.close()
 
def server_thread(c):
    """
    This function is the thread for listening and handling the received data
    """
    print("server_thread listening")
    # listening loop for server messages
    while True:
        # try to receive data
        try:
            data = c.recv(2048).decode()
            # if there is "dc" in the message delete the clients port from port_order list
            if "dc" in data:
                port = data.rstrip("dc")
                port_order.remove(port)
                # and from the gamedict
                for i in gamedict:
                    if port in i:
                        del gamedict[i]
                        break
            # if there is "Board" in the message we create the gamestate, current_player pair from the message and we use the host part as the key for the dictionary
            elif "Board" in data:
                board, c_player, host = data.lstrip("Board").split("!!")
                gamedict[host] =  (board, c_player)
            # if the message is just the port number, it is added to the port_order list
            else:
                port_order.append(data)
                # if there is an uneven number of ports, create a new place holder for the socket objects into the connection_list
                if len(port_order) % 2 == 1:
                    connection_list.append(["empty","empty"])
        except Exception as e:
            #print(e) for debugging
            # make sure the connection is actually closed
            c.close()
            # if server1 was closed print this 
            print("thread closed")
            break


def Main():
    # initialize variables
    # blank host name for the server
    host = ""
    # host name used for connecting to server1
    host2 = socket.gethostname()
    # port of the server
    port = 12346
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the soccket to the known port
    s.bind((host, port))
    print("socket bound to port", port)
    
    # put the socket into listening mode
    s.listen(5)
    # create socket object for connecting to server1
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect to server1
    c.connect((host2,12345))
    # start the listening thread for listening the messages from server1 
    start_new_thread(server_thread, (c,))
    # set the initial number of connections, variable is used for determining if we need to start a new thread or if there is someone waiting for another player
    connections = 0
    while True:
        print("socket is listening")
        
        time.sleep(0.1)
        # accept the connection from the client
        c, addr = s.accept()

        print('Connected to :', addr[0], ':', addr[1])
        # if the clients port is in the port_order list (client was playing on the server1) we try to restore the game that the player was playing on server1
        if str(addr[1]) in port_order:
            # get the index of the port
            port_i = port_order.index(str(addr[1]))
            # for ports in even indices
            if port_i % 2 == 0:
                #place the socket object to the right location in connection_list
                connection_list[int(port_i/2)][0] = c
                #start the thread for the player
                start_new_thread(threaded, (c,))
            else:
                #place the socket object to the right location in connection_list
                connection_list[int((port_i-1)/2)][1] = c
                #tell the player (p2) that they are waiting for players
                message = "you are connected\n Waiting for players"
                c.send(message.encode('ascii'))
            # keep count of all the gotten connections
            connections += 1
        else:
            # if the player did not come from server1 we check if there is an uneven number of connections
            if connections % 2 == 0:
                    # in the case of all players having a partner we start a new thread for the new player
                    connection_list.append([c, "empty"])
                    start_new_thread(threaded, (c,))
            else:
                # otherwise we search for the one who is waiting for a partner and set the socket object to the connection list 
                for i, pair in enumerate(connection_list):
                    if pair[0] == "empty":
                        continue
                    elif pair[1] == "empty":
                        connection_list[i][1] = c
                        break
            # keep count of all the gotten connections
            connections += 1
    s.close()
 
 
if __name__ == '__main__':
    Main()