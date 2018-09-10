import io
import json
import uuid

from django.apps import apps
from django.forms.models import model_to_dict
from pprint import pprint
from django.db.models.fields.related import (ManyToManyField,
                                             ForeignKey)
from django.db.models.fields import (BooleanField,
                                     NullBooleanField,
                                     IntegerField,
                                     FloatField,
                                     PositiveIntegerField)
from django.db import transaction


class BaseSerializableInstance(object):

    def childrens(self):
        return self.obj._meta.fields_map

    def has_childrens(self):
        """
        boolean
        """
        if self.childrens():
            return True

    def remove_related_field(self, related_field):
        del(self.dict['object'][related_field])
        del(self.dict['object'][related_field+'_id'])
        return related_field
    
    def json(self, indent=2):
        return json.dumps(self.dict, indent=indent)

    def app_model(self, app_name, model_name):
        """
        Returns model class 
        """
        return apps.get_model(app_label=app_name, model_name=model_name)
        
    
class SerializableInstance(BaseSerializableInstance):
    def __init__(self, obj,
                 excluded_fields=['created', 'modified'],
                 excluded_childrens = ['domandabando',],
                 auto_fields = False,
                 change_uniques = True,
                 duplicate = True):
        """
        change_uniques changes unique indexes values to random ones
        unique_values will be modified (be warn on this!)
        drilled_childrens: recursion on these one
        auto_fields = if True doesn't export auto_created, auto_now, auto_now_add
        null_fields = those who will be filled with None value
        parent_fields: these will be filled with None value if duplicate is True
        """

        self.obj = obj
        self.model = obj._meta.model
        self.model_name = obj._meta.object_name

        self.fields = obj._meta._forward_fields_map
        #self.fields = {i.attname:obj._meta._forward_fields_map[i.attname] for i in obj._meta.fields}
        self.excluded_fields = excluded_fields
        
        self.auto_fields = auto_fields
        self.change_uniques = change_uniques

        if duplicate:
            self.change_uniques, self.auto_fields = True, False
        else:
            self.change_uniques, self.auto_fields = False, True

        self.duplicate = duplicate

        # self.drilled_childrens = drilled_childrens
        self.excluded_childrens = excluded_childrens
        
        self.dict = {
            'app_name': obj._meta.app_label,
            'model_name': obj._meta.object_name,
            'object': {},
            'm2m': [], # lists m2m field names
            # 'related_field' : None # this is need only for children obj
            # these will be added in Serialized Tree
            'childrens': [],
            }

    def get_serialized_value(self, obj, ofield):
        """
        
        """
        # everything to string for the first time
        value = ofield.value_to_string(obj)

        # better specification for numeric types
        if type(ofield) in (BooleanField,
                            NullBooleanField,
                            IntegerField,
                            FloatField,
                            PositiveIntegerField,
                            ForeignKey):
            value = ofield.value_from_object(obj)

        # specify others types here if needed
        #
        
        # M2M management
        if isinstance(ofield, ManyToManyField):
            # this way value become a collection
            value = []
            for i in getattr(self.obj, ofield.attname).all():
                if not ofield.attname in self.dict['m2m']:
                    self.dict['m2m'].append(ofield.attname)
                si = self.__class__(i,
                                    excluded_fields=self.excluded_fields,
                                    duplicate=self.duplicate)
                si.serialize_obj()
                value.append(si.dict)
            return value

        # unique override if needed
        if self.change_uniques:
            if ofield.unique:
                if type(value) == str:
                    value = value +'-'+uuid.uuid4().hex
                elif type(value) == int:
                    value = uuid.uuid4().int
        
        return value

    def exclude_field(self, field_name):
        """
        boolean, returns True if elements was added (first time)
        otherwise means that element was already excluded
        """
        if field_name not in self.excluded_fields:
            self.excluded_fields.append(field_name)
            return True
    
    def prepare_duplication(self):
        """
        filters out auto filed and pk
        """
        for field in self.fields:
            ofield = self.fields[field]

            if self.duplicate:
                if ofield.primary_key:
                    self.exclude_field(field)
                    continue
            
            if not self.auto_fields:
                # add others if needed
                if hasattr(ofield, 'auto_now') or \
                   hasattr(ofield, 'auto_now_add'):
                   if ofield.auto_now or ofield.auto_now_add:
                        self.exclude_field(field)
                        continue
            
    def serialize_obj(self):
        """
        
        """
        if self.duplicate:
            self.prepare_duplication()
        
        for field in self.fields:
            if field in self.excluded_fields: continue

            value = self.get_serialized_value(self.obj, self.fields[field])
            if value:
                self.dict['object'][field] = value
        return self.dict

    def serialize_tree(self):
        self.serialize_obj()
        childrens = self.childrens()
        
        for i in childrens:
            if i in self.excluded_childrens: continue
            related_field = childrens[i].field.name
            method = getattr(childrens[i], 'get_accessor_name')
            method_name = method()
            
            children_items = []
            method_callable = hasattr(self.obj, method_name)
            if method_callable:
                method_called = getattr(self.obj, method_name)
                children_items = getattr(method_called, 'all')()

            d = []
            for child in children_items:
                si = self.__class__(child,
                                    excluded_fields=self.excluded_fields,
                                    duplicate=self.duplicate)
                si.serialize_tree()
                si.dict['related_field'] = related_field
                if self.duplicate:
                    si.remove_related_field(related_field)
                d.append(si.dict)
        
            self.dict['childrens'].extend(d)

        return self.dict

    def __str__(self):
        return 'Serializable: {} {}'.format(self.model_name, self.obj)

    def __repr__(self):
        return self.__str__()


class ImportableSerializedInstance(BaseSerializableInstance):
    
    def __init__(self, serialized_obj):
        if isinstance(serialized_obj, dict):
            self.dict = serialized_obj
        elif isinstance(serialized_obj, str):
            self.dict = json.loads(sertialized_obj)
        elif isinstance(serialized_obj, io.TextIOWrapper):
            self.dict = json.loads(sertialized_obj.read())
        else:
            raise Exception('Unknown serialized object format')

    def get_save_dict(self, model_obj, obj_dict):
        save_dict = {}
        for ofield in model_obj._meta.fields:
            # is it a relation?
            if isinstance(ofield, ForeignKey) and \
               ofield.attname in obj_dict['object'].keys() and \
               ofield.name in obj_dict['object'].keys():
                   save_dict[ofield.name] = ofield.related_model.objects.get(pk=obj_dict['object'][ofield.attname])
            elif ofield.name in obj_dict['object'].keys():
                save_dict[ofield.name] = obj_dict['object'][ofield.name]
        return save_dict

    def save_m2m(self, obj, m2ms):
        for m2m_key in m2ms:
            for m2m_child in m2ms[m2m_key]:
                m2m_app_name = m2m_child['app_name']
                m2m_model_name = m2m_child['model_name']
                m2m_model_obj = self.app_model(m2m_app_name, m2m_model_name)
                # print(m2m_model_obj, )
                m2m_child_obj = m2m_model_obj.objects.get(**m2m_child['object'])
                getattr(obj, m2m_key).add(m2m_child_obj)
                print('saved m2m: {} {} ({})'.format(m2m_app_name, m2m_model_name,obj))

    def save_object(self, obj_dict, parent_obj=None):
        """
        saves the single instance
        if parents: checks if children object has parent_name(key):None
        then made substitutes None with parent object if available, otherwise save without them
        returns ORM model object
        """
        app_name = obj_dict['app_name']
        model_name = obj_dict['model_name']
        model_obj = self.app_model(app_name, model_name)

        # se uno degli attributi ha oggetti innestati e type == m2m rimuovere attr, salvare e usare .add() sull'obj salvato per aggiungere gli m2m
        # move m2m definition to a private collection and then purge them from original object
        m2ms = { i:[e for e in obj_dict['object'][i]] for i in obj_dict['m2m']}

        # relation to the father
        if parent_obj:
            obj_dict['object'][obj_dict['related_field']] = parent_obj

        # save obj without optional m2m
        print('saving:', obj_dict['object'])
        # detect and fetch fk
        save_dict=self.get_save_dict(model_obj, obj_dict)
        obj = model_obj.objects.filter(**save_dict).last()
        if not obj:
            obj = model_obj.objects.create(**save_dict)
        print('saved: {} {} ({})'.format(app_name, model_name,obj))

        # save each m2m
        self.save_m2m(obj, m2ms)

        # ricorsione per childrens qui
        for child in obj_dict['childrens']:
            self.save_object(child, parent_obj=obj)
        
        return obj

    @transaction.atomic
    def save(self):
        """
        save all the object tree in a transaction
        """
        # save_object and pass it in parents=[] for every children
        obj = self.save_object(self.dict)
        # for every children
        if not self.dict['childrens']: return obj
        for child in self.dict['childrens']:
            self.save_object(child, obj)

        return obj

        
if __name__ == '__main__':
    # NOTES
    from gestione_peo.models import *
    
    bando = Bando.objects.all()[1]

    # object serialization
    # si = SerializableInstance(bando, duplicate=False, auto_fields=True, excluded_fields=[])
    
    # single object duplication
    si = SerializableInstance(bando)
    #si.serialize_obj()
    st = si.serialize_tree()
    # pprint(st)
    
    # main object with childrens
    # sit = SerializableInstanceTree(bando) #, duplicate=False)
    # sit.serialize_tree()
    
    # all the fields
    # bando._meta._forward_fields_map
    
    # childrens here
    # bando._meta.fields_map
    ## bando._meta.related_objects

    # another way with NestedObjects
    # from django.contrib.admin.utils import NestedObjects
    # from django.db import DEFAULT_DB_ALIAS
    
    # get json with pk and autofilled fields as they are
    # from django.core import serializers
    # serializers.serialize('json', [bando], ensure_ascii=False)
    
    # serializers.serialize() relies on it
    # model_to_dict(bando)
    
    #pprint(sit.dict)
    # for i in sit.dict['childrens']:
        # if i['model_name'] == 'IndicatorePonderato':
            # pprint(i)
            
    # tree_to_str = json.dumps(si.dict, indent=2)
    # jsonstr_to_dict = json.loads(tree_to_str)
    # pprint(jsonstr_to_dict )

    isi = ImportableSerializedInstance(si.dict)
    isi.save()
    # print(isi.json())
