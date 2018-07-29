from imports import *

def tree_traverse(n_nodes, children_left, children_right):
    """
    Traversing tree structure to compute compute various properties such
    as the depth of each node and whether or not it is a leaf.
    
    Input -
    n_nodes: number of nodes in the tree
    children_left: array of length n_nodes. left children node indexes
    children_right: array of length n_nodes. right children node indexes
    
    Output - 
    is_leaves: array of length n_nodes with boolean whether node i is leaf or not
    
    """
    
    node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaves = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, -1)]  # seed is the root node id and its parent depth
    
    while len(stack) > 0:
        node_id, parent_depth = stack.pop() # (0,-1)
        node_depth[node_id] = parent_depth + 1

        # If we have a test node
        if (children_left[node_id] != children_right[node_id]):
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
            is_leaves[node_id] = True
    
    return is_leaves


def node_string(clf, data, verbose=False, classifier=False, precision=1):
    """
    String to use as input for graphviz

    Input -
    clf: sklearn decision tree model
    data: input training data (without target variable)
    verbose: if Ture, prints the predictions, number of samples and impurity for non-leaf nodes also
    classifier: True if classification problem, False if regression problem
    precision: rounding off precision required to print the predictions, values or impurity


    Output -
    st: string that can be used as input for displaying decision tree using graphviz

    """
    # parsing the tree structure
    n_nodes = clf.tree_.node_count  # total nodes in the tree
    children_left = clf.tree_.children_left  # left children node index
    children_right = clf.tree_.children_right  # right children node index
    feature = clf.tree_.feature  # feature index at splits (-2 means leaf)
    threshold = clf.tree_.threshold  # split threshold values at given feature
    
    is_leaves = tree_traverse(n_nodes, children_left, children_right)
    
    ###############
    # fixed string setup
    st = '\ndigraph G {\n ranksep=equally;\n \
                        splines=line;\n \
                        nodesep=0.5;\n \
                        rankdir=TD;\n \
                        node [shape=plain width=1.5 height=0.5 fixedsize=False];\n \
                        edge [arrowsize=0.5]\n'

    # non leaf node feature names
    for i in range(n_nodes):
        if not is_leaves[i]:  # non leaf nodes
            st += str(i) + " [label=\"%s \"]" % (str(data.columns[feature[i]]))
            st += '\n '

    # get target values for leaf nodes
    for i in range(n_nodes):
        if is_leaves[i]:
            value = clf.tree_.value[i][0]
            node_samples = clf.tree_.n_node_samples
            impurity = clf.tree_.impurity

            st += str(i) + " [shape=box label=\"prediction=%s \n samples=%s \n mse=%s \"]" % \
                (str(np.round(value[0], precision)),
                 node_samples[i],
                 np.round(impurity[i], precision))

    # non leaf edges with > and <=
    for i in range(n_nodes):
        if not is_leaves[i]:
            st += str(i) + "->" + str(children_left[i]) + " [label=\"<%s\"]" % str(
                np.round(threshold[i], precision))
            st += str(i) + "->" + str(children_right[i]) + " [label=\">=%s\"]" % str(
                np.round(threshold[i], precision))

    # end of string
    st = st+'}'

    return st

if __name__=="__main__":
    
    # loading diabetes data
    diabetes = load_boston()
    data = pd.DataFrame(boston.data)
    data.columns = boston.feature_names
    
    # decision tree
    clf = tree.DecisionTreeRegressor(max_depth=3)
    clf = clf.fit(data, boston.target)
    
    # graphviz dot
    st = node_string(clf, data)
    display(graphviz.Source(st))
