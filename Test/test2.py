class SetAttrMeta(type):
    def __setattr__(cls, name, value):
        if name == "TEST":
            return super().__setattr__(name, value)
        else:
            print("Hey, you can't set {0} to {1}!".format(name, value))

class C(metaclass=SetAttrMeta):
    pass

c = C()

c.sp = "Egg"
