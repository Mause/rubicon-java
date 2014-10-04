# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import bootstrap

import math
from unittest import TestCase

from rubicon.java import JavaClass, JavaInterface


class JNITest(TestCase):

    def test_simple_object(self):

        Stack = JavaClass('java/util/Stack')

        stack = Stack()

        stack.push("Hello")
        stack.push("World")

        # The stack methods are protyped to return java/lang/Object,
        # so we need to call toString() to get the actual content...
        self.assertEqual(stack.pop().toString(), "World")
        self.assertEqual(stack.pop().toString(), "Hello")

        # with self.assertRaises(Exception):
            # stack.pop()

    def test_field(self):
        "A field on an instance can be accessed and mutated"
        Example = JavaClass('org/pybee/test/Example')

        obj = Example()

        self.assertEqual(obj.base_int_field, 22)
        self.assertEqual(obj.int_field, 33)

        obj.base_int_field = 8888
        obj.int_field = 9999

        self.assertEqual(obj.base_int_field, 8888)
        self.assertEqual(obj.int_field, 9999)

    def test_method(self):
        "An instance method can be invoked."
        Example = JavaClass('org/pybee/test/Example')

        obj = Example()
        self.assertEqual(obj.get_base_int_field(), 22)
        self.assertEqual(obj.get_int_field(), 33)

        obj.set_base_int_field(8888)
        obj.set_int_field(9999)

        self.assertEqual(obj.get_base_int_field(), 8888)
        self.assertEqual(obj.get_int_field(), 9999)

    def test_static_field(self):
        "A static field on a class can be accessed and mutated"
        Example = JavaClass('org/pybee/test/Example')

        Example.static_base_int_field = 1188
        Example.static_int_field = 1199

        self.assertEqual(Example.static_base_int_field, 1188)
        self.assertEqual(Example.static_int_field, 1199)

    def test_static_method(self):
        "A static method on a class can be invoked."
        Example = JavaClass('org/pybee/test/Example')

        Example.set_static_base_int_field(2288)
        Example.set_static_int_field(2299)

        self.assertEqual(Example.get_static_base_int_field(), 2288)
        self.assertEqual(Example.get_static_int_field(), 2299)

    def test_multiple_constructor(self):
        "Check that the right constructor is activated based on arguments used"
        Example = JavaClass('org/pybee/test/Example')

        obj1 = Example()
        obj2 = Example(2242)
        obj3 = Example(3342, 3337)

        self.assertEqual(obj1.base_int_field, 22)
        self.assertEqual(obj1.int_field, 33)

        self.assertEqual(obj2.base_int_field, 44)
        self.assertEqual(obj2.int_field, 2242)

        self.assertEqual(obj3.base_int_field, 3342)
        self.assertEqual(obj3.int_field, 3337)

    def test_static_access_non_static(self):
        "An instance field/method cannot be accessed from the static context"
        Example = JavaClass('org/pybee/test/Example')

        obj = Example()

        with self.assertRaises(AttributeError):
            obj.static_int_field

        with self.assertRaises(AttributeError):
            obj.get_static_int_field()

    def test_non_static_access_static(self):
        "A static field/method cannot be accessed from an instance context"
        Example = JavaClass('org/pybee/test/Example')

        with self.assertRaises(AttributeError):
            Example.int_field

        with self.assertRaises(AttributeError):
            Example.get_int_field()

    def test_string_argument(self):
        "A method with a string argument can be passed."
        Example = JavaClass('org/pybee/test/Example')
        example = Example()
        self.assertEqual(example.duplicate_string("Wagga"), "WaggaWagga")

    def test_string_return(self):
        "If a method or field returns a string, you get a Python string back"
        Example = JavaClass('org/pybee/test/Example')
        example = Example()
        self.assertEqual(example.toString(), "This is a Java Example object")

    def test_float_method(self):
        "A method with a float arguments can be handled."
        Example = JavaClass('org/pybee/test/Example')
        example = Example()
        self.assertEqual(example.area_of_square(1.5), 2.25)

    def test_double_method(self):
        "A method with a double arguments can be handled."
        Example = JavaClass('org/pybee/test/Example')
        example = Example()
        self.assertEqual(example.area_of_circle(1.5), 1.5 * math.pi)

    def test_object_return(self):
        "If a method or field returns an object, you get an instance of that type returned"
        Example = JavaClass('org/pybee/test/Example')
        example = Example()

        Thing = JavaClass('org/pybee/test/Thing')
        thing = Thing('This is thing', 2)

        example.set_thing(thing)

        the_thing = example.get_thing()
        self.assertEqual(the_thing.toString(), "This is thing 2")

    def test_interface(self):
        "An Java interface can be defined in Python and proxied."
        # ICallback = JavaInterface('org/pybee/test/ICallback')
        ICallback = JavaInterface('org/pybee/test/ICallback')

        results = {}

        class MyInterface(ICallback):
            def __init__(self, value):
                super(MyInterface, self).__init__()
                self.value = value

            def poke(self, example, value):
                results['string'] = example.toString()
                results['int'] = value + self.value

            def peek(self, example, value):
                results['string'] = example.toString()
                results['int'] = value + self.value

        # Create two handler instances so we can check the right one
        # is being invoked.
        handler1 = MyInterface(5)
        handler2 = MyInterface(10)

        # Create an Example object, and register a handler with it.
        Example = JavaClass('org/pybee/test/Example')
        example = Example()
        example.set_callback(handler2)

        # Invoke the callback; check that the results have been peeked as expected
        example.test_peek(42)

        self.assertEqual(results['string'], 'This is a Java Example object')
        self.assertEqual(results['int'], 52)

        example.test_poke(37)

        self.assertEqual(results['string'], 'This is a Java Example object')
        self.assertEqual(results['int'], 47)

    def test_alternatives(self):
        "A class is aware of it's type heirarchy"
        Example = JavaClass('org/pybee/test/Example')

        Example._load()
        self.assertEqual(
            Example.__dict__['_types'],
            [
                "Lorg/pybee/test/Example;",
                "Lorg/pybee/test/BaseExample;",
                "Ljava/lang/Object;",
            ])

        AbstractCallback = JavaClass('org/pybee/test/AbstractCallback')
        AbstractCallback._load()
        self.assertEqual(
            AbstractCallback.__dict__['_types'],
            [
                "Lorg/pybee/test/AbstractCallback;",
                "Lorg/pybee/test/ICallback;",
                "Ljava/lang/Object;",
            ])

    def test_inner(self):
        "Inner classes can be accessed, instantiated and invoked"

        Example = JavaClass('org/pybee/test/Example')
        Inner = JavaClass('org/pybee/test/Example$Inner')

        self.assertEqual(Inner.INNER_CONSTANT, 1234)

        # obj = Inner()
        # self.assertEqual(obj.the_answer(True), 42)
        # self.assertEqual(obj.the_answer(False), 54)