# from serv.server1 import enable_log
enable_log = True
def log(func):
    if enable_log:
        def callf(*args,**kwargs):
            # callf.__doc__ = func.__doc__
            # callf.__name__ = func.__name__
            with open('debug.log', 'a') as debug_log:
                debug_log.write('Вызов %s: %s,%s\n'%(func.__name__, args, kwargs))
                r = func(*args, **kwargs)
            return r
        return callf
    else:
        return func