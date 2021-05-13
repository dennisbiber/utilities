import inspect
import re
import unittest

__author__ = 'Dennis Biber'


class ClassInheritanceTest(unittest.TestCase):
    '''
    This is class provides a unittest.TestCase that can check that a class' implementation correctly
    inherits the members of its base class or classes.
    '''

    def _build_class_member_list(self, base_class):
        class_members = set()

        # Check all of the defined members from the base class
        for member_name, _ in inspect.getmembers(base_class):
            # We only want user-defined methods so skip anything starting with __ to avoid
            # all special methods
            if not re.match("__", member_name):
                class_members.add(member_name)

        return class_members

    def _check_inherited_methods(self, test_class, *init_args, **init_kwargs):
        # This function checks that all class methods and properties are properly inherited.
        # It does not check for attributes since they cannot be determined without creating instances
        # of the class and all of its base classes

        test_class_instance = test_class(*init_args, **init_kwargs)

        try:
            # The first entry returned from getmro is the definition for the class itself. Since we want
            # to look at the base classes, we skip the first entry in the list

            for base_class in inspect.getmro(test_class)[1:]:
                attribute_list = self._build_class_member_list(base_class)

                for attribute_name in attribute_list:
                    self.assertTrue(hasattr(test_class_instance, attribute_name), "Instances of the class '{0}' do not have an inherited \
attribute '{1}' from the base class '{2}'".format(test_class.__name__, attribute_name, base_class.__name__))

        except IndexError:
            self.fail("The class {0} does not inherit from {1}".format(test_class.__name__, object.__name__))
