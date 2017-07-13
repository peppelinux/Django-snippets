from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

_custom_perm =  (
            ('can_view', _('Permesso in lettura')),
            ('can_view_his_own', _('Permesso in lettura esclusivamente dei propri inserimenti')),
            ('can_change', _('Permesso in modifica')),
            ('can_change_his_own', _('Permesso in modifica esclusivamente dei propri inserimenti')),
            ('can_delete', _('Permesso in cancellazione')),
            ('can_delete_his_own', _('Permesso in cancellazione  esclusivamente dei propri inserimenti')),
                )

class User(AbstractUser):
    GENDER= (
                ( 'male', _('Maschio')),
                ( 'female', _('Femmina')),
                ( 'other', _('Altro')),
            )
    
    is_active = models.BooleanField(_('attivo'), default=True)
    email = models.EmailField('email address', blank=True, null=True)
    first_name = models.CharField(_('Nome'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('Cognome'), max_length=30, blank=True, null=True)   
    gender    = models.CharField(_('Genere'), choices=GENDER, max_length=12, blank=True, null=True)
    short_description = models.CharField(_('Descrizione breve'), max_length=33, blank=True, null=True)    
    avatar  = models.ImageField('Avatar, foto', upload_to='avatars/', null=True, blank=True)
    bio = models.TextField('Biografia, note', max_length=2048, blank=True, null=True)
    location = CountryField('Luogo di nascita', max_length=30, blank=True, null=True)
    birth_date = models.DateField('Data di nascita', null=True, blank=True)
    
    webpage_url = models.CharField(_('Pagina web'), max_length=512, blank=True, null=True)    
    class Meta:
        ordering = ['username']
        verbose_name_plural = _("Utenti di sistema")
    
    def groups_as_ul(self):
        head = '<ul>'
        for i in self.groups.all():
            head += '<li>%s</li>' % i.name
        head += '</ul>'
        return head
    groups_as_ul.short_description = 'Gruppo'
    groups_as_ul.allow_tags = True
    
    def __str__(self):
        return '%s' % (self.username)

class UserSkillType(models.Model):
    is_active = models.BooleanField(_('attivo'), default=True)
    name  = models.CharField(_('Nome'), max_length=150, blank=False, null=False)
    description = models.TextField(_('Descrizione'), max_length=512, blank=True, null=True)    
    icon  = models.ImageField(_('Skills icon'), upload_to='skills_icons/', null=True, blank=True)
    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Skills")
    def __str__(self):
        return '%s' % (self.name)

class UserSkill(models.Model):
    LEVEL = (
                ("0", "0"),    
                ("10", "10"),
                ("20", "20"),
                ("30", "30"),
                ("40", "40"),
                ("50", "50"),
                ("60", "60"),
                ("70", "70"),
                ("80", "80"),
                ("90", "90"),
                ("100", "100")
            )
    
    user          = models.ForeignKey(settings.AUTH_USER_MODEL,  blank=False, null=False, related_name="user_fk")
    skill         = models.ForeignKey(UserSkillType,  null=True, blank=True )    
    level         = models.CharField(_('Livello'), choices=LEVEL, max_length=3, null=True, blank=True )
    comments      = models.CharField(_('Commenti'), max_length=1024, blank=True, null=True)
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="created_by")            
    changed_by    = models.ForeignKey(settings.AUTH_USER_MODEL,  blank=True, null=True, related_name="changed_by")     
    create_date   = models.DateTimeField(auto_now=True)    
    change_date   = models.DateTimeField(blank=True, null=True)      
    class Meta:
        ordering = ['user', 'skill',]
        verbose_name_plural = "Skills, capacità degli utenti"
    
    def __str__(self):
        return '%s %s' % (self.user, self.skill)

class UserActivityType(models.Model):
    is_active = models.BooleanField(_('attivo'), default=True)
    name  = models.CharField(_('Nome'), max_length=150, blank=False, null=False)
    description = models.TextField(_('Descrizione'), max_length=1024, blank=True, null=True)    
    icon  = models.ImageField(_('Skills icon'), upload_to='skills_icons/', null=True, blank=True)
    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Tipologie di attività utente")
    def __str__(self):
        return '%s' % (self.name)

class UserActivity(models.Model):
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    application   = models.ForeignKey(ContentType, null=True, blank=True )    
    activity_type = models.ForeignKey(UserActivityType, null=True, blank=True )  
    note          = models.TextField(_('Note'), max_length=1024, blank=True, null=True)    
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="ua_created_by")            
    create_date   = models.DateTimeField(auto_now=True)    
    class Meta:
        ordering  = ['user', 'application',]
        verbose_name_plural = _("Attività utenti")
    def __str__(self):
        return '%s %s' % (self.application, self.activity_type)

class UserUrlShortcut(models.Model):
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    nome          = models.CharField(_('nome'), max_length=71, blank=True, null=True)        
    url           = models.CharField(_('url'), max_length=1024, blank=True, null=True)    
    is_active     = models.BooleanField(default=False)
    class Meta:
        ordering  = ['user', 'is_active',]
        verbose_name_plural = _("Scorciatoie dashboard utenti")
    def __str__(self):
        return '%s %s' % (self.nome, self.user)
