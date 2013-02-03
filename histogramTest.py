#!/usr/bin/python

from numpy.random import normal
gaussian_numbers = normal(size=1000)

import matplotlib.pyplot as plt
from numpy.random import normal
gaussian_numbers = normal(size=1000)
plt.hist(gaussian_numbers, bins=30, normed=True, histtype='step')
plt.title("Rank Histogram")
plt.xlabel("Rank")
plt.ylabel("Frequency")
plt.show()
