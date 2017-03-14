# django_joomla_authentication_backend

Some classes used in a customized application called "accounts", used to deploy hybrid authentication system in a educational django project. These classes have been used and tested with joomla 2.5.9.

just put them in the application that you prefer, or in the system core,  and then add the auth_backend in settings.py, according to the real path, as follow

AUTHENTICATION_BACKENDS = (
    'accounts.middleware.EmailBackend', 
    'accounts.middleware.OldJoomlaBackend',
    )

EmailBackend is not required, it comes just for fun :)
