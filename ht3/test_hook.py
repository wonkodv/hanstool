from .hook import *

def test_hook():
    h = Hook()


    X = []

    @h.register
    def callback(x):
        X.append(x)
        return x

    h(1)
    assert X == [1]

    h(2)
    assert X == [1,2]


def test_result_hook():
    h = ResultHook()

    @h.register
    def no0():
        return 0
    @h.register
    def no1():
        return 1
    @h.register
    def no2():
        return None
    @h.register
    def no3():
        return None

    assert h() == 1

