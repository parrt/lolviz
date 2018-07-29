import IPython, graphviz, re
import pydotplus
from io import StringIO
from IPython.display import Image  
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn.datasets import load_boston, load_iris