import tecplot as tp
from tecplot.constant import PlotType, AxisTitleMode, Color
import numpy as np
import os

def extractLine(dataset, zoneNr, nodeNr, distance):
	page = tp.active_page()
	frame = page.frame('Frame 001')
	frame.activate()
	Zne=dataset.zone(zoneNr)
	#Identification of var names for cordinates and normal vector
	coordVars=['x','y']
	vectorVars=['X Grid I Unit Normal','Y Grid I Unit Normal']

	#retrieves the start point(on the surface) and the end point of the line(offset)
	surfPt=[Zne.values(i)[nodeNr] for i in coordVars]
	endPt=[i-Zne.values(j)[nodeNr]*distance for i,j in zip(surfPt,vectorVars)]

	#defines all of the points coordinates along the line:
	linePts=np.zeros((3,100))
	for i,(j,k) in enumerate(zip(surfPt,endPt)):
	    linePts[i]=np.linspace(j, k, 100)
	#extract the line in Tecplot
	line = tp.data.extract.extract_line(zip(linePts[0],linePts[1]))

	#Compute the distance along the line
	tp.data.operate.execute_equation(equation=\
	    '{Dist}=SQRT(({'+'X}'+'-{}'.format(surfPt[0])+')**2'\
	        +'+({'+'Y}'+'-{}'.format(surfPt[1])+')**2)', zones=line)
	tp.data.operate.execute_equation(equation=\
		'{Layer Velocity} = {Y Velocity} * {X Grid I Unit Normal} - {X Velocity} * {Y Grid I Unit Normal}',
    zones=line)

	return dataset, line

def drawProfile(dataset, line, i, nameList):
	#Create a new frame for the plot
	frame2=tp.active_page().add_frame()
	frame2.position=(0.3 + 3.2 * i, 5.0)
	frame2.height=3.2
	frame2.width=3.2
	plot = tp.active_frame().plot(PlotType.XYLine)
	plot.activate()

	plot.delete_linemaps()
	lmap = plot.add_linemap('data', line, x=dataset.variable('Layer Velocity'), y=dataset.variable('Dist'))
	lmap.name='Velocity Profile'
	frame2.add_text(nameList[i], position=(35, 50), bold=True, italic=False, color=Color.Blue)
	lmap.line.line_thickness = 0.6

	plot.axes.x_axis(0).title.title_mode=AxisTitleMode.UseText
	plot.axes.y_axis(0).title.title_mode=AxisTitleMode.UseText
	plot.axes.x_axis(0).title.text = 'u(m/s)'
	plot.axes.y_axis(0).title.text = 'h/c,%'
	plot.axes.x_axis(0).fit_range_to_nice()

	plot.view.fit()

if __name__ == "__main__":
	tp.session.connect()

	#Initialize dataset and frame
	page = tp.active_page()
	frame = page.frame('Frame 001')
	frame.activate()
	dataset = frame.dataset
	zoneNr = 36
	distance = 0.05
	nodeList = [16825, 17386, 17541, 17665, 17820, 18006, \
				18130, 18223]
	nameList = ['0.9c', '0.94c', '0.95c', '0.96c', '0.97c', '0.98c', \
				'0.985c', '0.99c']
	i = 0
	
	#Calculate 2D Vector dicrection and velocity magnitude once
	tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
	    command=("Calculate Function='GRIDIUNITNORMAL' Normalization='None'"\
	        +" ValueLocation='Nodal' CalculateOnDemand='F'"\
	        +" UseMorePointsForFEGradientCalculations='F'"))
	#tp.macro.execute_extended_command(command_processor_id='CFDAnalyzer4',
	    #command="Calculate Function='VELOCITYMAG' Normalization='None' ValueLocation='Nodal' CalculateOnDemand='F' UseMorePointsForFEGradientCalculations='F'")

	for nodeNr in nodeList:
		data, line = extractLine(dataset, zoneNr - 1, nodeNr - 1, distance)
		drawProfile(data, line, i, nameList)
		i = i + 1