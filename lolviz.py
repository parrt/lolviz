"""
A small set of functions that display lists, dictionaries,
and lists of lists in a reasonable manner using graphviz.
Inspired by the object connectivity graphs in Pythontutor.com
"""
import graphviz

def dictviz(d):
    """
    Display a dictionary with the key/value pairs in a vertical list
    """
    s = """
    digraph G {
        nodesep=.05;
        rankdir=LR;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """
    labels = []
    for key,value in d.items():
        labels.append("%s&rarr;%s" % (repr(key),elviz(value,True)))
    s += '    mainlist [color="#444443", fontsize="9", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#FBFEB0", label = "'+'|'.join(labels)+'"];\n'
    s += '}\n'
    return graphviz.Source(s)


def listviz(elems, showassoc=True):
    s = """
    digraph G {
        nodesep=.05;
        node [penwidth="0.5", shape=record,width=.1,height=.1];
    """
    if type(elems)==dict:
        return dictviz(elems)

    labels = []
    for i in range(len(elems)):
        el = elems[i]
        if not el:
            labels.append(str(i))
        else:
            labels.append(idx_elviz(i,el,showassoc))
    s += '    mainlist [space="0.0", margin="0.01", fontcolor="#444443", fontname="Helvetica", label=<'+'|'.join(labels)+'>];\n'

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
        # if (type(bucket)==list or type(bucket)==tuple) and len(bucket) == 0:
        #     labels.append(str(i))
        # else:
        #     labels.append("<f%d> %d" % (i, i))
        labels.append("<f%d> %d" % (i, i))

    s += '    mainlist [color="#444443", fontsize="9", fontcolor="#444443", fontname="Helvetica", style=filled, fillcolor="#D9E6F5", label = "'+'|'.join(labels)+'"];\n'

    # define inner lists
    for i in range(len(table)):
        bucket = table[i]
        if bucket==None:
            continue
        elements = []
        if (type(bucket)==list or type(bucket)==tuple) and len(bucket) == 0:
            s += 'node%d [margin="0.03", fontname="Italics", shape=none label=<<font color="#444443" point-size="9">empty list</font>>];\n' % i
        else:
            if type(bucket)==list or type(bucket)==tuple:
                if len(bucket)>0:
                    for j, el in enumerate(bucket):
                        elements.append(idx_elviz(j, el, showassoc))
            else:
                elements.append(elviz(bucket, showassoc))
            s += 'node%d [color="#444443", fontname="Helvetica", margin="0.01", space="0.0", shape=record label=<{%s}>];\n' % (i, '|'.join(elements))

    # Do edges
    for i in range(len(table)):
        bucket = table[i]
        if bucket==None:
            continue
        # if not bucket or ((type(bucket)==list or type(bucket)==tuple) and len(bucket)==0):
        #     continue
        s += 'mainlist:f%d -> node%d [penwidth="0.5", color="#444443", arrowsize=.4]\n' % (i,i)
    s += "}\n"
    # print s
    return graphviz.Source(s)


def elviz(el, showassoc):
    if showassoc and type(el) == tuple and len(el) == 2:
        els = "%s&rarr;%s" % (elviz(el[0], showassoc), elviz(el[1], showassoc))
    elif type(el)==set:
        els = '{'+', '.join([elviz(e, showassoc) for e in el])+'}'
    elif type(el) == dict:
        els = '{' + ','.join([elviz(e, showassoc) for e in el.items()]) + '}'
    else:
        els = repr(el)
    els = els.replace('{', '&#123;')
    els = els.replace('}', '&#125;')
    return els


def idx_elviz(idx, el, showassoc):
    return \
        """
        <table BORDER="0" CELLBORDER="1" CELLSPACING="0">
          <tr>
            <td cellspacing="0" bgcolor="#FBFEB0" border="1" sides="b" valign="top"><font color="#444443" point-size="9">%d</font></td>
          </tr>
          <tr>
            <td bgcolor="#FBFEB0" border="0" align="center"><font point-size="11">%s</font></td>
          </tr>
        </table>
        """ % (idx, elviz(el,showassoc))
