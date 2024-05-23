import zmq
import numpy as np
import json
import random

class Client():
    def __init__(self, ip, goalIp):
        self.ip = ip
        self.goalIp = goalIp
        self.turn= 0
        self.publicKeyGoal = None
        self.public_key, self.private_key = self.generate_keypair()
        context = zmq.Context()
        print("Connecting to hello world server…")
        self.socket = context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, self.ip.encode('ascii'))
        self.socket.connect("tcp://localhost:5555")

    def sendMessage(self, message):
        message = self.crypt(message)
        md = dict(dtype=str(message.dtype), shape=message.shape)
        print("Sending message...")
        self.socket.send_multipart([json.dumps(md).encode('utf-8'), message.tobytes(), self.goalIp.encode('utf-8')])

    def receiveMessage(self):
        print("Waiting on response...")
        answer = self.socket.recv_multipart()
        md = json.loads(answer[0].decode('utf-8'))
        print(answer)
        message = np.frombuffer(answer[1], dtype=md['dtype']).reshape(md['shape'])
        message = self.decrypt(message)
        print(f"Received : {message} from {answer[2]}")

    def initialMessage(self):
        print("Sending initial message...")
        self.socket.send_multipart([self.public_key[0].encode('utf-8'),self.public_key[1].encode('utf-8')])
        print("Waiting on initial response...")
        answer, publiyKeyGoal1, publiyKeyGoal2 = self.socket.recv_multipart()
        self.publicKeyGoal = (publiyKeyGoal1, publiyKeyGoal2)
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
        e, n = self.publicKeyGoal
        ciphertext = []
        for char in message:
            ciphertext.append(pow(ord(char), int(e), int(n)))
        print(ciphertext)
        return  np.array(ciphertext, dtype=np.int64)


    
    def decrypt(self, message):
        d, n = self.private_key
        plaintext = [chr(pow(int(char), int(d), int(n))) for char in message]
        return ''.join(plaintext)
    
    def generate_prime(self,bits=32):
        while True:
            p = random.getrandbits(bits)
            if self.is_prime(p):
                return p
            
    def generate_keypair(self,bits=32):
        p = self.generate_prime(bits) #prim1
        q = self.generate_prime(bits) #prim2
        n = p * q
        phi = (p - 1) * (q - 1)
        e = random.randrange(1, phi)
        g = self.gcd(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = self.gcd(e, phi)
        d = self.mod_inverse(e, phi)
        return ((str(e), str(n)), (str(d), str(n)))
     
    def is_prime(self, n, k=5):
        if n == 2 or n == 3:
            return True
        if n <= 1 or n % 2 == 0:
            return False

        s, d = 0, n - 1
        while d % 2 == 0:
            s += 1
            d //= 2

        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a

    def mod_inverse(self, a, m):
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1


def main():
    try:
        getIp = str(input("Please enter Ip: "))
        getGoalIp = str(input("Please enter GoalIp: "))
        client= Client(getIp,getGoalIp)
        client.initialMessage()
        while True:
            if client.turn==0:
                getMessage = str(input("Please enter Message: "))
                client.sendMessage(getMessage)
            client.receiveMessage()
            client.turn=0

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
