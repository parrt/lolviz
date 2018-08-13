import IPython, graphviz, re
from io import StringIO
from IPython.display import Image
import numpy as np
import pandas as pd
import math
from sklearn import tree
from sklearn.datasets import load_boston, load_iris
from collections import defaultdict
import string
import re
import numpy as np
import matplotlib.pyplot as plt

# inspired by Mark Needham's blog
# https://markhneedham.com/blog/2017/09/23/python-3-create-sparklines-using-matplotlib/

#def sparkline(data, filename, fill=False, figsize=(4, 0.25), **kwags):
"""
Save a sparkline image
"""

boston = load_boston()
data = boston.data
features = boston.feature_names
target = boston.target
regr = tree.DecisionTreeRegressor(max_depth=4, random_state=666)
print(features)
print(target)
print(boston.data.shape, boston.target.shape)

fig, ax = plt.subplots(1, 1, figsize=(8,2))
ax.scatter(data[:,0], target, s=2, alpha=.4)
# ax.scatter(data[:,1], target, s=2)
# ax.scatter(data[:,2], target, s=2)
for k,v in ax.spines.items():
    v.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# ax.plot(len(data) - 1, data[len(data) - 1], 'r.')

#ax.fill_between(range(len(data)), data, len(data)*[min(data)], alpha=0.1)

#plt.savefig(filename, transparent=True, bbox_inches='tight', dpi = 300)
plt.show()