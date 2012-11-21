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
        properties = klass._find_model_properties(cls_dict)
        klass._plug_in_properties(properties)
        init = klass._transform_init(properties, cls_dict.get('__init__'))
        cls_dict['__init__'] = init
        return super(ModelMeta, klass).__new__(klass, name, bases, cls_dict)

    @classmethod
    def _find_model_properties(klass, cls_dict):
        return dict([(name, value) for name, value in cls_dict.items()
                     if isinstance(value, Property)])

    @classmethod
    def _plug_in_properties(klass, properties):
        for name, prop in properties.items():
            if prop.name is None:
                prop.name = name

    @classmethod
    def _transform_init(klass, properties, original_init=None):
        def transformed_init(self, *args, **kwargs):
            self._model = {}
            for name, prop in properties.items():
                self._model[name] = {}
                if name in kwargs:
                    setattr(self, name, kwargs.pop(name))
            if original_init is not None:
                original_init(self, *args, **kwargs)
            else:
                if len(args) > 0 or len(kwargs) > 0:
                    raise TypeError('unexpected arguments')
        return transformed_init


class Base(object):
    __metaclass__ = ModelMeta
