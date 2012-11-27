import unittest
import model


class TestModel(unittest.TestCase):
    class Student(model.Base):
        id = model.Property()
        first = model.Property()
        last = model.Property()

    def test_no_init(self):
        student = self.Student()
        self.assertIsNone(student.id)
        self.assertIsNone(student.first)
        self.assertIsNone(student.last)

    def test_partial_init(self):
        student = self.Student(id='1234')
        self.assertEqual(student.id, '1234')
        self.assertIsNone(student.first)
        self.assertIsNone(student.last)

    def test_full_init(self):
        student = self.Student(id='4567', first='Will', last='Smith')
        self.assertEqual(student.id, '4567')
        self.assertEqual(student.first, 'Will')
        self.assertEqual(student.last, 'Smith')

    def test_extra_kwargs_on_init_fail(self):
        with self.assertRaises(TypeError):
            self.Student(id='123', gpa=3.7)

    def test_setting_attributes(self):
        student = self.Student(id='123')
        student.id = '456'
        student.first = 'John'
        student.last = 'Johnson'
        self.assertEqual(student.id, '456')
        self.assertEqual(student.first, 'John')
        self.assertEqual(student.last, 'Johnson')

    def test_attributes_are_not_static(self):
        student1 = self.Student()
        student2 = self.Student()
        student1.id = '1'
        student2.id = '2'
        self.assertEqual(student1.id, '1')
        self.assertEqual(student2.id, '2')


class TestOriginalInitPreserved(unittest.TestCase):
    class Foo(model.Base):
        bar = model.Property()

        def __init__(self, baz=None):
            self.baz = baz

    def test_no_arg_init(self):
        foo = self.Foo()
        self.assertIsNone(foo.bar)
        self.assertIsNone(foo.baz)

    def test_model_kwarg_init(self):
        foo = self.Foo(bar='barbarbar')
        self.assertEqual(foo.bar, 'barbarbar')
        self.assertIsNone(foo.baz)

    def test_regular_kwarg_init(self):
        foo = self.Foo(baz='baaaaz!')
        self.assertIsNone(foo.bar)
        self.assertEqual(foo.baz, 'baaaaz!')

    def test_regular_positional_arg_init(self):
        foo = self.Foo('baaaaz!')
        self.assertIsNone(foo.bar)
        self.assertEqual(foo.baz, 'baaaaz!')

    def test_full_init_with_kwargs(self):
        foo = self.Foo(bar='moes', baz='sheep')
        self.assertEqual(foo.bar, 'moes')
        self.assertEqual(foo.baz, 'sheep')

    def test_full_init_with_positional(self):
        foo = self.Foo('sheep', bar='moes')
        self.assertEqual(foo.bar, 'moes')
        self.assertEqual(foo.baz, 'sheep')


class TestInheritance(unittest.TestCase):

    class IDObject(model.Base):
        id = model.Property()

    class Student(IDObject):
        first = model.Property()
        last = model.Property()

    def test_create_derived(self):
        student = self.Student()
        self.assertIsNone(student.id)
        self.assertIsNone(student.first)
        self.assertIsNone(student.last)

    def test_create_derived_with_derived_params(self):
        student = self.Student(first='Malcolm', last='Reynolds')
        self.assertIsNone(student.id)
        self.assertEqual(student.first, 'Malcolm')
        self.assertEqual(student.last, 'Reynolds')

    def test_create_derived_with_base_params(self):
        student = self.Student(id='abcd')
        self.assertEqual(student.id, 'abcd')
        self.assertIsNone(student.first)
        self.assertIsNone(student.last)

    def test_create_derived_with_all_params(self):
        student = self.Student(id='abcd', first='Malcolm', last='Reynolds')
        self.assertEqual(student.id, 'abcd')
        self.assertEqual(student.first, 'Malcolm')
        self.assertEqual(student.last, 'Reynolds')

    def test_set_params(self):
        student = self.Student()
        student.id = 'efgh'
        student.first = 'Mickey'
        student.last = 'Rooney'
        self.assertEqual(student.id, 'efgh')
        self.assertEqual(student.first, 'Mickey')
        self.assertEqual(student.last, 'Rooney')


class TestInitMethodsAndInheritance(unittest.TestCase):

    class Base(model.Base):
        base_prop = model.Property()

        def __init__(self, base_attr):
            self.base_attr = base_attr

    class Derived(Base):
        derived_prop = model.Property()

        def __init__(self, base_attr, derived_attr):
            super(self.__class__, self).__init__(base_attr)
            self.derived_attr = derived_attr

    def test_positional_attr_init(self):
        d = self.Derived('ba', 'da')
        self.assertIsNone(d.base_prop)
        self.assertIsNone(d.derived_prop)
        self.assertEqual(d.base_attr, 'ba')
        self.assertEqual(d.derived_attr, 'da')

    def test_full_init(self):
        d = self.Derived(base_attr='ba', base_prop='bp',
                         derived_attr='da', derived_prop='dp')
        self.assertEqual(d.base_attr, 'ba')
        self.assertEqual(d.base_prop, 'bp')
        self.assertEqual(d.derived_attr, 'da')
        self.assertEqual(d.derived_prop, 'dp')
        
    def test_full_init_with_positional_args(self):
        d = self.Derived('ba', 'da', base_prop='bp', derived_prop='dp')
        self.assertEqual(d.base_attr, 'ba')
        self.assertEqual(d.base_prop, 'bp')
        self.assertEqual(d.derived_attr, 'da')
        self.assertEqual(d.derived_prop, 'dp')


class Person(model.Base):
    name = model.Property()

    def greet(self):
        return 'My name is %s.' % self.name


class TestProxy(unittest.TestCase):
    class PersonProxy(model.Proxy):
        wrapped = Person

    def test_property_get(self):
        person = Person(name='Fred')
        proxy = self.PersonProxy(person)
        self.assertEqual(proxy.name, 'Fred')

    def test_property_set(self):
        person = Person()
        proxy = self.PersonProxy(person)
        proxy.name = 'Wilma'
        self.assertEqual(proxy.name, 'Wilma')
        self.assertEqual(person.name, 'Wilma')

    def test_method_call(self):
        person = Person(name='Henry')
        proxy = self.PersonProxy(person)
        greeting = proxy.greet()
        self.assertEqual(greeting, 'My name is Henry.')


class TestProxyMethodReplacement(unittest.TestCase):
    class PersonProxy(model.Proxy):
        wrapped = Person

        def greet(self):
            return 'Hello, World! %s' % self.wrapped.greet()

    def test_replaced_method(self):
        person = Person(name='Larry')
        proxy = self.PersonProxy(person)
        self.assertEquals(proxy.greet(), 'Hello, World! My name is Larry.')


class TestException(Exception):
    pass


class TestProxyAttributeReplacement(unittest.TestCase):
    class PersonProxy(model.Proxy):
        wrapped = Person

        name = model.PropertyProxy()

        @name.setter
        def set_name(self, name):
            if not name.istitle():
                raise TestException()
            self.wrapped.name = name

    def test_replaced_setter(self):
        person = Person()
        proxy = self.PersonProxy(person)
        with self.assertRaises(TestException):
            proxy.name = 'seamus'

    def test_underlying_setter_unaffected(self):
        person = Person()
        proxy = self.PersonProxy(person)
        person.name = 'seamus'
        self.assertEquals(proxy.name, 'seamus')
