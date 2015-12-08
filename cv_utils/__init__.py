import inspect
#stacktrace - returns the stacktrace
def stacktrace():
    st = ''
    try:
        st += 'Traceback (most recent call last):\n'
        for item in reversed(inspect.stack()[2:]):
            st += '    File "{1}", line {2}, in {3}\n'.format(*item)
        for line in item[4]:
            st += '    ' + line.lstrip()
        for item in inspect.trace():
            st += '        File "{1}", line {2}, in {3}\n'.format(*item)
        for line in item[4]:
            st += '    ' + line.lstrip()
        return st
    except:
        return st
