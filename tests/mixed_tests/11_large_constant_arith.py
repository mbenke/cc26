def f(a: int) -> int:
    return a + 3000000000

def g(a: int) -> int:
    return a - 3000000000

def h(a: int) -> int:
    return a * 3000000000

x = input_int()
y = x + 3000000000
print(y)
z = x - 3000000000
print(z)
print(f(x))
print(g(x))
print(h(x))
