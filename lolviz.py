"""
A small set of functions that display lists, dictionaries,
and lists of lists in a reasonable manner using graphviz.
Inspired by the object connectivity graphs in Pythontutor.com
"""
import graphviz
import inspect

def strviz(str):
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """

    s += string_node(str)

    s += '}\n'
    return graphviz.Source(s)


def varviz(varnames, showassoc=False):
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """

    stack = inspect.stack()
    caller = stack[1]
    caller_scopename = caller[3]
    if caller_scopename=='<module>':
        caller_scopename = 'globals'
    scope = caller[0].f_locals

    # Show scope dictionary
    values = []
    for name in varnames:
        v = scope[name]
        if type(v)==list or type(v)==tuple or type(v)==dict or type(v)==str:
            values.append(None)
        else:
            values.append(elviz(v, showassoc))

    html = scopetable_html(caller_scopename, varnames, values)
    s += '    vars [shape="box", color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#D9E6F5", label = <%s>];\n' % html

    # Show data structures in the heap
    for name in varnames:
        v = scope[name]
        if type(v)==list or type(v)==tuple:
            s += list_node(v, True)
        if type(v)==dict:
            s += dict_node(v)
        if type(v)==str:
            s += string_node(v)

    # Draw edges to objects in the heap
    for name in varnames:
        v = scope[name]
        if type(v)==list or type(v)==tuple or type(v)==dict or type(v)==str:
            s += 'vars:%s:c -> node%d [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % (name,id(scope[name]))

    s += '}\n'
    return graphviz.Source(s)


def dictviz(d):
    """
    Display a dictionary with the key/value pairs in a vertical list.
    """
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5",shape=box,width=.1,height=.1];
    """
    s += dict_node(d)
    s += '}\n'
    return graphviz.Source(s)


def listviz(elems, showassoc=True):
    """
    Display a list of elements in a horizontal fashion.
    If showassoc, then 2-tuples (3,4) are shown as 3->4.
    """
    s = """
    digraph G {
        nodesep=.05;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """
    if type(elems)==dict:
        return dictviz(elems)

    s += list_node(elems, showassoc)

    s += "}\n"
    return graphviz.Source(s)


def llistviz(head,
             valuefield='value', nextfield='next',
             value=None, next=None): # lambda/functions to obtain value/next fields
    """
    Display a linked list in a horizontal fashion. The fields/attributes
    obtained via getattr() are assumed to be 'value' and 'next' but you
    can passing different names, if you like.  You can also pass in
    lambdas or functions that indicate how to get the node's value or next
    fields. The default is to define value to get field valuefield,
    similar for next.
    """
    if value is None:
        value = lambda p : getattr(p,valuefield)
    if next is None:
        next = lambda p : getattr(p,nextfield)
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        ranksep=.2;
        node [shape=box, penwidth="0.5",width=.1,height=.1];
    """
    p = head
    i = 0
    edges = []
    while p is not None:
        html = llistnode_html(value(p), valuefield, nextfield)
        if next(p) is not None:
            edges.append( (i,i+1) )
        p = next(p)
        s += '    node%d [space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (i,html)
        i += 1

    # draw edges
    for e in edges:
        s += 'node%d:next:c -> node%d:value [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % e

    s += "}\n"
    # print s
    return graphviz.Source(s)


def treeviz(root,
            valuefield='value', leftfield='left', rightfield='right',
            value=None, left=None, right=None): # lambda/functions to obtain value/left/right fields

    if value is None:
        value = lambda p : getattr(p,valuefield)
    if left is None:
        left = lambda p : getattr(p,leftfield)
    if right is None:
        right = lambda p : getattr(p,rightfield)
    s = """
    digraph G {
        nodesep=.2;
        ranksep=.2;
        node [shape=box, penwidth="0.5",width=.1,height=.1];

"""

    nodes = []
    edges = []
    def walk(t,i):
        "Walk recursively to make a list of node definitions. Return the next node number"
        if t is None: return i
        html = treenode_html(value(t), leftfield, rightfield)
        nodes.append('    node%d [space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (i, html))
        ti = i
        i += 1
        lefti = i
        i = walk(left(t), i)
        righti = i
        i = walk(right(t), i)
        if left(t):
            edges.append( (ti,'left',lefti) )
        if right(t):
            edges.append( (ti,'right',righti) )
        return i

    walk(root,0)
    s += '\n'.join(nodes)

    # draw edges
    for e in edges:
        if e[2]=='left':
            s += '    node%d:%s:n -> node%d [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % e
        else:
            s += '    node%d:%s:n -> node%d [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % e

    s += "}\n"
    # print s
    return graphviz.Source(s)


def lolviz(table, showassoc=True):
    """
    Given a list of lists such as:

      [ [('a','3')], [], [('b',230), ('c',21)] ]

    return the dot/graphviz to display as a two-dimensional
    structure.

    If showassoc, display 2-tuples (x,y) as x->y.
    """
    def islol(table):
        for x in table:
            if type(x)==list or type(x)==tuple:
                return True
        return False

    if not islol(table):
        return listviz(table, showassoc)

    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """
    # Make outer list as vertical
    labels = []
    for i in range(len(table)):
        labels.append("<f%d> %d" % (i, i))

    s += '    mainlist [color="#444443", fontsize="9", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#D9E6F5", label = "'+'|'.join(labels)+'"];\n'

    # define inner lists
    for i in range(len(table)):
        bucket = table[i]
        if bucket==None:
            continue
        elements = []
        if (type(bucket)==list or type(bucket)==tuple) and len(bucket) == 0:
            s += 'node%d [margin="0.03", fontname="Italics", shape=none label=<<font color="#444443" point-size="9">empty list</font>>];\n' % id(bucket)
        elif type(bucket)==list or type(bucket)==tuple and len(bucket)>0:
            s += list_node(bucket, showassoc)
            # s += 'node%d [color="#444443", fontname="Helvetica", margin="0.01", space="0.0", shape=record label=<{%s}>];\n' % (i, '|'.join(elements))
        else:
            elements.append(elviz(bucket, showassoc))
            s += 'node%d [color="#444443", fontname="Helvetica", margin="0.01", space="0.0", shape=record label=<{%s}>];\n' % (i, '|'.join(elements))

    # Do edges
    for i in range(len(table)):
        bucket = table[i]
        if bucket==None:
            continue
        s += 'mainlist:f%d -> node%d [penwidth="0.5", color="#444443", arrowsize=.4]\n' % (i,id(bucket))
    s += "}\n"
    # print s
    return graphviz.Source(s)


def elviz(el, showassoc):
    if el is None:
        els = ' '
    elif showassoc and type(el) == tuple and len(el) == 2:
        els = "%s&rarr;%s" % (elviz(el[0], showassoc), elviz(el[1], False))
    elif type(el)==set:
        els = '{'+', '.join([elviz(e, showassoc) for e in el])+'}'
    elif type(el) == dict:
        els = '{' + ','.join([elviz(e, showassoc) for e in el.items()]) + '}'
    else:
        els = repr(el)
    els = els.replace('{', '&#123;')
    els = els.replace('}', '&#125;')
    return els


def label_elviz(label, el, showassoc, port=None):
    if port is None:
        port = label
    return \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
          <tr>
            <td cellspacing="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%s</font></td>
          </tr>
          <tr>
            <td port="%s" bgcolor="#FBFEB0" border="0" align="center"><font point-size="11">%s</font></td>
          </tr>
        </table>
        """ % (label, port, elviz(el,showassoc))


def list_node(elems, showassoc):
    html = listtable_html(elems, showassoc)
    return '    node%d [shape="box", space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (id(elems),html)


def listtable_html(values, showassoc):
    header = \
        """
        <table BORDER="0" CELLBORDER="0" CELLSPACING="0">
        """

    index_html = '<td cellspacing="0" bgcolor="#FBFEB0" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    value_html = '<td port="%d" bgcolor="#FBFEB0" border="1" sides="r" align="center"><font point-size="11">%s</font></td>\n'
    # don't want right border to show on last.
    last_index_html = '<td cellspacing="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    last_value_html = '<td port="%d" bgcolor="#FBFEB0" border="0" align="center"><font point-size="11">%s</font></td>\n'

    lastindex = len(values) - 1
    toprow = [index_html % i for i in range(lastindex)]
    bottomrow = [value_html % (i,elviz(values[i],showassoc)) for i in range(lastindex)]

    toprow.append(last_index_html % (lastindex))
    bottomrow.append(last_value_html % (lastindex, elviz(values[lastindex], showassoc)))

    tail = \
        """
        </table>
        """
    return header + '<tr>\n'+''.join(toprow)+'</tr>\n' + '<tr>\n'+''.join(bottomrow)+'</tr>' + tail


def llistnode_html(nodevalue, valuefield, nextfield):
    return \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
          <tr>
            <td cellspacing="0" bgcolor="#FBFEB0" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%s</font></td>
            <td cellspacing="0" bgcolor="#D9E6F5" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%s</font></td>
          </tr>
          <tr>
            <td port="value" bgcolor="#FBFEB0" border="1" sides="r" align="center"><font point-size="11">%s</font></td>
            <td port="next" bgcolor="#D9E6F5" border="0" align="center"><font point-size="11">%s</font></td>
          </tr>
        </table>
        """ % (valuefield, nextfield, elviz(nodevalue, True), ' ')


def scopetable_html(scopename, names, values):
    header = \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
        """

    blankrow = '<tr><td border="0"></td></tr>'

    scope = '<tr><td cellspacing="0" colspan="2" cellpadding="0" bgcolor="#D9E6F5" border="0" align="center"><font color="#444443" FACE="Times-Italic" point-size="11"><i>%s</i></font></td></tr>\n' % scopename

    rows = []
    rows.append(scope)
    for i in range(len(names)):
        name = '<td cellspacing="0" cellpadding="0" bgcolor="#D9E6F5" border="1" sides="r" align="right"><font color="#444443" point-size="11">%s </font></td>\n' % names[i]
        if values[i] is not None:
            v = values[i]
        else:
            v = ""
        value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="#D9E6F5" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n' % (names[i],v)
        row = '<tr>' + name + value + '</tr>\n'
        rows.append(row)

    tail = \
        """
        </table>
        """
    return header + blankrow.join(rows) + tail


def dict_node(d):
    html = dict_html(d)
    return '    node%d [color="#444443", fontsize="9", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#FBFEB0", label=<%s>];\n' % (id(d),html)


def dict_html(d):
    header = \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
        """
    rows = []
    for key,value in d.items():
        pair = "%s&rarr;%s" % (repr(key),elviz(value,False))
        html = '<td port="%s" cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="0" valign="top" align="left"><font color="#444443" point-size="11">%s</font></td>\n' % (key,pair)
        row = '<tr>\n' + html + '</tr>\n'
        rows.append(row)

    tail = \
        """
        </table>
        """
    return header + ''.join(rows) + tail


def treenode_html(nodevalue, leftfield, rightfield):
    return \
        """
    <table BORDER="0" CELLBORDER="1" CELLSPACING="0" fixedsize="TRUE">
      <tr>
        <td colspan="2" cellspacing="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="11">%s</font></td>
      </tr>
      <tr>
        <td cellspacing="0" cellpadding="1" bgcolor="#D9E6F5" border="1" sides="r" valign="top"><font color="#444443" point-size="7">%s</font></td>
        <td cellspacing="0" bgcolor="#D9E6F5" border="0" valign="top"><font color="#444443" point-size="7">%s</font></td>
      </tr>
      <tr>
        <td port="left" bgcolor="#D9E6F5" border="1" sides="r" align="center"></td>
        <td port="right" bgcolor="#D9E6F5" border="0" align="center"></td>
      </tr>
    </table>
        """ % (elviz(nodevalue, True), leftfield, rightfield)


def string_node(s):
    html = string_html(s)
    return '    node%d [color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#FBFEB0", label=<%s>];\n' % (id(s),html)


def string_html(s):
    values = list(s)
    header = \
        """
        <table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">
        """

    index_html = '<td cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    value_html = '<td cellspacing="0" cellpadding="0" port="%d" bgcolor="#FBFEB0" border="0" align="center"><font face="Monaco" point-size="11">%s</font></td>\n'
    # don't want right border to show on last.
    last_index_html = '<td cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    last_value_html = '<td port="%d" cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="0" align="center"><font face="Monaco" point-size="11">%s</font></td>\n'

    lastindex = len(values) - 1
    toprow = [index_html % i for i in range(lastindex)]
    bottomrow = [value_html % (i,values[i]) for i in range(lastindex)]

    toprow.append(last_index_html % (lastindex))
    bottomrow.append(last_value_html % (lastindex, values[lastindex]))

    tail = \
        """
        </table>
        """
    return header + '<tr><td></td>\n'+''.join(toprow)+'<td></td></tr>\n' + '<tr><td>\'</td>\n'+''.join(bottomrow)+'<td>\'</td></tr>' + tail


def idx_elviz(idx, el, showassoc):
    return label_elviz(str(idx), el, showassoc)


if __name__ == '__main__':
    i = 3
    price = 9.4
    name = 'parrt'
    s = [3, 9, 10]
    t = {'a': 999, 'b': 1}
    g = varviz(['i','name', 's', 't', 'price'])
    # g = strviz('parrt')
    # g = lolviz([[2],[3,4]])
    # g = dictviz(t)
    # g = listviz('parrt')
    print g.source
    g.render(view=True)