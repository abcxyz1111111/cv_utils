import time
import re

#class used for timing operations
class Benchmark():

    marks = []

    def __init__(self, package = None):
        self.package = package
        self.start = 0

    #start timer
    def enter(self):
        self.start = time.time()

    #end timer
    def exit(self,function = None, tag = None, dont_append = False):
        ellapsed = time.time() - self.start
        if not dont_append:
            Benchmark.marks.append((self.package, function, tag, ellapsed))
        return ellapsed

    #print all entries
    def print_all(self):
        for m in Benchmark.marks:
            self._print_mark(m)
        print ""
        self.clear()

    #print entries from a certain package
    def print_package(self, package):
        for m in Benchmark.marks:
            if m[0] == package:
                self._print_mark(m)
        print ""

    #print entries with a certain function
    def print_function(self, function):
        for m in Benchmark.marks:
            if m[1] == function:
                self._print_mark(m)
        print ""

    #print entries with a certain tag
    def print_tag(self, tag):
        for m in Benchmark.marks:
            if m[2] == tag:
                self._print_mark(m)
        print ""

    #print a single mark
    def _print_mark(self,mark):
        package, function, tag, ellapsed = mark

        line = "["
        #append package name if present
        if package is not None:
            line += " \033[1m\033[96m{0}.py\033[0m".format(package)
        #append function name if present
        if function is not None:
            line += " \033[1m\033[95m{0}()\033[0m".format(function)
        #append tag name if present
        if tag is not None:
            line += " \033[1m\033[92m{0}\033[0m".format(tag)
        line += " ]"

        #append spaces
        remainder = 60 - len(re.sub('\\033.{2,3}m','',line))
        for i in range (0, remainder):
            line += ' '

        #append time
        line += str(round(ellapsed * 1000,2))
        line += " ms"
        print line

    #clear out all entries
    def clear(self):
        Benchmark.marks = []




#test
if __name__ == "__main__":
    bench = Benchmark("Benchmark")
    bench.enter()
    time.sleep(0.5)
    bench.exit(function = "test", tag = "cv")

    bench.enter()
    time.sleep(0.5)
    bench.exit(function = "test1", tag = "utils")

    bench.enter()
    time.sleep(0.5)
    bench.exit(tag = "Nuge")

    bench.enter()
    time.sleep(0.5)
    bench.exit()

    bench.print_function("test")
    bench.print_all()
    bench.print_all()
