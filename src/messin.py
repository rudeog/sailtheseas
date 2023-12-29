import random

random.seed()
h = random.choices([1,2,3],[1,3,1], k=1)
print(h)