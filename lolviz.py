"""
A small set of functions that display simple data structures and
arbitrary object graphs in a reasonable manner using graphviz.
Even the call stack can be displayed well.

This is inspired by the object connectivity graphs in Pythontutor.com.
I love Pythontutor.com for interactive demos with the students,
but for expository material that must stand on its own, it's
useful to freeze dry / snapshot various states of execution.
Currently I have two cut-and-paste or awkwardly embed pythontutor
into my notes.
"""
from __future__ import print_function
import graphviz
import inspect
import types
from collections import defaultdict
import sys

YELLOW = "#fefecd" # "#fbfbd0" # "#FBFEB0"
BLUE = "#D9E6F5"
GREEN = "#cfe2d4"

class Prefs: pass
prefs = Prefs()
prefs.max_str_len = 20         # how many chars before we abbreviate with ...?
prefs.max_horiz_array_len = 40 # how many chars before it's too wide and we go vertical?
prefs.max_list_elems = 10      # how many elements max to display in list (unused so far)
prefs.float_precision = 5      # how many decimal places to show for floats

class WrapAssoc:
    def __init__(self,assoc):
        self.assoc = assoc
    def __repr__(self):
        return elviz(self.assoc,showassoc=True)


class Ellipsis:
    def __repr__(self):
        return '...'


def strviz(astring):
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [shape=box, penwidth="0.5"];
    """

    s += string_node(astring)

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

    newelems = []
    for e in elems:
        if showassoc and type(e) == tuple and len(e) == 2:
            newelems.append(WrapAssoc(e))
        else:
            newelems.append(e)

    s += gr_list_node('node%d'%id(elems), newelems)

    s += "}\n"
    return graphviz.Source(s)


def treeviz(root, leftfield='left', rightfield='right'):
    """
    Display a top-down visualization of a binary tree that has
    two fields pointing at the left and right subtrees. The
    type of each node is displayed, all fields, and then
    left/right pointers at the bottom.
    """
    if root is None:
        return

    s = """
    digraph G {
        nodesep=.1;
        ranksep=.3;
        rankdir=TD;
        node [penwidth="0.5", shape=box, width=.1, height=.1];

    """

    reachable = closure(root)

    for p in reachable:
        nodename = "node%d" % id(p)
        fields = []
        if hasattr(p,leftfield) or hasattr(p,rightfield):
            for k, v in p.__dict__.items():
                if k==leftfield or k==rightfield:
                    continue
                if isatom(v):
                    fields.append((k, k, v))
                else:
                    fields.append((k, k, None))
            s += '// %s TREE node with fields\n' % p.__class__.__name__
            s += gr_vtree_node(p.__class__.__name__, nodename, fields, separator=None)
        else:
            s += obj_node(p)

    # s += obj_nodes(reachable)
    s += obj_edges(reachable)

    s += "}\n"
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
        ranksep=.4;
        rankdir=LR;
        node [penwidth="0.5", shape=box, width=.1, height=.1];

    """
    sublists = table

    nodename = "node%d" % id(table)
    s += gr_vlol_node(nodename, table) # add vlist

    for sublist in sublists:
        nodename = "node%d" % id(sublist)
        s += gr_list_node(nodename, sublist)

    i = 0
    for sublist in sublists:
        s += 'node%d:%s -> node%d:w [arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4, weight=100]\n' % (id(table), str(i), id(sublist))
        i += 1

    s += "}\n"
    return graphviz.Source(s)


def ndarrayviz(data):
    return None


def callviz(frame=None, varnames=None):
    """
    Visualize one call stack frame. If frame is None, viz
    caller of callviz()'s frame. Restrict to varnames if
    not None.
    """
    if frame is None:
        stack = inspect.stack()
        frame = stack[1][0]

    return callsviz([frame], varnames)


def callsviz(callstack=None, varnames=None):
    s = """
    digraph G {
        nodesep=.1;
        ranksep=.1;
        rankdir=LR;
        node [penwidth="0.5", shape=box, width=.1, height=.1];

    """

    # Get stack frame nodes so we can stack 'em up
    if callstack is None:
        stack = inspect.stack()
        callstack = []
        for i,st in enumerate(stack[1:]):
            frame = st[0]
            name = st[3]
            callstack.append(frame)
            if name=='<module>':
                break

    # Draw all stack frame nodes together so we can use rank=same
    s += "\n{ rank=same;\n"
    callstack = list(reversed(callstack))
    for f in callstack:
        s += obj_node(f, varnames)

    for i in range(len(callstack)-1):
        this = callstack[i]
        callee = callstack[i+1]
        s += 'node%d -> node%d [style=invis, weight=100]\n' % (id(this), id(callee))
    s += "}\n\n"

    # find all reachable objects from call stack
    reachable = []
    for f in callstack:
        cl = closure(f, varnames)
        reachable.extend(cl)
    reachable = uniq(reachable)

    s += obj_nodes(reachable)
    s += obj_edges(reachable)
    s += obj_edges(callstack, varnames)
    s += "}\n"

    return graphviz.Source(s)


def ignoresym(sym):
    return sym[0].startswith('_') or\
           callable(sym[1]) or\
           isinstance(sym[1], types.ModuleType)


def objviz(o, orientation="LR"):
    """Draw an arbitrary object graph."""
    s = """
digraph G {
    nodesep=.1;
    ranksep=.3;
    rankdir=%s;
    node [penwidth="0.5", shape=box, width=.1, height=.1];
    
""" % orientation

    if type(o).__module__ == 'numpy': # avoid requiring numpy package unless used
        if type(o).__name__ == 'ndarray':
            return matrixviz(o)
    if not viz_exists_for_object(o) and hasattr(o, "__iter__"):
        o = list(o)

    reachable = closure(o)

    s += obj_nodes(reachable)
    s += obj_edges(reachable)
    s += "}\n"
    return graphviz.Source(s)


def obj_nodes(nodes):
    s = ""

    # organize nodes by connected_subgraphs so we can cluster
    # currently only making subgraph cluster for linked lists
    # otherwise it squishes trees.
    max_edges_for_type,subgraphs = connected_subgraphs(nodes)
    c = 1
    for g in subgraphs:
        firstelement = g[0]
        if max_edges_for_type[firstelement.__class__]==1: # linked list
            s += 'subgraph cluster%d {style=invis penwidth=.7 pencolor="%s"\n' % (c,GREEN)
            for p in g:
                s += obj_node(p)
            s += "\n}\n"
            c += 1
        elif max_edges_for_type[firstelement.__class__]==2: # binary tree
            for p in g:
                s += obj_node(p) # nothing special for now

    # now dump disconnected nodes
    for p in nodes:
        found = False
        for g in subgraphs:
            if p in g:
                found = True
                break
        if not found:
            s += obj_node(p)

    return s


def obj_node(p, varnames=None):
    s = ""
    nodename = "node%d" % id(p)
    if type(p) == types.FrameType:
        frame = p
        info = inspect.getframeinfo(frame)
        caller_scopename = info[2]
        if caller_scopename == '<module>':
            caller_scopename = 'globals'
        argnames, _, _ = inspect.getargs(frame.f_code)
        items = []
        # do args first to get proper order
        for arg in argnames:
            if varnames is not None and arg not in varnames: continue
            v = frame.f_locals[arg]
            if isatom(v):
                items.append((arg, arg, v))
            else:
                items.append((arg, arg, None))
        for k, v in frame.f_locals.items():
            if varnames is not None and k not in varnames: continue
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
    elif isinstance(p,dict):
        # print "DRAW DICT", p, '@ node' + nodename
        items = []
        i = 0
        for k, v in p.items():
            if varnames is not None and k not in varnames: continue
            if isatom(v):
                items.append((str(i), k, v))
            else:
                items.append((str(i), k, None))
            i += 1
        s += '// DICT\n'
        s += gr_dict_node(nodename, None, items)
    elif isinstance(p,set) and len(p) == 0:  # special case "empty set"
        s += 'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">empty set</font>>];\n' % id(p)
    elif p is True or p is False:  # Boolean
        s += 'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">%s</font>>];\n' % (id(p), str(p))
    elif type(p).__module__ == 'numpy' and type(p).__name__ == 'ndarray':
        s += gr_ndarray_node('node%d' % id(p), p)
    elif type(p).__module__ == 'pandas.core.series' and type(p).__name__ == 'Series':
        s += gr_ndarray_node('node%d' % id(p), p.values)
    elif type(p).__module__ == 'pandas.core.frame' and type(p).__name__ == 'DataFrame':
        s += gr_ndarray_node('node%d' % id(p), p.values)
    elif isinstance(p,list) and len(p)==0: # special case "empty list"
        s += 'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">empty list</font>>];\n' % id(p)
    elif hasattr(p, "__iter__") and isatomlist(p) or type(p)==tuple:
        # print "DRAW LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        if isinstance(p,set):
            s += '// SET of atoms\n'
            s += gr_set_node(nodename, elems)
        else:
            s += '// LIST or ITERATABLE of atoms\n'
            s += gr_list_node(nodename, elems)
    elif hasattr(p, "__iter__"):
        # print "DRAW VERTICAL LIST", p, '@ node' + nodename
        elems = []
        for el in p:
            if isatom(el):
                elems.append(el)
            else:
                elems.append(None)
        s += '// VERTICAL LIST or ITERATABLE\n'
        if isinstance(p,set):
            s += gr_vlol_node(nodename, elems, title='set', showindexes=False)
        else:
            s += gr_vlol_node(nodename, elems)

    elif hasattr(p, "__dict__"): # generic object
        # print "DRAW OBJ", p, '@ node' + nodename
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
        s += 'node%d [margin="0.03", shape=none label=<<font face="Times-Italic" color="#444443" point-size="9">%s</font>>];\n' % (id(p),abbrev_and_escape("<%s:%s>" % (type(p).__name__,repr(p))))

    return s


def obj_edges(nodes, varnames=None):
    s = ""
    es = edges(nodes, varnames)
    for (p, label, q) in es:
        if type(p) != types.FrameType and type(p) != dict and type(p) != tuple and hasattr(p,"__iter__") and not isatomlist(p):  # edges start at right edge not center for vertical lists
            s += 'node%d:%s -> node%d:w [arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4, weight=100]\n' % (id(p), label, id(q))
        else:
            s += 'node%d:%s:c -> node%d [dir=both, tailclip=false, arrowtail=dot, penwidth="0.5", color="#444443", arrowsize=.4]\n' % (id(p), label, id(q))

    return s


def elviz(el, showassoc):
    if el is None:
        els = ' '
    elif showassoc and type(el) == tuple and len(el) == 2:
        els = "%s&rarr;%s" % (elviz(el[0], showassoc), elviz(el[1], False))
    elif type(el)==set:
        els = '{'+', '.join([elviz(e, showassoc) for e in el])+'}'
    elif type(el) == dict:
        els = '{' + ','.join([elviz(e, showassoc) for e in el.items()]) + '}'
    elif isinstance(el,float):
        els = str(round(el,prefs.float_precision))
    else:
        els = repr(el)
    els = els.replace('{', '&#123;')
    els = els.replace('}', '&#125;')
    els = els.replace('<', '&lt;')
    els = els.replace('>', '&gt;')
    return els


def gr_list_node(nodename, elems, bgcolor=YELLOW):
    shape="box"
    if len(elems)>0:
        abbrev_values = abbrev_and_escape_values(elems) # compute just to see eventual size
        if len(''.join(abbrev_values))>prefs.max_horiz_array_len:
            html = gr_vlist_html(elems, bgcolor=bgcolor)
        else:
            html = gr_listtable_html(elems, bgcolor=bgcolor)
    else:
        shape = "none"
        html = '<font face="Times-Italic" color="#444443" point-size="9">empty list</font>'
    return '%s [shape="%s", space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (nodename,shape,html)


def gr_listtable_html(values, title=None, bgcolor=YELLOW, showindexes=True):
    header = '<table BORDER="0" CELLBORDER="0" CELLSPACING="0">\n'
    tail = "</table>\n"

    N = len(values)
    index_html = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%s</font></td>\n'
    value_html = '<td port="%s" bgcolor="%s" border="1" sides="r" align="center"><font point-size="11">%s</font></td>\n'
    # don't want right border to show on last.
    last_index_html = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    last_value_html = '<td port="%s" bgcolor="%s" border="0" align="center"><font point-size="11">%s</font></td>\n'

    oversize = False
    if N > prefs.max_list_elems:
        values = values[0:prefs.max_list_elems-1] + [values[N - 1]]
        oversize = True

    newvalues = []
    for value in values:
        if value is not None:
            if len(str(value)) > prefs.max_str_len:
                value = abbrev_and_escape(str(value))
            v = repr(value)
        else:
            v = "  "
        newvalues.append(v)
    values = newvalues

    lastindex = len(values) - 1
    toprow = [index_html % (bgcolor,i) for i in range(lastindex)]
    bottomrow = [value_html % (i,bgcolor,values[i]) for i in range(lastindex)]

    if oversize:
        toprow.append(index_html % (bgcolor,'...'))
        bottomrow.append(value_html % ('',bgcolor,'...'))

    if len(values)>=1:
        toprow.append(last_index_html % (bgcolor,N-1))
        bottomrow.append(last_value_html % (N-1, bgcolor,values[lastindex]))

    if title is not None:
        titlerow = '<tr><td cellspacing="0" colspan="%d" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (N, bgcolor, title)
    else:
        titlerow = ''

    if showindexes:
        return header + titlerow + '<tr>\n'+''.join(toprow)+'</tr>\n' + '<tr>\n'+''.join(bottomrow)+'</tr>' + tail
    else:
        return header + titlerow + '<tr>\n'+''.join(bottomrow)+'</tr>' + tail


def gr_set_node(nodename, elems, bgcolor=YELLOW):
    shape="box"
    if len(elems)>0:
        abbrev_values = abbrev_and_escape_values(elems) # compute just to see eventual size
        if len(''.join(abbrev_values))>prefs.max_horiz_array_len:
            html = gr_vlist_html(elems, title='set', bgcolor=bgcolor, showindexes=False, showelems=True)
        else:
            html = gr_listtable_html(elems, title='set', bgcolor=bgcolor, showindexes=False)
    else:
        shape = "none"
        html = '<font face="Times-Italic" color="#444443" point-size="9">empty list</font>'
    return '%s [shape="%s", space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (nodename,shape,html)


def gr_dict_node(nodename, title, items, highlight=None, bgcolor=YELLOW, separator="&rarr;", reprkey=True):
    html = gr_dict_html(title, items, highlight, bgcolor, separator, reprkey)
    return '%s [margin="0.03", color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (nodename,bgcolor,html)


def gr_dict_html(title, items, highlight=None, bgcolor=YELLOW, separator="&rarr;", reprkey=True):
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'

    blankrow = '<tr><td colspan="3" cellpadding="1" border="0" bgcolor="%s"></td></tr>' % (bgcolor)
    rows = []
    if title is not None:
        title = '<tr><td cellspacing="0" colspan="3" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (bgcolor, title)
        rows.append(title)

    ptrs = []
    atoms = []
    for it in items:
        if isatom(it[2]):
            atoms.append(it)
        else:
            ptrs.append(it)

    if len(items)>0:
        for label,key,value in atoms + ptrs: # do atoms first then ptrs
            font = "Helvetica"
            if highlight is not None and key in highlight:
                font = "Times-Italic"
            if separator is not None:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="0" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (label, bgcolor, font, repr(key) if reprkey else key)
                sep = '<td cellpadding="0" border="0" valign="bottom"><font color="#444443" point-size="9">%s</font></td>' % separator
            else:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (label, bgcolor, font, repr(key) if reprkey else key)
                sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

            if value is not None:
                if len(str(value)) > prefs.max_str_len:
                    value = abbrev_and_escape(str(value))
                v = repr(value)
            else:
                v = "   "
            value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n' % (label, bgcolor, v)
            row = '<tr>' + name + sep + value + '</tr>\n'
            rows.append(row)
    else:
        rows.append('<tr><td cellspacing="0" cellpadding="0" border="0"><font point-size="9"> ... </font></td></tr>\n')

    tail = "</table>\n"
    return header + blankrow.join(rows) + tail


def gr_vlol_node(nodename, elems, title=None, bgcolor=GREEN, showindexes=True, showelems=False):
    html = gr_vlol_html(elems, title, bgcolor=bgcolor, showindexes=showindexes, showelems=showelems)
    return '%s [color="#444443", margin="0.02", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (nodename,bgcolor,html)


def gr_vlol_html(elems, title=None, bgcolor=GREEN, showindexes=True, showelems=False):
    if len(elems)==0:
        return " "
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">\n'
    tail = "</table>\n"

    rows = []
    if title is not None:
        titlerow = '<tr><td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (bgcolor, title)
        rows.append(titlerow)

    for i,el in enumerate(elems):
        if showindexes:
            v = str(i)
        else:
            v = ' '
        if showelems:
            if el is None:
                v = ' '
            else:
                v = repr(el)
        if i==len(elems)-1:
            value = '<td port="%d" BORDER="0" cellpadding="3" cellspacing="0" bgcolor="%s" align="left"><font color="#444443" point-size="9">%s</font></td>\n' % (i, bgcolor, v)
        else:
            value = '<td port="%d" BORDER="1" cellpadding="2" cellspacing="0" sides="b" bgcolor="%s" align="left"><font color="#444443" point-size="9">%s</font></td>\n' % (i, bgcolor, v)
        row = '<tr>' + value + '</tr>\n'
        rows.append(row)

    return header + ''.join(rows) + tail


def gr_vlist_html(elems, title=None, bgcolor=YELLOW, showindexes=True, showelems=True):
    if len(elems)==0:
        return " "
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'
    tail = "</table>\n"
    blankrow = '<tr><td colspan="3" cellpadding="1" border="0" bgcolor="%s"></td></tr>' % (bgcolor)
    sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

    rows = []
    if title is not None:
        title = '<tr><td cellspacing="0" colspan="3" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (bgcolor, title)
        rows.append(title)

    N = len(elems)
    if N > prefs.max_list_elems:
        items = [(i,elems[i]) for i in range(prefs.max_list_elems-1)] + [(Ellipsis(),Ellipsis()),(N-1,elems[N - 1])]
    else:
        items = [(i,elems[i]) for i in range(N)]

    if len(items)>0:
        for i,e in items:
            index = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="Helvetica" color="#444443" point-size="11">%s </font></td>\n' % (bgcolor, i)

            if isatom(e) or isinstance(e, tuple):
                if len(str(e)) > prefs.max_str_len:
                    e = abbrev_and_escape(str(e))
                v = repr(e)
            else:
                v = '&lt;' + e.__class__.__name__ + '&gt;'
            value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="center"><font color="#444443" point-size="11"> %s</font></td>\n' % (i, bgcolor, v)
            if showindexes:
                row = '<tr>' + index + sep + value + '</tr>\n'
            else:
                row = '<tr>' + value + '</tr>\n'
            rows.append(row)
    else:
        rows.append('<tr><td cellspacing="0" cellpadding="0" border="0"><font point-size="9"> ... </font></td></tr>\n')

    return header + blankrow.join(rows) + tail


def gr_vtree_node(title, nodename, items, bgcolor=YELLOW, separator=None, leftfield='left', rightfield='right'):
    html = gr_vtree_html(title, items, bgcolor, separator)
    return '%s [margin="0.03", color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (nodename,bgcolor,html)


def gr_vtree_html(title, items, bgcolor=YELLOW, separator=None, leftfield='left', rightfield='right'):
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'

    rows = []
    blankrow = '<tr><td colspan="3" cellpadding="1" border="0" bgcolor="%s"></td></tr>' % (bgcolor)

    if title is not None:
        title = '<tr><td cellspacing="0" colspan="3" cellpadding="0" bgcolor="%s" border="1" sides="b" align="center"><font color="#444443" FACE="Times-Italic" point-size="11">%s</font></td></tr>\n' % (bgcolor, title)
        rows.append(title)

    if len(items)>0:
        for label,key,value in items:
            font = "Helvetica"
            if separator is not None:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="0" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (label, bgcolor, font, key)
                sep = '<td cellpadding="0" border="0" valign="bottom"><font color="#444443" point-size="9">%s</font></td>' % separator
            else:
                name = '<td port="%s_label" cellspacing="0" cellpadding="0" bgcolor="%s" border="1" sides="r" align="right"><font face="%s" color="#444443" point-size="11">%s </font></td>\n' % (label, bgcolor, font, key)
                sep = '<td cellspacing="0" cellpadding="0" border="0"></td>'

            if value is not None:
                v = abbrev_and_escape(str(value))
                v = repr(v)
            else:
                v = "   "
            value = '<td port="%s" cellspacing="0" cellpadding="1" bgcolor="%s" border="0" align="left"><font color="#444443" point-size="11"> %s</font></td>\n' % (label, bgcolor, v)
            row = '<tr>' + name + sep + value + '</tr>\n'
            rows.append(row)
    else:
        rows.append('<tr><td cellspacing="0" cellpadding="0" border="0"><font point-size="9"> ... </font></td></tr>\n')

    if separator is not None:
        sep = '<td cellpadding="0" bgcolor="%s" border="0" valign="bottom"><font color="#444443" point-size="15">%s</font></td>' % (bgcolor,separator)
    else:
        sep = '<td cellspacing="0" cellpadding="0" bgcolor="%s" border="0"></td>' % bgcolor

    kidsep = """
    <tr><td colspan="3" cellpadding="0" border="1" sides="b" height="3"></td></tr>
    """ + blankrow

    kidnames = """
    <tr>
    <td cellspacing="0" cellpadding="0" bgcolor="$bgcolor$" border="1" sides="r" align="left"><font color="#444443" point-size="6">%s</font></td>
    %s
    <td cellspacing="0" cellpadding="1" bgcolor="$bgcolor$" border="0" align="right"><font color="#444443" point-size="6">%s</font></td>
    </tr>
    """ % (leftfield, sep, rightfield)

    kidptrs = """
    <tr>
    <td port="%s" cellspacing="0" cellpadding="0" bgcolor="$bgcolor$" border="1" sides="r"><font color="#444443" point-size="1"> </font></td>
    %s
    <td port="%s" cellspacing="0" cellpadding="0" bgcolor="$bgcolor$" border="0"><font color="#444443" point-size="1"> </font></td>
    </tr>
    """ % (leftfield, sep, rightfield)

    bottomsep = """
    <tr>
    <td cellspacing="0" cellpadding="0" bgcolor="$bgcolor$" border="1" sides="r"><font color="#444443" point-size="3"> </font></td>
    %s
    <td cellspacing="0" cellpadding="0" bgcolor="$bgcolor$" border="0"><font color="#444443" point-size="3"> </font></td>
    </tr>
    """ % sep

    kidsep = kidsep.replace('$bgcolor$', bgcolor)
    kidnames = kidnames.replace('$bgcolor$', bgcolor)
    kidptrs = kidptrs.replace('$bgcolor$', bgcolor)
    bottomsep = bottomsep.replace('$bgcolor$', bgcolor)

    tail = "</table>\n"
    return header + blankrow.join(rows) + kidsep + kidnames + kidptrs + bottomsep + tail


def string_node(s):
    html = string_html(s)
    return '    node%d [width=0,height=0, color="#444443", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="%s", label=<%s>];\n' % (id(s),YELLOW,html)


def string_html(s):
    values = list(s)
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="0" CELLSPACING="0">\n'

    index_html = '<td cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="1" sides="br" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    value_html = '<td port="%d" cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="0" align="center"><font face="Monaco" point-size="11">%s</font></td>\n'
    # don't want right border to show on last.
    last_index_html = '<td cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>\n'
    last_value_html = '<td port="%d" cellspacing="0" cellpadding="0" bgcolor="#FBFEB0" border="0" align="center"><font face="Monaco" point-size="11">%s</font></td>\n'

    lastindex = len(values) - 1
    toprow = [index_html % i for i in range(lastindex)]
    bottomrow = [value_html % (i,values[i]) for i in range(lastindex)]

    toprow.append(last_index_html % lastindex)
    bottomrow.append(last_value_html % (lastindex, values[lastindex]))

    tail = "</table>\n"
    return header + '<tr><td></td>\n'+''.join(toprow)+'<td></td></tr>\n' + '<tr><td>\'</td>\n'+''.join(bottomrow)+'<td>\'</td></tr>' + tail


def gr_1darray_html(data, bgcolor=YELLOW):
    if 'numpy' not in sys.modules:
        import numpy
    np = sys.modules['numpy']
    if not isinstance(data,np.ndarray):
        return " "
    if data.ndim > 1:
        return gr_1darray_html(data, bgcolor)
    if data.ndim > 2:
        return " "

    ncols = len(data)
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'
    tail = "</table>\n"

    # grab slice of max elements from matrix
    coloversize = False
    midpoint = prefs.max_list_elems//2
    if ncols > prefs.max_list_elems:
        colslice = list(np.arange(0,midpoint)) + list(np.arange(ncols-midpoint,ncols))
        data = data[colslice]
        ncols=len(colslice)
        coloversize = True

    cells = []
    for j in range(ncols):
        if coloversize and j==midpoint:
            cells.append( '<td cellspacing="0" cellpadding="2" bgcolor="%s" border="0" align="center"><font color="#444443" point-size="10">...</font></td>\n' % bgcolor)
        value = data[j]
        if isinstance(value, float):
            if str(value).endswith('.0'):
                value = str(value)[:-1]
            else:
                value = round(value, prefs.float_precision)
        if isinstance(value, float) and str(value).endswith('.0'):
            value = str(value)[:-1]
        if len(str(value)) > prefs.max_str_len:
            value = abbrev_and_escape(str(value))
        cell = '<td cellspacing="0" cellpadding="3" bgcolor="%s" border="0" align="center"><font color="#444443" point-size="10">%s</font></td>\n' % (bgcolor, value)
        cells.append( cell )

    row = '<tr>' + ''.join(cells) + '</tr>\n'

    return header + row + tail


def gr_2darray_html(data, bgcolor=YELLOW):
    if 'numpy' not in sys.modules:
        import numpy
    np = sys.modules['numpy']
    if len(data)==0:
        return " "
    if not isinstance(data,np.ndarray):
        return " "
    if data.ndim == 1:
        return gr_1darray_html(data, bgcolor)
    if data.ndim > 2:
        return " "

    nrows,ncols = data.shape
    header = '<table BORDER="0" CELLPADDING="0" CELLBORDER="1" CELLSPACING="0">\n'
    tail = "</table>\n"

    # grab slice of max elements from matrix
    coloversize = rowoversize = False
    midpoint = prefs.max_list_elems//2
    if nrows > prefs.max_list_elems:
        rowslice = list(np.arange(0,midpoint)) + list(np.arange(nrows-midpoint,nrows))
        data = data[rowslice]
        nrows=len(rowslice)
        rowoversize = True
    if ncols > prefs.max_list_elems:
        colslice = list(np.arange(0,midpoint)) + list(np.arange(ncols-midpoint,ncols))
        data = data[:,colslice]
        ncols=len(colslice)
        coloversize = True

    rows = []
    for i in range(nrows):
        if rowoversize and i==midpoint:
            rows.append( '<tr><td bgcolor="%s" cellpadding="2" border="0" align="center"><font color="#444443" point-size="10">&#8942;</font></td><td bgcolor="%s" cellpadding="2" border="0" colspan="%d"></td></tr>\n' % (bgcolor,bgcolor,ncols))
        cells = []
        for j in range(ncols):
            if coloversize and j==midpoint:
                cells.append( '<td cellspacing="0" cellpadding="2" bgcolor="%s" border="0" align="center"><font color="#444443" point-size="10">...</font></td>\n' % bgcolor)
            value = data[i,j]
            if isinstance(value, float):
                if str(value).endswith('.0'):
                    value = str(value)[:-1]
                else:
                    value = round(value, prefs.float_precision)
            if len(str(value)) > prefs.max_str_len:
                value = abbrev_and_escape(str(value))
            cell = '<td cellspacing="0" cellpadding="3" bgcolor="%s" border="0" align="center"><font color="#444443" point-size="10">%s</font></td>\n' % (bgcolor, value)
            cells.append( cell )
        row = '<tr>' + ''.join(cells) + '</tr>\n'
        rows.append(row)

    return header + ''.join(rows) + tail


def gr_ndarray_node(nodename, data, bgcolor=YELLOW):
    shape="box"
    html = gr_2darray_html(data, bgcolor=bgcolor)
    return '%s [shape="%s", space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<%s>];\n' % (nodename,shape,html)


def matrixviz(data):
    s = """
    digraph G {
        nodesep=.05;
        node [penwidth="0.5", width=.1,height=.1];
    """

    s += gr_ndarray_node('node%d'%id(data), data)

    s += "}\n"
    return graphviz.Source(s)


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
    if len(elems)==0: # empty lists are not atom lists
        return False
    for x in elems:
        if not isatom(x):
            return False
    return True


def isatom(p):
    if (sys.version_info > (3, 0)):
        return isatom_(p)
    else:
        return isatom_(p) or type(p) == unicode # only python 2 distinguishes between str/unicode


def isatom_(p): return type(p) == int or type(p) == float or \
                       type(p) == str or \
                       p.__class__ == WrapAssoc or \
                       p.__class__ == Ellipsis


def isplainobj(p): return type(p) != types.FrameType and \
                          type(p) != dict and \
                          not hasattr(p,"__iter__") and \
                          hasattr(p, "__dict__")


def closure(p, varnames=None):
    """
    Find all nodes reachable from p and return a list of pointers to those reachable.
    There can't be duplicates even for cyclic graphs due to visited set. Chase ptrs
    from but don't include frame objects.
    """
    return closure_(p, varnames, set())


def closure_(p, varnames, visited):
    if p is None or isatom(p):
        return []
    if id(p) in visited:
        return []
    visited.add(id(p))
    result = []
    if type(p) != types.FrameType:
        result.append(p)

    # now chase where we can reach
    if type(p) == types.FrameType:
        frame = p
        info = inspect.getframeinfo(frame)
        for k, v in frame.f_locals.items():
            # error('INCLUDE frame var %s' % k)
            if varnames is not None and k not in varnames: continue
            if not ignoresym((k, v)):
                cl = closure_(v, varnames, visited)
                result.extend(cl)
        caller_scopename = info[2]
        if caller_scopename != '<module>': # stop at globals
            cl = closure_(p.f_back, varnames, visited)
            result.extend(cl)
    elif type(p).__module__ == 'numpy' and type(p).__name__ == 'ndarray':
        pass # ndarray added already above; don't chase its elements here
    elif type(p).__module__ == 'pandas.core.series' and type(p).__name__ == 'Series':
        pass  # pd.Series added already above; don't chase its elements here
    elif type(p).__module__ == 'pandas.core.frame' and type(p).__name__ == 'DataFrame':
        pass
    elif type(p)==dict:
        for k,q in p.items():
            cl = closure_(q, varnames, visited)
            result.extend(cl)
    elif hasattr(p, "__dict__"): # regular object like Tree or Node
        for k,q in p.__dict__.items():
            cl = closure_(q, varnames, visited)
            result.extend(cl)
    elif hasattr(p, "__iter__"): # a list or similar
        for q in p:
            cl = closure_(q, varnames, visited)
            result.extend(cl)
    return result


def edges(reachable, varnames=None):
    """Return list of (p, port-in-p, q) for all p in reachable node list"""
    edges = []
    for p in reachable:
        edges.extend( node_edges(p, varnames) )
    return edges


def node_edges(p, varnames=None):
    """Return list of (p, fieldname-in-p, q) for all ptrs in p"""
    edges = []
    if type(p) == types.FrameType:
        frame = p
        for k, v in frame.f_locals.items():
            if varnames is not None and k not in varnames: continue
            if not ignoresym((k, v)) and not isatom(v) and v is not None:
                edges.append((frame, k, v))
    elif type(p) == dict:
        i = 0
        for k, v in p.items():
            if not isatom(v) and v is not None:
                edges.append((p, str(i), v))
            i += 1
    elif type(p).__module__ == 'numpy' and type(p).__name__ == 'ndarray':
        pass # don't chase elements
    elif hasattr(p, "__iter__"):
        for i, el in enumerate(p):
            if not isatom(el) and el is not None:
                edges.append((p, str(i), el))
    elif hasattr(p, "__dict__"):
        for k, v in p.__dict__.items():
            if not isatom(v) and v is not None:
                edges.append((p, k, v))
    return edges


def viz_exists_for_object(p):
    if type(p) == types.FrameType: return True
    if isinstance(p,dict): return True
    elif isinstance(p,set) and len(p) == 0: return True
    elif p is True or p is False: return True
    elif type(p).__module__ == 'numpy' and type(p).__name__ == 'ndarray': return True
    elif type(p).__module__ == 'pandas.core.series' and type(p).__name__ == 'Series': return True
    elif type(p).__module__ == 'pandas.core.frame' and type(p).__name__ == 'DataFrame': return True
    return False


def connected_subgraphs(reachable, varnames=None):
    """
    Find all connected subgraphs of same type and same fieldname. Return a list
    of sets containing the id()s of all nodes in a specific subgraph
    """
    max_edges_for_type = max_edges_in_connected_subgraphs(reachable, varnames)

    reachable = closure(reachable, varnames)
    reachable = [p for p in reachable if isplainobj(p)]
    subgraphs = [] # list of sets of obj id()s
    subgraphobjs = [] # list of sets of obj ptrs (parallel list to track objs since can't hash on some objs like lists/sets as keys)
    type_fieldname_map = {}
    for p in reachable:
        edges = node_edges(p, varnames)
        for e in edges:
            fieldname = e[1]
            q = e[2]
            if type(p) == type(q):
                # ensure that singly-linked nodes use same field
                cname = p.__class__.__name__
                if max_edges_for_type[p.__class__]==1 and cname in type_fieldname_map:
                    prev_fieldname = type_fieldname_map[cname]
                    if fieldname!=prev_fieldname:
                        continue
                else:
                    type_fieldname_map[cname] = fieldname
                # search for an existing subgraph
                found = False
                for i in range(len(subgraphs)):
                    g = subgraphs[i]
                    go = subgraphobjs[i]
                    if id(p) in g or id(q) in g:
                        found = True
                        g.update({id(p), id(q)})
                        go.extend([p, q])
                if not found:
                    subgraphs.append({id(p),id(q)})
                    subgraphobjs.append([p, q])

    uniq = []
    for g in subgraphobjs:
        uniq.append( list(set(g)) )

    return max_edges_for_type,uniq


def max_edges_in_connected_subgraphs(reachable, varnames=None):
    """
    Return mapping from node class obj to max num edges connecting
    nodes of that same type. Ignores all but isplainobj() nodes.
    Ignores any node type w/o at least one edge connecting to same type.

    The keys indicate the set of types (class def objects)
    that are involved in connected subgraphs.

    Max == 1 indicates possible linked list
    whereas max == 2 indicates possible binary tree.
    """
    max_edges_for_type = defaultdict(int)
    reachable = closure(reachable, varnames)
    reachable = [p for p in reachable if isplainobj(p)]
    for p in reachable:
        homo_edges = edges_to_same_type(p, varnames)
        m = len(homo_edges)
        if m>0:
            max_edges_for_type[p.__class__] = max(max_edges_for_type[p.__class__], m)

    return max_edges_for_type


def edges_to_same_type(p, varnames):
    homo_edges = []
    edges = node_edges(p, varnames)
    for e in edges:
        q = e[2]
        if type(p) == type(q):
            homo_edges.append(e)
            #print("CONNECTED", p, q, 'via', fieldname)
    return homo_edges


def abbrev_and_escape_values(elems):
    abbrev_values = []
    for v in elems:
        if v is not None:
            abbrev_values.append(abbrev_and_escape(str(v)))
        else:
            abbrev_values.append('  ')
    return abbrev_values


def abbrev_and_escape(s):
    if s is None:
        return s
    if len(s) > prefs.max_str_len:
        s = s[:prefs.max_str_len] + "..."
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s


def uniq(elems):
    seen = set()
    u = []
    for e in elems:
        if id(e) not in seen:
            seen.add(id(e))
            u.append(e)
    return u


def error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
