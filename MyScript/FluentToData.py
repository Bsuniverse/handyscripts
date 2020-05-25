import tecplot as tp
from tecplot.constant import *
tp.session.connect()

ds = tp.active_frame().dataset
sections = ds.zones("fluid")

for section in sections:
	section_x = section.values('X').as_numpy_array()
	section_y = section.values('Y').as_numpy_array()
	section_vor = section.values('Z Vorticity').as_numpy_array()
	print(section_x - section_y)
