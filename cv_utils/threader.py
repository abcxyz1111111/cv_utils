import threading

class Threader(threading.Thread):

    active_threads = []

    #create the thread
    def __init__(self, target, args, iterations = 1,):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.iterations = iterations
        self.req_stop = False
        Threader.active_threads.append(self)

    #run the target
    def run(self):
        #execute task
        while not self.req_stop and (self.iterations > 0 or self.iterations == -1):
            self.target(self.args)
            self.iterations = max(-1,self.iterations - 1)

        #clean up
        Threader.active_threads.remove(self)

    #request the thread to stop at the next iteration
    def stop(self):
        self.req_stop = True

    @classmethod
    #request all threads to stop at the next iteration
    def stop_all(self):
        print "Closing {0} threads...".format(len(Threader.active_threads))
        for thr in Threader.active_threads:
            thr.stop()
