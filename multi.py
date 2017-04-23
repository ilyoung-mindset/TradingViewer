import threading
import _thread
queueLock = threading.Lock()
class multithreading(threading.Thread):
    def __init__(self,threadID,function,*args):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.function = function
        self.args = args
    def run(self):
        #print (self.function.__name__ + " starting")
        self.function(*self.args)
        #print (self.function.__name__ + " end")



def testfunction(number,number2):
    print (number+number2)

if __name__=="__main__":
    mythread = multithreading(1,testfunction,9,10)
    mythread.start()