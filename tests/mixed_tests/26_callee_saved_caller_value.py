def g(x: int) -> int:
    y = x + 1
    print(0)
    return y

def f(a: int) -> int:
    b = g(a)
    return a + b

print(f(10))
