#import required modules
import socket
from _thread import start_new_thread
import time
# Global lists
#list of plaer pairs socket objects
connection_list = []
#list of servers (implemetation of more than 2 servers was thought and this was mainly for that but current implementation only supports one backup server)
servers = []

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
    # tell p1 that they are waiting for another player
    message = "you are connected\n Waiting for players"
    p1.send(message.encode('ascii'))
    # finds the index of p1 in connection_list
    i = connection_list.index([p1, "empty"])
    # loop for waiting for another player
    while connection_list[i][1] == "empty":
        pass
    # sets p2
    p2 = connection_list[i][1]
    # save the ports of p1 and p2
    port1 = str(p1.getpeername()[1])
    port2 = str(p2.getpeername()[1])
    # tell the players that an opponent has been found
    message = ("player found\nBoard:\n" + format_board(board)).encode('ascii')
    p1.send(message)
    p2.send(message)
    #tell p2 to wait for their turn
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
            # try to update server2 of the gamestate
            try:
                servers[0].send(("Board" + str(board) + "!!" + str(current_player) + "!!" + str(port1 + port2)).encode('ascii'))    
            except:
                pass
            # send the updated board to both players
            p1.send(("Board:\n" + format_board(board)).encode('ascii'))
            p2.send(("Board:\n" + format_board(board)).encode('ascii'))

        except Exception as e:
            # try to send the information about diconnected clients to server2
            try:
                servers[0].send((port1 + "dc").encode('ascii'))
                time.sleep(0.1)    
                servers[0].send((port2 + "dc").encode('ascii'))
            except:
                pass
            # in the case of a disconnection declare the remaining player as winner
            try:
                p1.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
            except ConnectionResetError:
                p2.send(('Game over. Other player disconnected. Winner: you').encode('ascii'))
                # if both sends fail we just continue and close both sockets
            except OSError:
                pass
            try:
                p1.close()
                p2.close()
            except:
                pass
            return 0

    try:
        #try to update server2 about disconnections
        try:
            servers[0].send((port1 + "dc").encode('ascii'))    
            servers[0].send((port2 + "dc").encode('ascii'))
        except:
            pass
        # if winner was found tell it to the players
        p1.send(('Game over. Winner: ' + winner).encode('ascii'))
        p2.send(('Game over. Winner: ' + winner).encode('ascii'))
    except:
        # in case of error pass
        pass
    # close the sockets
    p1.close()
    p2.close()
    return 0

def Main():
    # blank host name for the server
    host = ""
    # port of the server
    port = 12345
    # create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the soccket to the known port
    s.bind((host, port))
    print("socket binded to port", port)
    
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening for servers")
    #accept the connection from server2
    c, addr = s.accept()
    # append the server port to the server list
    servers.append(c)
    # set the initial number of connections, variable is used for determining if we need to start a new thread or if there is someone waiting for another player
    connections = 0
    while True:
        print("socket is listening")
        # establish connection with client
        c, addr = s.accept()
        #try to send the port of a new connection to server2
        try:
            servers[0].send(str(addr[1]).encode())
        except:
            pass
        print('Connected to :', addr[0], ':', addr[1])

        # we check if there is an uneven number of connections
        if connections % 2 == 0:
            # in the case of all players having a partner we start a new thread for the new player
            connection_list.append([c, "empty"])
            start_new_thread(threaded, (c,))
        else:
            # otherwise we search for the one who is waiting for a partner and set the socket object to the connection list 
            for i, pair in enumerate(connection_list):
                if pair[1] == "empty":
                    connection_list[i][1] = c
        # keep count of all the gotten connections
        connections += 1

    s.close()
 
 
if __name__ == '__main__':
    Main()

