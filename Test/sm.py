import sys, typing
sys.dont_write_bytecode = True
from meta import BaseSecuredMeta


class Test(object, metaclass=BaseSecuredMeta, module="TEST"):
    def __init__(self) -> None:
        print(self._MODULE)
        print(self._ID)


class Another(object, metaclass=BaseSecuredMeta, module="TEST"):
    def __init__(self) -> None:
        print(self._MODULE)
        print(self._ID)