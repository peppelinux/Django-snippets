import hashlib
from django.contrib.auth.models import User
from django.utils.html import simple_email_re  as email_re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group

from django.contrib.auth.hashers import make_password

# this is a custom app used to map joomla 2.5.9 tables in django ORM
from accounts.models import OldJoomlaUsers

class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        #If username is an email address, then try to pull it up
        if email_re.search(username):
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            #We have a non-email address username we should try username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
                
        if user.check_password(password):
            return user

class OldJoomlaBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            j_user = OldJoomlaUsers.objects.get(username=username, imported=False)
        except:
            return None
        
        # calcolo md5 per verificare
        m = hashlib.md5()
        
        # check if password is salted or not
        s_pass = j_user.password.split(':')
        if len(s_pass) > 1:
            # salted password
            m.update(password+s_pass[1])
        else:
            m.update(password)
        
        if s_pass[0] == m.hexdigest():
            # password vera, importo l'utente
            name     = ' '.join(j_user.name.split(' ')[:-1])
            surname  = j_user.name.split(' ')[-1]
            
            #~ RegistrationManager.create_inactive_user()
            dj_password = make_password(password)
            nuser     = User.objects.create(username=username, \
                                       first_name=name,\
                                       last_name=surname,\
                                       email=username,\
                                       password=dj_password)
            
            # customize it if you want to assing a group to every recycled joomla user
            # default group
            # g = Group.objects.get(name__icontains='ola')
            #g.user_set.add(user)
            j_user.imported = True
            j_user.save()            
            return user
        
        else:
            return None

