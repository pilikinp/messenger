# class TypedProperty:
#     def __init__(self, name, type):
#         self.name = '_' + name
#         self.type = type
#
#     def __get__(self, instance, cls):
#         return getattr(instance, self.name)
#
#     def __set__(self, instance, value):
#         if not isinstance(value, self.type):
#             raise TypeError('не верный тип данных')
#         setattr(instance, self.name, value)
#
#     def __delete__(self, instance):
#         raise AttributeError('нельзя удалять')
#
# class Foo:
#     name = TypedProperty('name', str)
#     num = TypedProperty('num', int)
#
# f = Foo()
# f.type = 'udblj'
# a = f.type
# f.name = 'udblj'
# f.num = 43
# print(f.num)
# print(a)
import json

class C:
    def __init__(self):
        self._x = None

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = {}
        self._x['a'], self._x['b'] = value


    def pack(self):
        pass

ass = C()
ass.x = (12, 13)
print(ass.x)

