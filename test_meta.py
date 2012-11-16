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

    def test_attributes_are_not_static(self):
        student1 = self.Student()
        student2 = self.Student()
        student1.id = '1'
        student2.id = '2'
        self.assertEqual(student1.id, '1')
        self.assertEqual(student2.id, '2')
