"""
models that work together with SQLModel+SQLAlchemy
you need to install fundamend[sqlmodels] to use this sub-package
"""

# the models here do NOT inherit from the original models, because I didn't manage to fix the issue that arise:
# <frozen abc>:106: in __new__
#     ???
# E   TypeError: Anwendungshandbuch.__init_subclass__() takes no keyword arguments
#
# or
#
# ..\.tox\dev\Lib\site-packages\sqlmodel\main.py:697: in get_sqlalchemy_type
#     raise ValueError(f"{type_} has no matching SQLAlchemy type")
# E   ValueError: <class 'fundamend.models.anwendungshandbuch.Anwendungshandbuch'> has no matching SQLAlchemy type
# => you need to keep the models in sync manually by now





