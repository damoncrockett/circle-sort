import pandas as pd
import numpy as np

DIR = "/Users/damoncrockett/Desktop/Seoul_selfies/"

df = pd.read_csv(DIR+"slices/slice_metadata.csv")
tmp = df.sample(n=10000)

print "data read"

from shapely.geometry import Point
from PIL import Image

thumb_side = 16

#puresortvar = 'hue_med'
#tmp = df.sort([puresortvar])
    
# option to double sort, need to bin first

options = [
['val_mean','hue_mean',[0,.25,.5,.75,1]],
['val_mean','hue_mean',[0,.25,.75,1]],
['val_mean','hue_mean',[0,.75,1]],
['val_mean','hue_mean',[0,.125,.25,.375,.5,.625,.75,.875,1]],
['val_mean','hue_med',[0,.25,.5,.75,1]],
['val_mean','hue_med',[0,.25,.75,1]],
['val_mean','hue_med',[0,.33,.67,1]],
['val_mean','hue_med',[0,.67,1]],
['val_mean','hue_med',[0,.75,1]],
['val_mean','hue_med',[0,.125,.25,.375,.5,.625,.75,.875,1]],
['val_mean','sat_mean',[0,.25,.5,.75,1]],
['val_mean','sat_mean',[0,.25,.75,1]],
['val_mean','sat_mean',[0,.75,1]],
['val_mean','sat_mean',[0,.125,.25,.375,.5,.625,.75,.875,1]],
['val_mean','sat_med',[0,.25,.5,.75,1]],
['val_mean','sat_med',[0,.25,.75,1]],
['val_mean','sat_med',[0,.33,.67,1]],
['val_mean','sat_med',[0,.75,1]],
['val_mean','val_mean',[0,.5,1]]
]


for option in options:
	y_bin_var,sort_var,cut = option
	
	try:
		tmp['y_bin'] = pd.cut(tmp[y_bin_var],cut,labels=False)
	except:
		print "can't bin"

	# sort the resulting DataFrame (tmp) by the sorting variable
	# note ascending kwarg

	try:
		#tmp = tmp.sort(['y_bin'],ascending=[False])
		 tmp = tmp.sort(['y_bin',sort_var],ascending=[False,False])
	except:
		 print "can't double sort"
		 #tmp = tmp.sort(sort_var,ascending=True)

	# reset index because we'll use the index in a loop
	tmp.reset_index(drop=True,inplace=True)
	n = len(tmp.index)

	print "data sorted"

	side = int(round(np.sqrt(n))) + 4
	canvas = Image.new('RGB',(side * thumb_side, side * thumb_side),(50,50,50))
	x,y = range(side) * side, np.repeat(range(side),side)
	grid_list = pd.DataFrame(x,columns=['x'])
	grid_list['y'] = y

	point = []
	m = len(grid_list.index)
	for i in range(m):
		point.append(Point(grid_list.x.loc[i],grid_list.y.loc[i]))
	grid_list['point'] = point
	open_grid = list(grid_list.point)

	print "grid constructed"

	exemplar = Point(int(round(side/2)),int(round(side/2)))
	im = Image.open(tmp.filename.loc[0])
	im.thumbnail((thumb_side,thumb_side),Image.ANTIALIAS)
	x = int(exemplar.x) * thumb_side
	y = int(exemplar.y) * thumb_side
	canvas.paste(im,(x,y))
	open_grid.remove(exemplar)

	print "exemplar plotted"

	for i in range(1,n):
		im = Image.open(tmp.filename.loc[i])
		im.thumbnail((thumb_side,thumb_side),Image.ANTIALIAS)
		closest_open = min(open_grid,key=lambda x: exemplar.distance(x))
		x = int(closest_open.x) * thumb_side
		y = int(closest_open.y) * thumb_side
		canvas.paste(im,(x,y))
		print i,"pasted","of",n
		open_grid.remove(closest_open)
		print i,"removed from open_grid","of",n

	cut_string = str(cut).translate(None,"][,.")
	canvas.save(DIR+"circle_sorts/"+
				"_"+y_bin_var+
				"_"+sort_var+
				cut_string+".png")