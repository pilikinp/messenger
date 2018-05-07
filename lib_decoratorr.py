import logging

enable_log = True
app_log = logging.getLogger('app')

def log(func):
    if enable_log:
        def callf(*args,**kwargs):
            # callf.__doc__ = func.__doc__
            # callf.__name__ = func.__name__
            # with open('debug.log', 'a') as debug_log:
            #     debug_log.write('Вызов %s: %s,%s\n'%(func.__name__, args, kwargs))
            #     r = func(*args, **kwargs)
            app_log.debug('Вызов %s: %s,%s\n'%(func.__name__, args, kwargs))
            r = func(*args, **kwargs)
            return r
        return callf
    else:
        return func

def login_required(func):
    pass