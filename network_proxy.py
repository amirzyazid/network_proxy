import signal
import socket
import threading


# Creating an incoming socket

class NetworkProxy:
    def __init__(self, config):
        # Ensure config has required keys
        if 'HOST_NAME' not in config or 'BIND_PORT' not in config:
            raise ValueError("Config must contain 'HOST_NAME' and 'BIND_PORT'")

        # Shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.shutdown) 

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to a public host, and a port   
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT']))
        
        self.serverSocket.listen(10) # become a server socket
        self.__clients = {}
        self.config = config  # Store the config for later use
        
        while True:
            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept() 
            
            d = threading.Thread(name=self._getClientName(client_address), 
            target=self.proxy_thread, args=(clientSocket, client_address, self.config))
            d.setDaemon(True)
            d.start()
            
            
            
    def proxy_thread(self, clientSocket, client_address, config):
    # get the request from browser
        request = clientSocket.recv(config['MAX_REQUEST_LEN']) 

        # parse the first line
        first_line = request.split(b'\n')[0]

        # get url
        url = first_line.split(b' ')[1]
        
        http_pos = url.find(b"://") # find pos of ://
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of url

        port_pos = temp.find(b":") # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find(b"/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = b""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos: 
            # default port 
            port = 80 
            webserver = temp[:webserver_pos] 
        else: # specific port 
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos] 
            
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.settimeout(config['CONNECTION_TIMEOUT'])
        s.connect((webserver.decode(), port))
        s.sendall(request)
        
        while True:
            # receive data from web server
            data = s.recv(config['MAX_REQUEST_LEN'])

            if len(data) > 0:
                clientSocket.send(data) # send to browser/client
            else:
                break
            
            