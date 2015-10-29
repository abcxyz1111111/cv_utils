import threading
import sys
import traceback

class Threader(threading.Thread):

    active_threads = []

    #create the thread
    def __init__(self, target, args, iterations = 1):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.iterations = iterations
        self.exit = False
        self.paused = False
        self.ret = None
        Threader.active_threads.append(self)

    #run the target
    def run(self):
        #execute task
        try:
            while not self.exit and (self.iterations > 0 or self.iterations == -1):
                if not self.paused:
                    if self.args is not None:
                        self.ret = self.target(self.args)
                    else:
                        self.ret = self.target()
                    self.iterations = max(-1,self.iterations - 1)
                else:
                    time.sleep(0.1)
        except Exception as err:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise SystemExit("Exception in thread")


        #clean up
        Threader.active_threads.remove(self)

    #request the thread to stop at the next iteration
    def stop(self):
        self.exit = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    @classmethod
    #request all threads to stop at the next iteration
    def stop_all(self):
        print "Closing {0} threads...".format(len(Threader.active_threads))
        for thr in Threader.active_threads:
            thr.stop()
