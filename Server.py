import zmq
import numpy as np


class Server():
    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind("tcp://*:5555")
        self.clients = [] 
    
    def wait_for_clients(self):
        while len(self.clients) < 2:
            print("Waiting for " + (2-len(self.clients)).__str__() + " clients to connect")
            client_id, message = self.socket.recv_multipart()
            if not self.clients.__contains__(client_id):
                self.clients.append(client_id)
                print(client_id)
                if len(self.clients) == 2:
                    self.socket.send_multipart([client_id,  b"Connected2"])
                else:
                    self.socket.send_multipart([client_id,  b"Connected"])
    
    def activate(self):
        print("activated")
        while True:
            message = self.socket.recv_multipart()
            print(message[0], " an ", message[3])
            self.socket.send_multipart([message[3], message[1], message[2], message[0]])



def main():
    server = Server()
    server.wait_for_clients()
    server.activate()


if __name__ == "__main__":
    main()

    



