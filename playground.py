from lolviz import *

def hashcode(o): return ord(o)  # assume keys are single-element strings


# test linked list node
class Node:
    def __str__(self):
        return "Node(%s,%s)" % (self.value, str(self.next))

    def __repr__(self):
        return str(self)

    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class User:
    def __init__(self, name):
        self.name = name

class Tree:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def g(x):
    s = "hi"
    g1 = callsviz(varnames=None)
    print g1.source
    g1.view()

def f(x,y):
    t = "mom"
    g(y)

def hashcode(o): return ord(o) # assume keys are single-element strings

table = [ [], [], [], [], [] ]
key = 'a'
value = 99

bucket_index = hashcode(key) % len(table)
bucket = table[bucket_index]
bucket.append( (key,value) ) # add association to the bucket
bucket.append( (key+'x',value+100) ) # add association to the bucket
table[4].append( [9,8,7,6] )

# lolviz(table).view()

# g2 = lolviz(table)
# g2 = strviz('parrt')
# print g2.source
# g2.view()

root = Tree('parrt',
            Tree('mary',
                 Tree('jim',
                      Tree('srinivasan'),
                      Tree('april'))),
            Tree('xue',None,Tree('mike')))

treeviz(root).view()

table = [[3,4], ["aaa",5.3]]
d = {'super cool':table, 'bar':99}
table.append(d)

head = Node('tombu')
head = Node('parrt', head)
head = Node('foo', head)

h = Node('blort', Node(head))

# objviz(root).view()
# lolviz(bucket).view()

# g = llistviz(head)

x = [User('name'+str(i)) for i in range(3)]

f(989,head)

# head2 = ('parrt',('mary',None))
# objviz(head2).view()

# print(root)
# g = callsviz()

# treeviz(root)
# print(g.source)
# g.view(cleanup=True)
# g.render('lolviz', view=True)

#g = callviz()
# print "hashcode =", hashcode(key)
# bucket_index = hashcode(key) % len(table)
# print "bucket_index =", bucket_index
# bucket = table[bucket_index]
# bucket.append((key, value))  # add association to the bucket
# lolviz(table)
# i = 3
# price = 9.4
# name = 'parrt'
# s = [3, 9, 10]
# t = {'a': 999, 'b': 1}


# JUNK DRAWER
#
# from subprocess import check_call
# check_call(['dot','-Tpng','InputFile.dot','-o','OutputFile.png'])
#
# s2 = """
#     digraph G {
#         nodesep=.2;
#         ranksep=.2;
#         node [shape=box, penwidth="0.5",width=.1,height=.1];
#
# """
# s2 += obj_nodes(g)
# s2 += obj_edges(g)
# s2 += '}'
# tr = graphviz.Source(s2)
# tr.save('lolviz_subgraph.dot')
# check_call(['dot', '-Tpng', 'lolviz_subgraph.dot', '-Gdpi=300', '-o', 'lolviz_subgraph.png'])
# check_call(['dot', '-Tpdf', 'lolviz_subgraph.dot', '-o', 'lolviz_subgraph.pdf'])
# check_call(['dot', '-Tgif', 'lolviz_subgraph.dot', '-o', 'lolviz_subgraph.gif'])
# s += 'nodedfadsfasdfasdf [image="lolviz_subgraph.pdf"]'
