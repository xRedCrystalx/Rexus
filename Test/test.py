import sys,uuid
sys.dont_write_bytecode = True



def reloader() -> None:
    from sm import Test, Another
    Test()
    Another()
  
    while True:
        ask = input()

        if ask == "reload":
            if "sm" in sys.modules:
                del sys.modules["sm"]

            from sm import Test, Another
            test = Test()
            test.__setattr__("var", True, test._ID)
            print(test.var)

            another = Another()

            print(getattr(test, "var"))
            print(getattr(another, "var"))

reloader()
