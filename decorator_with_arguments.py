from django.http.response import HttpResponseRedirect, HttpResponse
from functools import wraps
from django.urls import reverse


def decorator(arg1, arg2):
    """an explained example
    """
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            print("Arguements passed to decorator %s and %s" % (arg1, arg2))
            function(*args, **kwargs)
        return wrapper
    return inner_function


def redirect_if_authenticated(redirect_to):
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            request = args[0]
            print("Arguements passed to decorator {}".format(redirect_to))
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse(redirect_to))
            return function(*args, **kwargs)
        return wrapper
    return inner_function
