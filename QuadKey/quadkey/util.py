import functools


def condition(precondition=None, postcondition=None):
    def decorator(func):
        @functools.wraps(func)  # preserve name, docstring, etc
        def wrapper(*args, **kwargs):  # NOTE: no self
            if precondition is not None:
                assert precondition(*args, **kwargs)
            retval = func(*args, **kwargs)  # call original function or method
            if postcondition is not None:
                assert postcondition(retval)
            return retval
        return wrapper
    return decorator


def precondition(check):
    return condition(precondition=check)


def postcondition(check):
    return condition(postcondition=check)
