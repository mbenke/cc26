from runtime import input_int

def double(x: int) -> int:
    return x + x

n = input_int()
print(double(n))
