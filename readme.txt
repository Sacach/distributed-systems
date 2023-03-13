Instructions for running the code:

- Start server1 by running server1.py

- Start server2 by running server2.py, this order is mandatory and both need to be started
  for the system to operate properly

- Start opening clients by running client1.py as many times as you want. Naturally,
  at least two clients are needed for a game to start

- We recommend running the server programs from the command line with "python server{1 or 2}.py"
  as opposed to executing them from a folder as this appears to make things more stable

- The clients are paired in the order they connect to the server
	- 1st and 2nd are paired, 3rd and 4th are paired, etc.

- In the client program you can submit moves (1-9), which are updated and displayed to
  both players in a pair. Illegal moves are not accepted and the client will need to
  resubmit

- If a winning condition is met, the result is sent to both players, who are then
  instructed to exit the program. Users needs to open a new client to play again

- Players can close their clients forcefully at any time (top right X), which results in
  the other player in a pair receiving a victory message

- If server1 crashes, all connected clients are transfered to server2 and all
  gamestates are preserved meaning the game continues from the state it was in
  before server1 crashed
	- You can crash server1 by forcefully closing it (top right X)
	- New instances of client1.py will automatically connect to server2
	  after server1 has crashed

- The system can sometimes appear to be frozen. This can usually be fixed by pressing enter on a
  window that hasn't updated

- If server2 crashes before server1, the system will continue operating normally until server1 crashes

- Neither server can be restarted after crashing to enable back and forth switching between the two servers.
  Restarts will lead to undesired behaviour and is not recommended

- The system is configured to run on a local machine (servers and clients on same machine).
  In order to run in local network configuration you must change the host variable in client1.py
  (line 8) to match the servers. The value you want is displayed as the first print of server1.py

- We have not tested operation across different networks
  

