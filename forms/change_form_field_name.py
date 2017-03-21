# -*- coding: utf-8 -*-

from django import forms
from .models import *

from django.forms.util import ErrorList
from django.contrib.admin.helpers import ActionForm

def set_field_html_name(cls, new_name):
    """
    This creates wrapper around the normal widget rendering, 
    allowing for a custom field name (new_name).
    """
    old_render = cls.widget.render
    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    cls.widget.render = _widget_render_wrapper

class OlaGruppoDiStudioActionForm(ActionForm):
    ore_studio_in_aula       = forms.IntegerField(required=False)    
    ola_gruppo_di_studio    = forms.ModelChoiceField( OlaGruppoDiStudio.objects.all(), required=False )
    set_field_html_name(ola_gruppo_di_studio, 'ola_gruppo')
