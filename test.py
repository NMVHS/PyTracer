import random

def test(value):
	value.clear()
	value.extend([10000])
	return False


x = [100]

print(test(x))

print(x)

