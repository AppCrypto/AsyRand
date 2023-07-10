import sys
from multiprocessing import Process, Manager
import time

def producer(dic, name):
    for i in range(10000):
        dic["A"] = i
        time.sleep(2)


def consumer(dic, name):
    for i in range(10000):
        aval = dic.get("A")
        #print(f" {name} - Val = {aval}")
        sys.stdout.write(f" {name} - Val = {aval}")
        sys.stdout.flush()
        time.sleep(2.2)


if __name__ == '__main__':
    manager = Manager()
    dic = manager.dict()
    Process(target=producer, args=(dic,"TT")).start()
    time.sleep(1)
    Process(target=consumer, args=(dic,"Con1")).start()
    Process(target=consumer, args=(dic,"Con2")).start()

    while True:
        time.sleep(1)