# Simple OpenCV based bounding box annotation tool
Tested with Ubuntu 18.04 & Windows 10. Python 3.6

### Minimum requirements

Python libraries: Numpy, OpenCV and Pillow


## How to run
### annotation tool
```
$ python3 simple_annotation_tool.py
```
annotations format: \
x y (box 1::vertice1)  \
x y (box 1::vertice2) \
x y (box 1::vertice3) \
x y (box 1::vertice4) \
x y (box 2::vertice1) \
x y (box 2::vertice2) \
. \
. \
.
### resizing tool
```
$ python3 resizing_tool.py --size [W] [H] --input-path [path] --output-path [path] 
```

