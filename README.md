# lolviz

A simple Python data-structure visualization tool for lists of lists, lists, dictionaries; primarily for use in Jupyter notebooks / presentations. It seems that I'm always trying to describe how data is laid out in memory to students. There are really great data structure visualization tools but I wanted something I could use directly via Python in Jupyter notebooks. The look and idea was inspired by the awesome [Python tutor](http://www.pythontutor.com).

There are currently three functions of interest that return `graphviz.files.Source` objects:

* `dictviz()`: A dictionary visualization<br><img src=images/dict.png width=50>
* `listviz()`: Horizontal list visualization<br><img src=images/list2.png width=300>
* `lolviz()`: List of lists visualization with the first list vertical and the nested lists horizontal.<br><img src=images/lol2.png width=400>

## Installation

```bash
$ pip install lolviz
```

## Usage

From within generic Python, you can get a window to pop up using the `render()` method:

```python
from lolviz import *
g = listviz(['hi','mom',{3,4},{"parrt":"user"}])
g.render(view=True) # render graphviz.files.Source object
```

<img src="images/list.png" width=200>

From within Jupyter notebooks you can avoid the `render()` call because Jupyter knows how to display `graphviz.files.Source` objects:

<img src=images/jupyter.png width=700>