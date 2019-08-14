# 2019-atmoswing-external-optimization
External optimization AtmoSwing


Report on optimizing AtmoSwing input parameters
Seminar geodata analysis and modelling by Dr. Pascal Horton & Dr. Andreas Zischg
University of Bern, FS 2019
Julian Bernegger - 14-121-610
Abstract
AtmoSwing (Analog Technique Model for Statistical weather downscalING and forecastING) is a scientific open-source software, developed at the university of Lausanne to automate calculations from a set of data to possible events and conditions in the future. The software package includes a forecaster, a viewer, a downscale and an optimizer. The aim of the method described in this report was to optimize five interdependent input metadata parameters for the AtmoSwingOptimizer by writing and running a Python program in PyCharm.
Method
The AtmoSwingOptimizer uses xml files to specify information on how to treat data. In the program written in this work, the five parameters optimized, their ranges tested and the predefined iterations are:
parameter	min	max	step
analogs_number	5.00	80.00	no predefined values
x_min	-10.00	10.00	1.25
x_points_nb	1.00	25.00	1
y_min	35.00	50.00	1.25
y_points_nb	1.00	17.00	1

The main workflow of the program is to create an array with vectors of possible combinations for the input parameters, run AtmoSwingOptimizer in a loop of testing all vectors of the array and rely the creation of the next array on the resulting low calibration number (CRPS) and the relating parameters vector. In this program this workflow is run four times to get the optimized parameters for the xml file of AtmoSwingOptimizer. In the first run, the wide ranges are combined with a low number of possible values per parameter. The second run focuses the creation of the array on a new range around the optimized parameters relating to resulting CRPS of the first run. In the runs 3 and 4, ranges get smaller and the resolution of values get higher (Fig. 1).
Result
By running the python program, a minimum number of 0.2715581 for the CRPS value could be pointed out. The optimal vector of the five input parameters for the xml file related to this CRPS minimum is: Analogs_number = 15.160468743, x_min = -3.75, x_points_nb = 12, y_min = 41.25, y_points_nb = 9. While there were five possible values for parameter 1 estimated to be possible for the same CRPS minimum, what is visible in Figure 8.


