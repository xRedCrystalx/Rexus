import sys, uuid, hashlib, typing
sys.dont_write_bytecode = True

class BaseSecuredMeta(type):
    def __new__(cls: str, clsname: type, bases: tuple[str, ...], attrs: dict[str, typing.Any], module=None) -> typing.Any:
        if not module:
            raise RuntimeError("Module not specified.")

        if not (ID := cls.__secured_hash()):
            raise RuntimeError("Cannot initialize class object.")

        if not cls.__self_report(module, ID):
            raise RuntimeError("Not accepted.")

        attrs["_ID"] = ID
        attrs["_MODULE"] = module
        attrs["__setattr__"] = cls.__secured_setattr__
        attrs["__delattr__"] = cls.__secured_delattr__

        del module, ID
        return super().__new__(cls, clsname, bases, attrs)
    
    def __secured_setattr__(self, __name: str, __value: typing.Any, __pass: str) -> None:
        if __pass == self._ID: # TODO
            return __class__.__setattr__(type(self), __name, __value)

    def __secured_delattr__(self, __name: str, __pass: str) -> None:
        if __pass == self._ID: # TODO
            return __class__.__delattr__(type(self), __name)

    def __secured_hash() -> str:
        return hashlib.sha512(str(uuid.uuid4()).encode()).hexdigest()

    def __self_report(module: str, hash: str) -> None:
        # TODO: logic
        return True