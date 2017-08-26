# lolviz

A simple Python data-structure visualization tool for lists of lists, lists, dictionaries; primarily for use in Jupyter notebooks / presentations. It seems that I'm always trying to describe how data is laid out in memory to students. There are really great data structure visualization tools but I wanted something I could use directly via Python in Jupyter notebooks. The look and idea was inspired by the awesome [Python tutor](http://www.pythontutor.com).

There are currently three functions of interest:

* `dictviz()` A dictionary visualization
* `listviz()`
* `lolviz()`

## Installation

```bash
$ pip install lolviz
```

## Usage

From within generic Python,

```python
from lolviz import *
g = listviz(['hi','mom',{3,4},{"parrt":"user"}])
g.render(view=True)
```

<img src="images/list.png" width=200>
