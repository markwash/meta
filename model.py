class Property(object):
    def __init__(self, name=None):
        self.name = name

    def _lookup_storage(self, obj):
        return obj._model[self.name]

    def __get__(self, obj, owner=None):
        if obj is None and owner is not None:
            # This happens if you access the property as a class rather
            # than instance attribute.
            return self
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


class PropertyProxy(object):
    def __init__(self, name=None):
        self.name = name
        self._setter = None
        self._getter = None

    def __get__(self, obj, owner=None):
        if self._getter is not None:
            return self._getter(obj)
        return getattr(obj.wrapped, self.name)

    def __set__(self, obj, value):
        if self._setter is not None:
            self._setter(obj, value)
        setattr(obj.wrapped, self.name, value)

    def setter(self, method):
        """Decorator-style __set__ override"""
        self._setter = method
        return method

    def getter(self, method):
        """Decorator-style __get__ override"""
        self._getter = method


class CallableProxy(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, owner=None):
        return getattr(obj.wrapped, self.name)


class ProxyMeta(type):

    def __new__(klass, name, bases, cls_dict):
        klass.plug_in_properties(name, bases, cls_dict)
        klass.load_proxies(name, bases, cls_dict)
        klass.transform_init(name, bases, cls_dict)
        return super(ProxyMeta, klass).__new__(klass, name, bases, cls_dict)

    @classmethod
    def plug_in_properties(klass, name, bases, cls_dict):
        for name, prop in cls_dict.items():
            if isinstance(prop, PropertyProxy) and prop.name is None:
                prop.name = name

    @classmethod
    def load_proxies(klass, name, bases, cls_dict):
        model = cls_dict['wrapped']
        for name, prop in model.__dict__.items():
            if name in cls_dict:
                continue
            if isinstance(prop, Property):
                cls_dict[name] = PropertyProxy(name)
            elif callable(prop) and not name.startswith('__'):
                cls_dict[name] = CallableProxy(name)

    @classmethod
    def transform_init(klass, name, bases, cls_dict):
        original_init = cls_dict.get('__init__')
        def init(self, wrapped, *args, **kwargs):
            self.wrapped = wrapped
            if original_init is not None:
                original_init(self, wrapped, *args, **kwargs)
        cls_dict['__init__'] = init


class Proxy(object):
    __metaclass__ = ProxyMeta
    wrapped = Base
