class A:
    def __init__(self, func):
        self.func = func


a = A(lambda: print('aaa'))
a.func()