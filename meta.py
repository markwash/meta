class Property(object):
    def __init__(self):
        self.name = None

    def __get__(self, obj, type=None):
        print self.name
        if not hasattr(obj, self.name):
            setattr(obj, self.name, None)
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)

class Base(object):
    def __init__(self, **kwargs):
        for name, attribute in self.__class__.__dict__.items():
            if isinstance(attribute, Property):
                attribute.name = '_meta_{}'.format(name)
                if name in kwargs:
                    setattr(self, name, kwargs.pop(name))
        if len(kwargs) > 0:
            message = "unexpected keyword argument '{}'"
            raise TypeError(message.format(kwargs.popitem()[0]))
