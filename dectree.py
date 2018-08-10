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

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"

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


def dectreeviz(root, X, y, precision=1, orientation="LR"):
    def get_feature(i):
        name = X.columns[feature[i]]
        node_name = name.translate(None, string.punctuation)+str(i)
        return name, node_name

    def round(v):
        return format(v, '.' + str(precision) + 'f')

    # parsing the tree structure
    n_nodes = root.node_count  # total nodes in the tree
    children_left = root.children_left  # left children node index
    children_right = root.children_right  # right children node index
    feature = root.feature  # feature index at splits (-2 means leaf)
    threshold = root.threshold  # split threshold values at given feature

    is_leaf, node_depth = tree_traverse(n_nodes, children_left, children_right)

    ranksep = ".22"
    if orientation=="TD":
        ranksep = ".15"
    st = '\ndigraph G {\n ranksep=equally;\n \
                        splines=line;\n \
                        nodesep=0.1;\n \
                        ranksep=%s;\n \
                        rankdir=%s;\n \
                        node [penwidth="0.5" shape=plain fixedsize=False];\n \
                        edge [arrowsize=.4 penwidth="0.5"]\n' % (ranksep,orientation)

    # Define decision nodes (non leaf nodes) as feature names
    for i in range(n_nodes):
        if not is_leaf[i]:  # non leaf nodes
            name, node_name = get_feature(i)
            html = """<table BORDER="0" CELLPADDING="2" CELLBORDER="0" CELLSPACING="0">
            <tr><td><font face="Helvetica" color="#444443" point-size="9">"""+name+"""</font></td></tr>
            </table>"""
            st += '{name} [shape=plain label=<<b>{label}</b>>]\n'.format(label=html, name=node_name)

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
            left_html = '<font face="Helvetica" color="#444443" point-size="8">&lt; %s</font>' % split
            right_html = '<font face="Helvetica" color="#444443" point-size="8">&ge; %s</font>' % split
            if orientation=="TD":
                ldistance = "1.3"
                rdistance = "1.3"
                langle = "-55"
                rangle = "55"
            else:
                ldistance = "1.3" # not used in LR mode; just label not taillable.
                rdistance = "1.3"
                langle = "-90"
                rangle = "90"
            st += '{name} -> {left} [labelangle="{angle}" labeldistance="{ldistance}" {tail}label=< {label} >]\n'\
                      .format(label=left_html,
                              angle=langle,
                              ldistance=ldistance,
                              name=node_name,
                              tail="",#""tail" if orientation=="TD" else "",
                              left=left_node_name)
            st += '{name} -> {right} [labelangle="{angle}" labeldistance="{rdistance}" {tail}label=<{label}>]\n' \
                .format(label=right_html,
                        angle=rangle,
                        rdistance=rdistance,
                        name=node_name,
                        tail="",# "tail" if orientation == "TD" else "",
                        right=right_node_name)

    # Define leaf nodes (after edges so >= edges shown properly)
    for i in range(n_nodes):
        if is_leaf[i]:
            value = clf.tree_.value[i][0]
            node_samples = clf.tree_.n_node_samples
            impurity = clf.tree_.impurity
            # html = '<font face="Helvetica" color="#444443" point-size="9">predict={pred}</font>'.format(pred=round(value[0]))
            html = """<table BORDER="0" CELLPADDING="1" CELLBORDER="0">
            <tr><td><font face="Helvetica" color="#444443" point-size="9">"""+round(value[0])+"""</font></td></tr>
            </table>"""
            st += 'leaf{i} [height=0 width="0" margin="0" fillcolor="{color}" style=filled shape=box label=<{label}>]\n'\
                .format(i=i, label=html, name=node_name, color=YELLOW)


    # end of string
    st = st+'}'

    return st

clf = tree.DecisionTreeRegressor(max_depth=3, random_state=666)
boston = load_boston()

print(boston.data.shape, boston.target.shape)

data = pd.DataFrame(boston.data)
data.columns =boston.feature_names

clf = clf.fit(data, boston.target)

st = dectreeviz(clf.tree_, data, boston.target)
# st = dectreeviz(clf.tree_, data, boston.target, orientation="TD")

print(st)
graphviz.Source(st).view()
