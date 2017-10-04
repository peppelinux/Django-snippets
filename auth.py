from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import user_passes_test

import datetime

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            return u.is_superuser or bool(u.groups.filter(name__in=group_names))
        return False
    return user_passes_test(in_groups)

class SessionUniqueBackend(ModelBackend):
    """
        This class logout a user if another session of that user
        will be created
        
        in settings.py
        AUTHENTICATION_BACKENDS = [ 'django.contrib.auth.backends.ModelBackend',
                                    'unical_ict.auth.SessionUniqueBackend'
                                  ]
    """
    def authenticate(self, username=None, password=None, **kwargs):
        # check if username exists and if it is active
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return None

        # disconnect already created session, only a session per user is allowed
        # get all the active sessions
        for session in Session.objects.all():
            print(session)
            try:
                if int(session.get_decoded()['_auth_user_id']) == user.pk:
                    session.delete()
            except (KeyError, TypeError, ValueError):
                pass
        
        return user if user else None
