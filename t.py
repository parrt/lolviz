from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd


class DecisionNode:
    def __init__(self, split):
        self.split = split

    def predict(self):
        if x < self.split:
            return self.left.predict()
        return self.right.predict()


class LeafNode:
    def __init__(self, values):
        self.values = values

    def predict(self):
        return np.mean(self.values)


class L2Stump:
    def fit(self, x, y):
        """
        We train on the (x,y), getting split of single-var x that
        minimizes variance in subregions of y created with split.
        Predictions are the means of subregions.
        """
        split = self.find_best_split(x, y)
        self.root = DecisionNode(split)
        self.root.left = LeafNode(y[x <= split])
        self.root.right = LeafNode(y[x > split])

    def find_best_split(self, x, y):
        best = np.inf
        for v in x:
            lvar = np.var(y[x <= v])
            rvar = np.var(y[x > v])
            avg = (lvar + rvar) / 2
            if avg < best: best = avg
        return best

    def predict(self, x):
        if isinstance(x, np.ndarray) or isinstance(x, pd.Series):
            return np.array([self.root.predict(xi) for xi in x])
        return self.root.predict(x)

df = pd.DataFrame()
df["sqfeet"] = [750, 800, 850, 900,950]
df["rent"] = [1160, 1200, 1280, 1450,2000]

from lolviz import *

# objviz(df).view()
# objviz(df.rent).view()

t = L2Stump()
t.fit(df.sqfeet, df.rent)
treeviz(t.root).view()