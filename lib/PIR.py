import serial
import time
import numpy as np
import threading
from datetime import datetime
import time

class STPIR_Logger(threading.Thread):
    def __init__(self, com, baud, time, t0, log_name):
        threading.Thread.__init__(self)
        self.com = com
        self.baud = baud
        self.time = time
        self.t0 = t0
        self.log_name = log_name
        self.start()

    def run(self):
        self.connect()
        self.log()

    def connect(self):
        self.ser = serial.Serial(self.com, self.baud, parity='N', stopbits=1, )
        time.sleep(1)
        self.ser.write(b'CONNECT\r\n')
        print(self.com, ": ", self.ser.readline())
        time.sleep(0.1)

        self.ser.write(b'START 0\r\n')
        print(self.com, ": ", self.ser.readline())

    def log(self):
        t0 = datetime.now()
        X = np.array([])
        while (datetime.now() - t0).total_seconds() < self.time:
            line_binary = self.ser.readline()
            try:
                line = line_binary.decode('ascii')
                list_values = line.split('\t')
                n = len(list_values)
                list_values = list_values[1:n - 1]
                if X.shape[0] == 0:
                    X = np.array(list_values)
                    python_timestamp = round(1000 * (datetime.now() - t0).total_seconds(), 3)
                    X = np.append(X, python_timestamp)
                    X = X.reshape(1, -1)
                    print(X)
                else:
                    new_row = np.array(list_values).reshape(1, -1)
                    python_timestamp = round(1000 * (datetime.now() - t0).total_seconds(), 3)
                    new_row = np.append(new_row, python_timestamp)
                    new_row = new_row.reshape(1, -1)

                    if new_row.shape[1] == 9:
                        X = np.concatenate((X, new_row), axis=0)

                    print(self.com, new_row)

            except:
                print("Decode error")

            time.sleep(0.04)

        np.savetxt(self.log_name, X, delimiter=',', fmt='%s')
        print("Log saved for ", self.com)

        while 1:
            time.sleep(1)
