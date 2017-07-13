from django.contrib import admin
from .models import User
#from .admin_inline import *
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib.auth.admin import UserAdmin
from .admin_inlines import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # as an example, this custom user admin orders users by email address
    ordering = ('username',)
    readonly = ('date_joined',)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser', 'groups_as_ul' )
    list_editable = ('is_active', 'is_staff', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        
        (_('betaCRM'), {'fields': ('gender', 'avatar', 'bio', 'location', 'birth_date', 'webpage_url')}),     
                   
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    inlines = [UserSkillInline,]
#~ admin.site.unregister(User)
#~ admin.site.register(User, CustomUserAdmin)


@admin.register(UserSkillType)
class UserSkillTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(UserActivityType)
class UserActivityTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    pass

@admin.register(UserUrlShortcut)
class UserUrlShortcutAdmin(admin.ModelAdmin):
    pass

