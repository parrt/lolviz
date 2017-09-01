"""
A small set of functions that display lists, dictionaries,
and lists of lists in a reasonable manner using graphviz.
Inspired by the object connectivity graphs in Pythontutor.com.
I love Pythontutor.com for interactive demos with the students,
but for expository material that must stand on its own, it's
useful to freeze dry / snapshot various states of execution.
Currently I have two cut-and-paste or awkwardly embed pythontutor
into my notes.
"""
import graphviz
import inspect
import types
import sys

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

def strviz(str):
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", width=.1,height=.1];
    """

    s += string_node(str)

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
        node [penwidth="0.5", width=.1,height=.1];
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
    if not islol(table):
        return listviz(table, showassoc)

    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", width=.1,height=.1];
    """

    nodes,edges = lol_nodes(table, showassoc)
    s += ''.join(nodes.values())
    s += ''.join(edges)

    s += "}\n"
    # print s
    return graphviz.Source(s)


def callviz(frame=None, varnames=[]):
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", shape=box, width=.1, height=.1];

    """

    # Get stack frame nodes so we can stack 'em up
    stack = inspect.stack()
    callstack = []
    for i,st in enumerate(stack[1:]):
        frame = st[0]
        name = st[3]
        callstack.append(frame)
        if name=='<module>':
            break

    s += "\n{ rank=same;\n"
    callstack = list(reversed(callstack))
    for f in callstack:
        s += obj_node(f)

    for i in range(len(callstack)-1):
        this = callstack[i]
        callee = callstack[i+1]
        s += 'node%d -> node%d [style=invis]\n' % (id(this), id(callee))
    s += "}\n\n"

    caller = stack[1]
    reachable = closure(caller[0])

    s += obj_nodes(reachable)
    s += obj_edges(reachable)
    s += obj_edges(callstack)
    s += "}\n"

    # print s
    return graphviz.Source(s)

    # s += obj_nodes(reachable)
    # s += obj_edges(reachable)
    # s += "}\n"
    # return graphviz.Source(s)

    # return objviz()
    # caller = stack[1]
    # caller_frame = caller[0]
    # scope = caller_frame.f_locals
    # if varnames is None:
    #     varnames = [sym[0] for sym in scope.items() if not ignoresym(sym)]
    # caller_scopename = caller[2]
    # if caller_scopename=='<module>':
    #     caller_scopename = 'globals'


def ignoresym(sym):
    return sym[0].startswith('_') or\
           callable(sym[1]) or\
           isinstance(sym[1], types.ModuleType) or \
           repr(sym[1]).startswith('<')


def objviz(o):
    """Draw an arbitrary object graph."""
    s = """
digraph G {
    nodesep=.05;
    rankdir=LR;
    node [penwidth="0.5", shape=box, width=.1, height=.1];
    
"""
    reachable = closure(o)
    s += obj_nodes(reachable)
    s += obj_edges(reachable)
    s += "}\n"
    return graphviz.Source(s)


def obj_nodes(nodes):
    s = ""
    # define nodes
    for p in nodes:
        s += obj_node(p)
    return s


def obj_node(p):
    s = ""
    nodename = "node%d" % id(p)
    if type(p) == types.FrameType:
        frame = p
        info = inspect.getframeinfo(frame)
        caller_scopename = info[2]
        if caller_scopename == '<module>':
            caller_scopename = 'globals'
        argnames, _, _ = inspect.getargs(frame.f_code)
        # varnames = [sym[0] for sym in frame.f_locals.items() if not ignoresym(sym)]
        items = []
        # do args first to get proper order
        for arg in argnames:
            v = frame.f_locals[arg]
            if isatom(v):
                items.append((arg, arg, v))
            else:
                items.append((arg, arg, None))
        for k, v in frame.f_locals.items():
            if k in argnames:
                continue
            if ignoresym((k, v)):
                continue
            if isatom(v):
                items.append((k, k, v))
            else:
                items.append((k, k, None))
        s += '// FRAME %s\n' % caller_scopename
        s += gr_dict_node(nodename, caller_scopename, items, highlight=argnames, bgcolor=BLUE,
                          separator=None, reprkey=False)
    elif type(p) == dict:
        print "DRAW DICT", p, '@ node' + nodename
        items = []
        i = 0
        for k, v in p.items():
            if isatom(v):
                items.append((str(i), k, v))
            else:
                items.append((str(i), k, None))
            i += 1
        s += '// DICT\n'
        s += gr_dict_node(nodename, None, items)
    elif hasattr(p, "__iter__") and isatomlist(p):
        print "DRAW LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        s += '// LIST or ITERATABLE\n'
        s += gr_list_node(nodename, elems)
    elif hasattr(p, "__iter__"):
        print "DRAW VERTICAL LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        s += '// VERTICAL LIST or ITERATABLE\n'
        s += gr_vlist_node(nodename, elems)
    elif hasattr(p, "__dict__"):  # generic object
        print "DRAW OBJ", p, '@ node' + nodename
        items = []
        for k, v in p.__dict__.items():
            if isatom(v):
                items.append((k, k, v))
            else:
                items.append((k, k, None))
        s += '// %s OBJECT with fields\n' % p.__class__.__name__
        s += gr_dict_node(nodename, p.__class__.__name__, items, separator=None,
                          reprkey=False)
    else:
        print "CANNOT HANDLE: " + str(p)
    return s


def obj_edges(nodes):
    s = ""
    es = edges(nodes)
    for (p, label, q) in es:
        if type(p) != types.FrameType and type(p) != dict and hasattr(p,"__iter__") and not isatomlist(p):  # edges start at right edge not center for vertical lists
            s += 'node%d:%s -> node%d [arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % (id(p), label, id(q))
        else:
            s += 'node%d:%s:c -> node%d [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % (id(p), label, id(q))

    return s


def lol_nodes(table, showassoc):
    """
    Create and return a dictionary mapping node name to graphviz code for that node.
    Also return a list of edges connecting the outer list to the inner lists.
    """
    nodes = {}
    s = ""
    # Make outer list as vertical
    labels = []
    for i in range(len(table)):
        labels.append("<f%d> %d" % (i, i))
    s = 'node%d [color="#444443", fontsize="9", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#D9E6F5", label = "%s"];\n' % (id(table), '|'.join(labels))
    nodes['node%d'%id(table)] = s
    # define inner lists
    for i in range(len(table)):
        bucket = table[i]
        if bucket == None:
            continue
        if (type(bucket) == list or type(bucket) == tuple) and len(bucket) == 0:
            s = 'node%d [margin="0.03", shape=none label=<<font color="#444443" point-size="9">empty list</font>>];\n' % id(bucket)
        elif type(bucket) == list or type(bucket) == tuple and len(bucket) > 0:
            s = list_node(bucket, showassoc)
        else:
            s = 'node%d [color="#444443", fontname="Helvetica", margin="0.01", space="0.0", label=<{%s}>];\n' % (id(bucket), elviz(bucket, showassoc))
        nodes['node%d' % id(bucket)] = s

    # Do edges
    edges = []
    for i in range(len(table)):
        bucket = table[i]
        if bucket == None:
            continue
        s = 'node%d:f%d -> node%d [penwidth="0.5", color="#444443", arrowsize=.4]\n' % (id(table), i, id(bucket))
        edges.append(s)
    return nodes, edges


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
    els = els.replace('<', '&lt;')
    els = els.replace('>', '&gt;')
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
    header = '<table BORDER="0" CELLBORDER="0" CELLSPACING="0">\n'

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

    tail = "</table>\n"
    return header + '<tr>\n'+''.join(toprow)+'</tr>\n' + '<tr>\n'+''.join(bottomrow)+'</tr>' + tail


def gr_list_node(nodename, elems, bgcolor=YELLOW):
    if len(elems)>0:
        html = gr_listtable_html(elems, bgcolor)
    else:
        html = " "
    return '%s [shape="box", space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (nodename,html)


def gr_listtable_html(values, bgcolor=YELLOW):
    header = '<table BORDER="0" CELLBORDER="0" CELLSPACING="0">\n'

    index_html = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    value_html = '<td port="%d" bgcolor="%s" border="1" sides="r" align="center"><font point-size="11">%s</font></td>\n'
    # don't want right border to show on last.
    last_index_html = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    last_value_html = '<td port="%d" bgcolor="%s" border="0" align="center"><font point-size="11">%s</font></td>\n'

    lastindex = len(values) - 1
    toprow = [index_html % (bgcolor,i) for i in range(lastindex)]
    bottomrow = [value_html % (i,bgcolor,repr(values[i]) if values[i] is not None else ' ') for i in range(lastindex)]

    if len(values)>=1:
        toprow.append(last_index_html % (bgcolor,lastindex))
        bottomrow.append(last_value_html % (lastindex, bgcolor,repr(values[lastindex]) if values[lastindex] is not None else ' '))

    tail = "</table>\n"
    return header + '<tr>\n'+''.join(toprow)+'</tr>\n' + '<tr>\n'+''.join(bottomrow)+'</tr>' + tail


def gr_dict_node(nodename, title, items, highlight=None, bgcolor=YELLOW, separator="&rarr;", reprkey=True):
    html = gr_dict_html(title, items, highlight, bgcolor, separator, reprkey)
    return '%s [margin="0.03", color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (nodename,bgcolor,html)


def gr_dict_html(title, items, highlight=None, bgcolor=YELLOW, separator="&rarr;", reprkey=True):
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'

    blankrow = '<tr><td cellpadding="1" border="0"></td></tr>'

    rows = []
    if title is not None:
        title = '<tr><td cellspacing="0" colspan="3" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (bgcolor, title)
        rows.append(title)

    for label,key,value in items:
        font = "Helvetica"
        if highlight is not None and key in highlight:
            font = "Times-Italic"
        if separator is not None:
            name = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="0" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (bgcolor, font, repr(key) if reprkey else key)
            sep = '<td cellpadding="0" border="0" valign="bottom"><font color="#444443" point-size="9">%s</font></td>' % separator
        else:
            name = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (bgcolor, font, repr(key) if reprkey else key)
            sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

        if value is not None:
            v = repr(value)
        else:
            v = "   "
        value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n' % (label, bgcolor, v)
        row = '<tr>' + name + sep + value + '</tr>\n'
        rows.append(row)

    tail = "</table>\n"
    return header + blankrow.join(rows) + tail


def gr_vlist_node(nodename, elems, bgcolor=GREEN):
    html = gr_vlist_html(elems, bgcolor)
    return '%s [color="#444443", margin="0.02", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (nodename,bgcolor,html)


def gr_vlist_html(elems, bgcolor=GREEN):
    if len(elems)==0:
        return " "
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">\n'

    rows = []
    for i,el in enumerate(elems):
        sides = 'BORDER="1" sides="b" cellpadding="0"'
        if i==len(elems)-1:
            sides='BORDER="0" cellpadding="1"'
        value = '<td port="%d" cellspacing="0" %s bgcolor="%s" align="left"><font color="#444443" point-size="9">%s</font></td>\n' % (i, sides, bgcolor, str(i))
        row = '<tr>' + value + '</tr>\n'
        rows.append(row)

    tail = "</table>\n"
    return header + ''.join(rows) + tail


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


def scopetable_html(scopename, names, values, color="#D9E6F5"):
    header = \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
        """

    blankrow = '<tr><td border="0"></td></tr>'

    scope = '<tr><td cellspacing="0" colspan="2" cellpadding="0" bgcolor="%s" border="0" align="center"><font color="#444443" FACE="Times-Italic" point-size="11"><i>%s</i></font></td></tr>\n' % (scopename,color)

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


def islol(elems):
    if type(elems)!=list:
        return False
    for x in elems:
        if type(x)!=list and type(x)!=tuple and type(elems)!=set:
            return False
    return True


def isatomlist(elems):
    if type(elems)!=list and type(elems)!=tuple and type(elems)!=set:
        return False
    for x in elems:
        if not isatom(x):
            return False
    return True


def isatom(p): return type(p) == int or type(p) == float or type(p) == str


def closure(p):
    """
    Find all nodes reachable from p and return a list of pointers to those reachable.
    There can't be duplicates even for cyclic graphs due to visited set. Chase ptrs
    from but don't include frame objects.
    """
    return closure_(p, set())


def closure_(p, visited):
    if p is None or isatom(p):
        return []
    if id(p) in visited:
        return []
    visited.add(id(p))
    result = []
    if type(p) != types.FrameType:
        result.append(p)
    if type(p) == types.FrameType:
        frame = p
        info = inspect.getframeinfo(frame)
        for k, v in frame.f_locals.items():
            if not ignoresym((k, v)):
                cl = closure_(v, visited)
                result.extend(cl)
        caller_scopename = info[2]
        if caller_scopename != '<module>': # stop at globals
            cl = closure_(p.f_back, visited)
            result.extend(cl)
    elif type(p)==dict:
        for q in p.values():
            cl = closure_(q, visited)
            result.extend(cl)
    elif hasattr(p, "__dict__"): # regular object like Tree or Node
        for q in p.__dict__.values():
            cl = closure_(q, visited)
            result.extend(cl)
    elif hasattr(p, "__iter__"): # a list or similar
        for q in p:
            cl = closure_(q, visited)
            result.extend(cl)
    return result


def edges(reachable):
    "Return list of (p, port-in-p, q)"
    edges = []
    for p in reachable:
        if type(p) == types.FrameType:
            frame = p
            for k, v in frame.f_locals.items():
                if not ignoresym((k, v)) and not isatom(v) and v is not None:
                    edges.append( (frame,k,v) )
        elif type(p)==dict:
            i = 0
            for k,v in p.items():
                if not isatom(v) and v is not None:
                    edges.append( (p,str(i),v) )
                i += 1
        elif hasattr(p, "__iter__"):
            for i,el in enumerate(p):
                if not isatom(el) and el is not None:
                    edges.append( (p,str(i),el) )
        elif hasattr(p,"__dict__"):
            for k,v in p.__dict__.items():
                if not isatom(v) and v is not None:
                    edges.append( (p,k,v) )
    return edges
