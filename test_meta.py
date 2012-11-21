import unittest
import meta


class TestModel(unittest.TestCase):
    class Student(meta.Base):
        id = meta.Property()
        first = meta.Property()
        last = meta.Property()

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
    class Foo(meta.Base):
        bar = meta.Property()

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

    class IDObject(meta.Base):
        id = meta.Property()

    class Student(IDObject):
        first = meta.Property()
        last = meta.Property()

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
