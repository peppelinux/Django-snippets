from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

from registration.models import RegistrationProfile, RegistrationManager

class OldJoomlaUsers(models.Model):
    id_tabella       = models.AutoField(primary_key=True)
    name             = models.CharField(max_length=135, blank=False, null=False)
    username         = models.CharField(max_length=135, blank=False, null=False)
    email            = models.CharField(max_length=135, blank=False, null=False)
    password         = models.CharField(max_length=135, blank=False, null=False)
    registerDate     = models.DateTimeField()
    imported           = models.BooleanField(default=False)    
    class Meta:
        #~ db_table = u'attivita_didattica'
        ordering = ['-registerDate']
        verbose_name_plural = "OldJoomlaUsers"
        #~ unique_together = ('nome')
    
    def __unicode__(self):
        return smart_unicode('%s' % (self.name) )
        
# only if django atuh is coupled with django registration-redux or django registration

class UserProfile(models.Model):
    #user = models.ForeignKey(User, unique=True)
    registration_profile = models.ForeignKey(RegistrationProfile, unique=True)
    force_password_change = models.BooleanField(default=False)
    def __unicode__(self):
        try:
            return smart_unicode('%s profile' % (self.registration_profile) )
        except:
            return  smart_unicode('%d NO-Profile' % (self.pk))
            
def create_user_profile_signal(sender, instance, created, **kwargs):
    if created:
        r_user = RegistrationProfile(user=instance)
        #print r_user
        up = UserProfile(registration_profile=r_user)
        r_user.activation_key = RegistrationProfile.ACTIVATED
        r_user.save()
        up.save()

def password_change_signal(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.username)
        if not user.password == instance.password:
          print user
          profile = RegistrationProfile.objects.get(user = user) 
          profile.force_password_change = False
          profile.save()
    except User.DoesNotExist:
        pass

signals.pre_save.connect(password_change_signal, sender=User, dispatch_uid='accounts.models')
signals.post_save.connect(create_user_profile_signal, sender=User, dispatch_uid='accounts.models')
