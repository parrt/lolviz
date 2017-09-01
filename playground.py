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

def g(x):
    g = callviz()
    print g.source
    g.render(view=True)

def f(x,y):
    g(y)

head = Node('tombu')
head = Node('parrt', head)
head = Node('foo', head)
# g = llistviz(head)

f(989,head)

# g = callviz()
# print g.source
# g.render(view=True)

table = [[3,4], ["aaa",5.3]]
d = {'super cool':table, 'bar':99}
table.append(d)
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
