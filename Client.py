import zmq
import numpy as np
import json

class Client():
    def __init__(self, ip, goalIp):
        self.ip = ip
        self.goalIp = goalIp
        self.turn= 0
        context = zmq.Context()
        print("Connecting to hello world server…")
        self.socket = context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, self.ip.encode('ascii'))
        self.socket.connect("tcp://localhost:5555")

    def sendMessage(self, message):
        message = str(message)
        message = self.crypt(message)
        md = dict(dtype=str(message.dtype), shape=message.shape)
        print("Sending message...")
        self.socket.send_multipart([json.dumps(md).encode('utf-8'), message.tobytes(), self.goalIp.encode('utf-8')])

    def receiveMessage(self):
        print("Waiting on response...")
        answer = self.socket.recv_multipart()
        print(answer[0])
        print(answer[1])
        md = json.loads(answer[0].decode('utf-8'))
        print("here")
        message = np.frombuffer(answer[1], dtype=md['dtype']).reshape(md['shape'])
        message = self.decrypt(message)
        print(f"Received array: {message} from {answer[2]}")

    def initialMessage(self):
        print("Sending initial message...")
        self.socket.send_string("Connection")

        print("Waiting on initial response...")
        answer = self.socket.recv()
        print(answer)
        try:
            if answer==b'Connected2':
                self.turn=1
                print("connected succesfully")
            elif answer==b'Connected':
                print("connected succesfully")
        except Exception as e:
            print("not connected succesfully")

    def crypt(self, message):
        chars = np.array([])
        for char in message:
            chars = np.append(chars,(ord(message[len(chars)])))
        print(chars)
        return chars
    
    def decrypt(self, message):
        text = np.array([])
        for char in message:
            text = np.append(text,(chr(int(message[len(text)]))))
        text = ''.join(map(str, text))
        return text


def main():
    try:
        getIp = str(input("Please enter Ip: "))
        getGoalIp = str(input("Please enter GoalIp: "))
        client= Client(getIp,getGoalIp)
        client.initialMessage()
        aktiverChat = True
        while aktiverChat:
            if client.turn==0:
                getMessage = str(input("Please enter Message: "))
                client.sendMessage(getMessage)
            client.receiveMessage()
            client.turn=0

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()


