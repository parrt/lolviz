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

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

color_blind_friendly_colors = {
    'redorange': '#f46d43',
    'orange': '#fdae61', 'yellow': '#fee090', 'sky': '#e0f3f8',
    'babyblue': '#abd9e9', 'lightblue': '#74add1', 'blue': '#4575b4'
}

color_blind_friendly_colors = [
    None, # 0 classes
    None, # 1 class
    [YELLOW,BLUE], # 2 classes
    [YELLOW,BLUE,GREEN], # 3 classes
    [YELLOW,BLUE,GREEN,'#a1dab4'], # 4
    [YELLOW,BLUE,GREEN,'#a1dab4','#41b6c4'], # 5
    [YELLOW,'#c7e9b4','#7fcdbb','#41b6c4','#2c7fb8','#253494'], # 6
    [YELLOW,'#c7e9b4','#7fcdbb','#41b6c4','#1d91c0','#225ea8','#0c2c84'], # 7
    [YELLOW,'#edf8b1','#c7e9b4','#7fcdbb','#41b6c4','#1d91c0','#225ea8','#0c2c84'], # 8
    [YELLOW,'#ece7f2','#d0d1e6','#a6bddb','#74a9cf','#3690c0','#0570b0','#045a8d','#023858'], # 9
    [YELLOW,'#e0f3f8','#313695','#fee090','#4575b4','#fdae61','#abd9e9','#74add1','#d73027','#f46d43'] # 10
]

# for x in color_blind_friendly_colors[2:]:
#     print(x)

max_class_colors = len(color_blind_friendly_colors)-1


def tree_traverse(n_nodes, children_left, children_right):
    """
    Derives code from http://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html
    to walk tree

    Traversing tree structure to compute compute various properties such
    as the depth of each node and whether or not it is a leaf.

    Input -
    n_nodes: number of nodes in the tree
    children_left: array of length n_nodes. left children node indexes
    children_right: array of length n_nodes. right children node indexes

    :return:
        is_leaf: array of length n_nodes with boolean whether node i is leaf or not,
        node_depth: depth of each node from root to node. root is depth 0
    """
    node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaf = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, -1)]  # seed is the root node id and its parent depth

    while len(stack) > 0:
        node_id, parent_depth = stack.pop()  # (0,-1)
        node_depth[node_id] = parent_depth + 1

        # If we have a non-leaf node
        if children_left[node_id] != children_right[node_id]:
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
            is_leaf[node_id] = True

    return is_leaf, node_depth


# def shadow_decision_tree(tree):
#     n_nodes = tree.node_count
#     children_left = tree.children_left
#     children_right = tree.children_right
#
#     def walk(node_id):
#         if (children_left[node_id] != children_right[node_id]): # decision node
#             left = walk(children_left[node_id])
#             right = walk(children_right[node_id])
#             return DecTreeNode(node_id, left, right)
#         else:  # leaf
#             return DecTreeNode(node_id)
#
#     root_node_id = 0
#     return walk(root_node_id)


# def dectree_max_depth(tree):
#     n_nodes = tree.node_count
#     children_left = tree.children_left
#     children_right = tree.children_right
#
#     def walk(node_id):
#         if (children_left[node_id] != children_right[node_id]):
#             left_max = 1 + walk(children_left[node_id])
#             right_max = 1 + walk(children_right[node_id])
#             #             if node_id<100: print(f"node {node_id}: {left_max}, {right_max}")
#             return max(left_max, right_max)
#         else:  # leaf
#             return 1
#
#     root_node_id = 0
#     return walk(root_node_id)


def dtreeviz(tree, X, y, precision=1, classnames=None, orientation="LR"):
    def get_feature(i):
        name = X.columns[feature[i]]
        node_name = ''.join(c for c in name if c not in string.punctuation)+str(i)
        node_name = re.sub("["+string.punctuation+string.whitespace+"]", '_', node_name)
        return name, node_name

    def round(v,ndigits=precision):
        return format(v, '.' + str(ndigits) + 'f')

    def dec_node_box(name, node_name, split):
        html = """<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        <tr>
          <td colspan="3" align="center" cellspacing="0" cellpadding="0" bgcolor="#fefecd" border="1" sides="b"><font face="Helvetica" color="#444443" point-size="12">{name}</font></td>
        </tr>
        <tr>
          <td colspan="3" cellpadding="1" border="0" bgcolor="#fefecd"></td>
        </tr>
        <tr>
          <td cellspacing="0" cellpadding="0" bgcolor="#fefecd" border="1" sides="r" align="right"><font face="Helvetica" color="#444443" point-size="11">split</font></td>
          <td cellspacing="0" cellpadding="0" border="0"></td>
          <td cellspacing="0" cellpadding="0" bgcolor="#fefecd" align="left"><font face="Helvetica" color="#444443" point-size="11">{split}</font></td>
        </tr>
        </table>""".format(name=name, split=split)
        return '{node_name} [shape=box label=<{label}>]\n'.format(label=html, node_name=node_name)

    def dec_node(name, node_name, split):
        html = """<font face="Helvetica" color="#444443" point-size="12">{name}<br/>@{split}</font>""".format(name=name, split=split)
        return '{node_name} [shape=none label=<{label}>]\n'.format(label=html, node_name=node_name)

    def prop_size(n):
        margin_range = (0.00, 0.3)
        if sample_count_range>0:
            zero_to_one = (n - min_samples) / sample_count_range
            return zero_to_one * (margin_range[1] - margin_range[0]) + margin_range[0]
        else:
            return margin_range[0]

    # parsing the tree structure
    n_nodes = tree.node_count  # total nodes in the tree
    children_left = tree.children_left  # left children node index
    children_right = tree.children_right  # right children node index
    feature = tree.feature  # feature index at splits (-2 means leaf)
    threshold = tree.threshold  # split threshold values at given feature

    is_leaf, node_depth = tree_traverse(n_nodes, children_left, children_right)

    ranksep = ".22"
    if orientation=="TD":
        ranksep = ".35"
    st = '\ndigraph G {splines=line;\n \
                        nodesep=0.1;\n \
                        ranksep=%s;\n \
                        rankdir=%s;\n \
                        node [margin="0.03" penwidth="0.5" width=.1, height=.1];\n \
                        edge [arrowsize=.4 penwidth="0.5"]\n' % (ranksep,orientation)

    # Define decision nodes (non leaf nodes) as feature names
    for i in range(n_nodes):
        if not is_leaf[i]:  # non leaf nodes
            name, node_name = get_feature(i)
            # st += dec_node_box(name, node_name, split=round(threshold[i]))
            st += dec_node(name, node_name, split=round(threshold[i]))

    # non leaf edges with > and <=
    for i in range(n_nodes):
        if not is_leaf[i]:
            name, node_name = get_feature(i)
            left, left_node_name = get_feature(children_left[i])
            if is_leaf[children_left[i]]:
                left = left_node_name ='leaf%d' % children_left[i]
            right_name, right_node_name = get_feature(children_right[i])
            if is_leaf[children_right[i]]:
                right = right_node_name ='leaf%d' % children_right[i]
            split = round(threshold[i])
            left_html = '<font face="Helvetica" color="#444443" point-size="11">&lt;</font>'
            right_html = '<font face="Helvetica" color="#444443" point-size="11">&ge;</font>'
            if orientation=="TD":
                ldistance = ".9"
                rdistance = ".9"
                langle = "-28"
                rangle = "28"
            else:
                ldistance = "1.3" # not used in LR mode; just label not taillable.
                rdistance = "1.3"
                langle = "-90"
                rangle = "90"
            blankedge = 'label=<<font face="Helvetica" color="#444443" point-size="1">&nbsp;</font>>'
            st += '{name} -> {left} [{blankedge} labelangle="{angle}" labeldistance="{ldistance}" {tail}label=<{label}>]\n'\
                      .format(label="",#left_html,
                              angle=langle,
                              ldistance=ldistance,
                              name=node_name,
                              blankedge = "",#blankedge,
                              tail="tail",#""tail" if orientation=="TD" else "",
                              left=left_node_name)
            st += '{name} -> {right} [{blankedge} labelangle="{angle}" labeldistance="{rdistance}" {tail}label=<{label}>]\n' \
                .format(label="",#right_html,
                        angle=rangle,
                        rdistance=rdistance,
                        name=node_name,
                        blankedge="",#blankedge,
                        tail="tail",# "tail" if orientation == "TD" else "",
                        right=right_node_name)

    # find range of leaf sample count
    leaf_sample_counts = [tree.n_node_samples[i] for i in range(n_nodes) if is_leaf[i]]
    min_samples = min(leaf_sample_counts)
    max_samples = max(leaf_sample_counts)
    sample_count_range = max_samples - min_samples
    print(leaf_sample_counts)
    print("range is ", sample_count_range)

    # is_classifier = hasattr(tree, 'n_classes')
    is_classifier = tree.n_classes > 1
    color_values = list(reversed(color_blind_friendly_colors))
    n_classes = tree.n_classes[0]
    color_values = color_blind_friendly_colors[n_classes]
    # color_values = [c+"EF" for c in color_values] # add alpha

    # Define leaf nodes (after edges so >= edges shown properly)
    for i in range(n_nodes):
        if is_leaf[i]:
            node_samples = tree.n_node_samples[i]
            impurity = tree.impurity

            if is_classifier:
                counts = np.array(tree.value[i][0])
                predicted_class = np.argmax(counts)
                predicted = predicted_class
                if classnames:
                    predicted = classnames[predicted_class]
                ratios = counts / node_samples # convert counts to ratios totalling 1.0
                ratios = [round(r,3) for r in ratios]
                color_spec = ["{c};{r}".format(c=color_values[i],r=r) for i,r in enumerate(ratios)]
                color_spec = ':'.join(color_spec)
                if n_classes > max_class_colors:
                    color_spec = YELLOW
                html = """<font face="Helvetica" color="black" point-size="12">{predicted}<br/>&nbsp;</font>""".format(predicted=predicted)
                margin = prop_size(node_samples)
                st += 'leaf{i} [height=0 width="0.4" margin="{margin}" style={style} fillcolor="{colors}" shape=circle label=<{label}>]\n' \
                    .format(i=i, label=html, name=node_name, colors=color_spec, margin=margin,
                            style='wedged' if n_classes<=max_class_colors else 'filled')
            else:
                value = tree.value[i][0]
                html = """<font face="Helvetica" color="#444443" point-size="11">"""+round(value[0])+"""</font>"""
                margin = prop_size(node_samples)
                st += 'leaf{i} [margin="{margin}" style=filled fillcolor="{color}" shape=circle label=<{label}>]\n'\
                    .format(i=i, label=html, name=node_name, color=YELLOW, margin=margin)


    # end of string
    st = st+'}'

    return st

def boston():
    regr = tree.DecisionTreeRegressor(max_depth=4, random_state=666)
    boston = load_boston()

    print(boston.data.shape, boston.target.shape)

    data = pd.DataFrame(boston.data)
    data.columns =boston.feature_names

    regr = regr.fit(data, boston.target)

    # st = dectreeviz(regr.tree_, data, boston.target)
    st = dtreeviz(regr.tree_, data, boston.target, orientation="TD")

    with open("/tmp/t3.dot", "w") as f:
        f.write(st)

    return st

def iris():
    clf = tree.DecisionTreeClassifier(max_depth=4, random_state=666)
    iris = load_iris()

    print(iris.data.shape, iris.target.shape)

    data = pd.DataFrame(iris.data)
    data.columns = iris.feature_names

    clf = clf.fit(data, iris.target)

    # st = dectreeviz(clf.tree_, data, boston.target)
    st = dtreeviz(clf.tree_, data, iris.target, orientation="TD"
                  , classnames=["setosa", "versicolor", "virginica"]
                  )

    with open("/tmp/t3.dot", "w") as f:
        f.write(st)

    print(clf.tree_.value)
    return st


class ShadowDecTree:
    """
    A tree that shadows a decision tree as constructed by scikit-learn's
    DecisionTree(Regressor|Classifier).  Each node has left and right
    pointers to child nodes, if any.  As part of build process, the
    samples considered at each decision node or at each leaf node are
    saved into field node_samples.
    """
    def __init__(self, tree, id, left=None, right=None, node_samples=None):
        self.tree = tree
        self.id = id
        self.left = left
        self.right = right
        self.node_samples = node_samples

    def split(self):
        return self.tree.threshold[self.id]

    def feature(self):
        return self.tree.feature[self.id]

    def num_samples(self):
        return self.tree.n_node_samples[self.id] # same as len(self.node_samples)

    def prediction(self):
        is_classifier = self.tree.n_classes > 1
        if is_classifier:
            counts = np.array(tree.value[self.id][0])
            predicted_class = np.argmax(counts)
            return predicted_class
        else:
            return self.tree.value[self.id][0][0]

    def __str__(self):
        if self.left is None and self.right is None:
            return "pred={value},n={n}".format(value=round(self.prediction(),1),n=self.num_samples())
        else:
            return "({f}@{s} {left} {right})".format(f=self.feature(),
                                                     s=round(self.split(),1),
                                                     left=self.left if self.left is not None else '',
                                                     right=self.right if self.right is not None else '')

    @staticmethod
    def get_node_samples(tree_model, data):
        """
        Return dictionary mapping node id to list of sample indexes considered by
        the feature/split decision.
        """
        # Doc say: "Return a node indicator matrix where non zero elements
        #           indicates that the samples goes through the nodes."
        dec_paths = tree_model.decision_path(data)

        # each sample has path taken down tree
        node_to_samples = defaultdict(list)
        for sample_i, dec in enumerate(dec_paths):
            _, nz_nodes = dec.nonzero()
            for node_id in nz_nodes:
                node_to_samples[node_id].append(sample_i)

        return node_to_samples

    @staticmethod
    def from_model(tree_model):
        tree = tree_model.tree_
        children_left = tree.children_left
        children_right = tree.children_right

        node_to_samples = ShadowDecTree.get_node_samples(regr, data)

        def walk(node_id):
            if (children_left[node_id] == -1 and children_right[node_id] == -1):  # leaf
                return ShadowDecTree(tree, node_id, node_samples=node_to_samples[node_id])
            else:  # decision node
                left = walk(children_left[node_id])
                right = walk(children_right[node_id])
                return ShadowDecTree(tree, node_id, left, right,
                                     node_samples=node_to_samples[node_id])

        root_node_id = 0
        return walk(root_node_id)


regr = tree.DecisionTreeRegressor(max_depth=5, random_state=666)
boston = load_boston()

data = pd.DataFrame(boston.data)
data.columns = boston.feature_names

regr = regr.fit(data, boston.target)

dtree = ShadowDecTree.from_model(regr)
print(dtree)

# st = iris()
# st = boston()
# print(st)
# graphviz.Source(st).view()
