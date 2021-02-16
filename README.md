# Simple OpenCV based bounding box annotation tool for rotated bounding boxes
Tested with Ubuntu 18.04 & Windows 10. Python 3.6

### Minimum requirements

Python libraries: Numpy v.1.15.3, OpenCV v.3.4.2 and Pillow v.5.3.0


## How to run
### annotation tool
Add images to be annotated to Images-folder. Then run:
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

