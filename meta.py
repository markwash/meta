class Property(object):
    def __init__(self, name=None):
        self.name = name

    def _lookup_storage(self, obj):
        return obj._model[self.name]

    def __get__(self, obj, type=None):
        storage = self._lookup_storage(obj)
        if not 'value' in storage:
            return None
        return storage['value']

    def __set__(self, obj, value):
        storage = self._lookup_storage(obj)
        storage['value'] = value


class ModelMeta(type):

    def __new__(klass, name, bases, cls_dict):
        klass._plug_in_properties(bases, cls_dict)
        klass._transform_init(bases, cls_dict)
        return super(ModelMeta, klass).__new__(klass, name, bases, cls_dict)

    @classmethod
    def _plug_in_properties(klass, bases, cls_dict):
        for name, prop in cls_dict.items():
            if not isinstance(prop, Property):
                continue
            if prop.name is None:
                prop.name = name

    @classmethod
    def _transform_init(klass, bases, cls_dict):
        original_init = cls_dict.get('__init__')

        def _init_model_properties(self, kwargs):
            for name, prop in cls_dict.items():
                if not isinstance(prop, Property):
                    continue
                if not name in self._model:
                    self._model[name] = {}
                if name in kwargs:
                    setattr(self, name, kwargs.pop(name))
        
        cls_dict['_init_model_properties'] = _init_model_properties
                
        def transformed_init(self, *args, **kwargs):
            if not hasattr(self, '_model'):
                self._model = {}
            self._init_model_properties(kwargs)
            for base in bases:
                if hasattr(base, '_init_model_properties'):
                    base._init_model_properties(self, kwargs)
            if original_init is not None:
                original_init(self, *args, **kwargs)
            else:
                if len(args) > 0 or len(kwargs) > 0:
                    raise TypeError('unexpected arguments')
        
        cls_dict['__init__'] = transformed_init


class Base(object):
    __metaclass__ = ModelMeta
