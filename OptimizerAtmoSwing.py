import os
import subprocess
import math
import numpy as np
import glob
import random
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from array import *
from io import StringIO
import shutil

# define working directory
path = "C:/Users/cyber/Desktop/University/Project"
os.chdir(path)

# define directory of predictor file
folder = "data"

# define input nc file with model data
ncfile = "data/Precipitation-Daily-Catchment-RhiresD-Switzerland.nc"

# define AtmoSwing Optimizer xml file to be optimized
xmlfile = "data/output.xml"

################################################################################################################################################
# run1
#################################################################################################################################################
# define number of values for parameter 1
n_sample = 30
analogs_number_sample = np.linspace(10, 80, n_sample)
# create arrays with possible values for parameters (2, 3, 4, 5) optimized ranges, because of steps in the loop
x_min_sample = np.arange(-10, 11, 1.25)
x_points_nb_sample = np.arange(1, 27, 1)
y_min_sample = np.arange(35, 55, 1.25)
y_points_nb_sample = np.arange(1, 19, 1)
# define empty list to collect resulting CRPS values
C_opt_1 = []
# define empty array to create combinations of values for AtmoSwing input
input_array = np.empty((0, 5))

###################################################################################################################################################
# create vectors of all possible combinations (rows) of input parameters, low resolution to get a first picture 102060 vectors

for sample in range(0, n_sample):
    for con1 in range(0, 17, 2):
        for con2 in range(0, 25, 3):
            for con3 in range(1, 14, 2):
                for con4 in range(1, 18, 2):
                    para = [str(analogs_number_sample[sample]), str(x_min_sample[con1]), str(x_points_nb_sample[con2]), str(y_min_sample[con3]), str(y_points_nb_sample[con4])]

                    input_array = np.append(input_array, [para], axis=0)

print(input_array)
print("input_array has " +str(int(input_array.size/5)) + " rows")
np.savetxt("input_array_1.txt", input_array, fmt="%s")

##################################################################################################################################################
# reopen the saved input_array/ or C_opt
input_array = np.loadtxt("input_array_1.txt")

################################################################################################################################################
# delete all subfolders in run
shutil.rmtree("runs")
os.mkdir("runs")
################################################################################################################################################

# define number of runs of AtmoSwing by counting the number of rows in the generated imput_array_light
runs = int(input_array.size/5)

##################################################################################################################################################
# change xml input file with parameters out of the input_array and run AtmoSwing in a loop
for run in range(1, runs+1):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for elem in root.iter("analogs_number"):
            elem.text = str(input_array[run-1, 0])
    for elem in root.iter("x_min"):
            elem.text = str(input_array[run-1, 1])
    for elem in root.iter("x_points_nb"):
            elem.text = str(input_array[run-1, 2])
    for elem in root.iter("y_min"):
            elem.text = str(input_array[run-1, 3])
    for elem in root.iter("y_points_nb"):
            elem.text = str(input_array[run-1, 4])
# save the modified xml file
    tree.write("data/input.xml")
    input = ("data/input.xml")

    subprocess.call(["C:/Program Files/AtmoSwing/bin/atmoswing-optimizer.exe", "-s", "-l", "-r {}".format(run), "--file-parameters=" +input,"--predictand-db=" +ncfile, "--dir-predictors=" +folder, "--log-level=2", "--calibration-method=single", "--threads-nb=4", "--station-id=1"])

# define output file of AtmoSwing run
    outtext = "runs/{}/results/*all_station_parameters.txt".format(run)

    for result in glob.glob(outtext):
            rf = open(result, "r")
            text = rf.read()
# create a string to get the number out of it
            index = text

# create a list to count the place, where the calib is
            li = [text]
            nbli = int(li[0].find("Calib"))
            rf.close

# define the CRPS number out of the results
            CRPS = float(index[nbli+6:nbli+18])

# append current CRPS to list of results
            C_opt_1.append(CRPS)


            print(("run number: ")+str(run)+(" CRPS = ")+str(CRPS))

# search for minimum element index in list of CPRS and define the related parameters of input_array_light
P_opt_1 = input_array[C_opt_1.index(min(C_opt_1))]

# save resulting CRPS list
with open("C_opt_1.txt", "w") as output:
    output.write(str(C_opt_1))

# print the resulting optimization of AtmoSwingOptimizer
print(("min CRPS is ") + str(min(C_opt_1)))
print(("optimized parameters are ")+str(P_opt_1))

# reopen the saved input_array/ or C_opt
input_array = np.loadtxt("input_array_1.txt")

f = open("C_opt_1.txt", "r")
x = f.read()
#C_opt_11 = list(x)
C = x.split(",")
C_opt_1 = list(np.float_(C))


###################################################################################################################################################
# create lists out of input_array columns and plot run1
p1r1 = input_array[:, 0].tolist()
p2r1 = input_array[:, 1].tolist()
p3r1 = input_array[:, 2].tolist()
p4r1 = input_array[:, 3].tolist()
p5r1 = input_array[:, 4].tolist()


plt.scatter(p2r1, C_opt_1, s=3, c="r", marker="o", label="x_min")
plt.scatter(p5r1, C_opt_1, s=3, c="m", marker="o", label="y_points_nb")
plt.scatter(p3r1, C_opt_1, s=3, c="y", marker="o", label="x_points_nb")
plt.scatter(p4r1, C_opt_1, s=3, c="g", marker="o", label="y_min")
plt.scatter(p1r1, C_opt_1, s=3, c="b", marker="o", label="analogs_number")
plt.locator_params(axis="x", nbins=10)
plt.locator_params(axis="y", nbins=40)
xint = range(-5, 50)
plt.title("run 1")
plt.xlabel("input parameters []")
plt.ylabel("CRPS")
plt.legend(loc="upper left");
plt.grid()
plt.show


################################################################################################################################################
# run2
#################################################################################################################################################
# define number of values for parameter 1
n_sample = 30
# define new ranges, adapted to results from run1
analogs_number_sample = np.linspace(P_opt_1[0]-7, P_opt_1[0]+8, n_sample)

# create adapted arrays to run1 with possible values for parameters (2, 3, 4, 5)
x_min_sample = np.arange(P_opt_1[1]-5, P_opt_1[1]+6.25, 1.25)
x_points_nb_sample = np.arange(P_opt_1[2]-4, P_opt_1[2]+5, 1)
y_min_sample = np.arange(P_opt_1[3]-5, P_opt_1[3]+6.25, 1.25)
y_points_nb_sample = np.arange(P_opt_1[4]-2, P_opt_1[4]+3, 1)

# define empty list to collect resulting CRPS values
C_opt_2 = []

# define empty array to create combinations of values for AtmoSwing input
input_array_2 = np.empty((0, 5))

###################################################################################################################################################
# create vectors of all possible combinations (rows) of input parameters_2, different ranges than run1, higher resolution (iterations given)
for sample in range(0, n_sample, 2):# n_sample values*********************************
    for con1 in range(0, 9):# 5 values************************************************TO BE DEFINED****************+++++++++++++++++++++++++++++++++
        for con2 in range(0, 9):# 5 values
            for con3 in range(0, 9, 2):# 5
                for con4 in range(0, 5):# 5
                    para = [str(analogs_number_sample[sample]), str(x_min_sample[con1]), str(x_points_nb_sample[con2]), str(y_min_sample[con3]), str(y_points_nb_sample[con4])]
                    print(para)
                    print(sample)
                    input_array_2 = np.append(input_array_2, [para], axis=0)

#print(input_array)
print("input_array_2 has " +str(int(input_array_2.size/5)) + " rows")
np.savetxt("input_array_2.txt", input_array_2, fmt="%s")

###################################################################################################################################################

# define number of runs of AtmoSwing by counting the number of rows in the generated imput_array_light
runs = int(input_array_2.size/5)

##################################################################################################################################################
# change xml input file with parameters out of the input_array and run AtmoSwing in a loop, save CRPS values to list
for run in range(1, runs+1):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for elem in root.iter("analogs_number"):
            elem.text = str(input_array_2[run-1, 0])
    for elem in root.iter("x_min"):
            elem.text = str(input_array_2[run-1, 1])
    for elem in root.iter("x_points_nb"):
            elem.text = str(input_array_2[run-1, 2])
    for elem in root.iter("y_min"):
            elem.text = str(input_array_2[run-1, 3])
    for elem in root.iter("y_points_nb"):
            elem.text = str(input_array_2[run-1, 4])
# save the modified xml file
    tree.write("data/input.xml")
    input = ("data/input.xml")

    subprocess.call(["C:/Program Files/AtmoSwing/bin/atmoswing-optimizer.exe", "-s", "-l", "-r {}".format(run), "--file-parameters=" +input,"--predictand-db=" +ncfile, "--dir-predictors=" +folder, "--log-level=2", "--calibration-method=single", "--threads-nb=4", "--station-id=1"])

# define output file of AtmoSwing run
    outtext = "runs/{}/results/*all_station_parameters.txt".format(run)

    for result in glob.glob(outtext):
            rf = open(result, "r")
            text = rf.read()
# create a string to get the number out of it
            index = text

# create a list to count the place, where the calib is
            li = [text]
            nbli = int(li[0].find("Calib"))
            rf.close

# define the CRPS number out of the results
            CRPS = float(index[nbli+6:nbli+18])

# append current CRPS to list of results
            C_opt_2.append(CRPS)


            print(("run number: ")+str(run)+(" CRPS = ")+str(CRPS))

################################################################################################################################################
# delete all subfolders in run
shutil.rmtree("runs")
os.mkdir("runs")
################################################################################################################################################

# reopen after closing the program
input_array_2 = np.loadtxt("input_array_2.txt")


# search for minimum element index in list of CPRS and define the related parameters of input_array_light
P_opt_2 = input_array_2[C_opt_2.index(min(C_opt_2))]

# save resulting CRPS list
with open("C_opt_2.txt", "w") as output:
    output.write(str(C_opt_2))

# print the resulting optimization of AtmoSwingOptimizer
print(("min CRPS is ") + str(min(C_opt_2)))
print(("optimized parameters are ")+str(P_opt_2))


f = open("C_opt_2.txt", "r")
x = f.read()
#C_opt_11 = list(x)
C2 = x.split(",")
C_opt_2 = list(np.float_(C2))

###################################################################################################################################################
# create lists out of input_array columns and plot run2
p1r2 = input_array_2[:, 0].tolist()
p2r2 = input_array_2[:, 1].tolist()
p3r2 = input_array_2[:, 2].tolist()
p4r2 = input_array_2[:, 3].tolist()
p5r2 = input_array_2[:, 4].tolist()


plt.scatter(p2r2, C_opt_2, s=7, c="r", marker="o", label="x_min")
plt.scatter(p5r2, C_opt_2, s=7, c="m", marker="o", label="y_points_nb")
plt.scatter(p3r2, C_opt_2, s=7, c="y", marker="o", label="x_points_nb")
plt.scatter(p4r2, C_opt_2, s=7, c="g", marker="o", label="y_min")
plt.scatter(p1r2, C_opt_2, s=7, c="b", marker="o", label="analogs_number")
plt.locator_params(axis="x", nbins=10)
plt.locator_params(axis="y", nbins=30)
xint = range(-5, 50)
plt.title("run 2")
plt.xlabel("input parameters []")
plt.ylabel("CRPS")
plt.legend(loc="upper left");
plt.grid()
plt.show

################################################################################################################################################
# run3
#################################################################################################################################################
# define number of values for parameter 1
n_sample = 50
# define new ranges, adapted to results from run2
analogs_number_sample = np.linspace(P_opt_2[0]-7, P_opt_2[0]+8, n_sample)

# create adapted arrays from run 2 with possible values for parameters (2, 3, 4, 5)
x_min_sample = np.arange(P_opt_2[1]-1.25, P_opt_2[1]+2.5, 1.25)
x_points_nb_sample = np.arange(P_opt_2[2]-1, P_opt_2[2]+2, 1)
y_min_sample = np.arange(P_opt_2[3]-1.25, P_opt_2[3]+2.5, 1.25)
y_points_nb_sample = np.arange(P_opt_2[4]-2, P_opt_2[4]+3, 1)

# define empty list to collect resulting CRPS values
C_opt_3 = []
# define empty array to create combinations of values for AtmoSwing input
input_array_3 = np.empty((0, 5))


###################################################################################################################################################
# create vectors of all possible combinations (rows) of input parameters_3, different ranges than run2, high resolution (iterations given)
for sample in range(0, n_sample):
    for con1 in range(0, 3):
        for con2 in range(0, 3):
            for con3 in range(0, 3):
                for con4 in range(0, 5):
                    para = [str(analogs_number_sample[sample]), str(x_min_sample[con1]), str(x_points_nb_sample[con2]), str(y_min_sample[con3]), str(y_points_nb_sample[con4])]
                    print(para)
                    print(sample)
                    input_array_3 = np.append(input_array_3, [para], axis=0)

#print(input_array)
print("input_array_3 has " +str(int(input_array_3.size/5)) + " rows")
np.savetxt("input_array_3.txt", input_array_3, fmt="%s")


###################################################################################################################################################

# define number of runs of AtmoSwing by counting the number of rows in the generated imput_array_light
runs = int(input_array_3.size/5)

##################################################################################################################################################
# change xml input file with parameters out of the input_array and run AtmoSwing in a loop
for run in range(1, runs+1):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for elem in root.iter("analogs_number"):
            elem.text = str(input_array_3[run-1, 0])
    for elem in root.iter("x_min"):
            elem.text = str(input_array_3[run-1, 1])
    for elem in root.iter("x_points_nb"):
            elem.text = str(input_array_3[run-1, 2])
    for elem in root.iter("y_min"):
            elem.text = str(input_array_3[run-1, 3])
    for elem in root.iter("y_points_nb"):
            elem.text = str(input_array_3[run-1, 4])
# save the modified xml file
    tree.write("data/input.xml")
    input = ("data/input.xml")

    subprocess.call(["C:/Program Files/AtmoSwing/bin/atmoswing-optimizer.exe", "-s", "-l", "-r {}".format(run), "--file-parameters=" +input,"--predictand-db=" +ncfile, "--dir-predictors=" +folder, "--log-level=2", "--calibration-method=single", "--threads-nb=4", "--station-id=1"])

# define output file of AtmoSwing run
    outtext = "runs/{}/results/*all_station_parameters.txt".format(run)

    for result in glob.glob(outtext):
            rf = open(result, "r")
            text = rf.read()
# create a string to get the number out of it
            index = text

# create a list to count the place, where the calib is
            li = [text]
            nbli = int(li[0].find("Calib"))
            rf.close

# define the CRPS number out of the results
            CRPS = float(index[nbli+6:nbli+18])

# append current CRPS to list of results
            C_opt_3.append(CRPS)


            print(("run number: ")+str(run)+(" CRPS = ")+str(CRPS))


# search for minimum element index in list of CPRS and define the related parameters of input_array_light
P_opt_3 = input_array_3[C_opt_3.index(min(C_opt_3))]


# save resulting CRPS list
with open("C_opt_3.txt", "w") as output:
    output.write(str(C_opt_3))

# print the resulting optimization of AtmoSwingOptimizer
print(("min CRPS is ") + str(min(C_opt_3)))
print(("optimized parameters are ")+str(P_opt_3))

################################################################################################################################################
# delete all subfolders in run
shutil.rmtree("runs")
os.mkdir("runs")
################################################################################################################################################
# reopen after closing the program
input_array_3 = np.loadtxt("input_array_3.txt")

f = open("C_opt_3.txt", "r")
x = f.read()
#C_opt_11 = list(x)
C3 = x.split(",")
C_opt_3 = list(np.float_(C3))


##########################################################################################################################
# create lists out of input_array columns and plot run 3
p1r3 = input_array_3[:, 0].tolist()
p2r3 = input_array_3[:, 1].tolist()
p3r3 = input_array_3[:, 2].tolist()
p4r3 = input_array_3[:, 3].tolist()
p5r3 = input_array_3[:, 4].tolist()


plt.scatter(p2r3, C_opt_3, s=7, c="r", marker="o", label="x_min")
plt.scatter(p5r3, C_opt_3, s=7, c="m", marker="o", label="y_points_nb")
plt.scatter(p3r3, C_opt_3, s=7, c="y", marker="o", label="x_points_nb")
plt.scatter(p4r3, C_opt_3, s=7, c="g", marker="o", label="y_min")
plt.scatter(p1r3, C_opt_3, s=7, c="b", marker="o", label="analogs_number")
plt.locator_params(axis="x", nbins=10)
plt.locator_params(axis="y", nbins=30)
xint = range(-5, 50)
plt.title("run 3")
plt.xlabel("input parameters []")
plt.ylabel("CRPS")
plt.legend(loc="upper left");
plt.grid()
plt.show


################################################################################################################################################
# run4
#################################################################################################################################################
# define number of values for parameter 1
n_sample = 30
# define new ranges, adapted to results from run3
analogs_number_sample = np.linspace(float(P_opt_3[0])-3, float(P_opt_3[0])+4, n_sample)

# create arrays from optimized vectors of run 3 with possible values for parameters (2, 3, 4, 5)
x_min_sample = np.arange(float(P_opt_3[1])-1.25, float(P_opt_3[1])+2.5, 1.25)
x_points_nb_sample = np.arange(float(P_opt_3[2])-1, float(P_opt_3[2])+2, 1)
y_min_sample = np.arange(float(P_opt_3[3])-1.25, float(P_opt_3[3])+2.5, 1.25)
y_points_nb_sample = np.arange(float(P_opt_3[4])-1, float(P_opt_3[4])+2, 1)

# define empty list to collect resulting CRPS values
C_opt_4 = []

# define empty array to create combinations of values for AtmoSwing input
input_array_4 = np.empty((0, 5))



###################################################################################################################################################
# create vectors of all possible combinations (rows) of input parameters_3, different ranges, high resolution (iterations given)
for sample in range(0, n_sample):
    for con1 in range(0, 3):
        for con2 in range(0, 3):
            for con3 in range(0, 3):
                for con4 in range(0, 3):
                    para = [str(analogs_number_sample[sample]), str(x_min_sample[con1]), str(x_points_nb_sample[con2]), str(y_min_sample[con3]), str(y_points_nb_sample[con4])]
                    print(para)
                    print(sample)
                    input_array_4 = np.append(input_array_4, [para], axis=0)

#print(input_array)
print("input_array_4 has " +str(int(input_array_4.size/5)) + " rows")
np.savetxt("input_array_4.txt", input_array_4, fmt="%s")


###################################################################################################################################################

# define number of runs of AtmoSwing by counting the number of rows in the generated imput_array_light
runs = int(input_array_4.size/5)

##################################################################################################################################################
# change xml input file with parameters out of the input_array and run AtmoSwing in a loop
for run in range(1, runs+1):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    for elem in root.iter("analogs_number"):
            elem.text = str(input_array_4[run-1, 0])
    for elem in root.iter("x_min"):
            elem.text = str(input_array_4[run-1, 1])
    for elem in root.iter("x_points_nb"):
            elem.text = str(input_array_4[run-1, 2])
    for elem in root.iter("y_min"):
            elem.text = str(input_array_4[run-1, 3])
    for elem in root.iter("y_points_nb"):
            elem.text = str(input_array_4[run-1, 4])
# save the modified xml file
    tree.write("data/input.xml")
    input = ("data/input.xml")

    subprocess.call(["C:/Program Files/AtmoSwing/bin/atmoswing-optimizer.exe", "-s", "-l", "-r {}".format(run), "--file-parameters=" +input,"--predictand-db=" +ncfile, "--dir-predictors=" +folder, "--log-level=2", "--calibration-method=single", "--threads-nb=4", "--station-id=1"])

# define output file of AtmoSwing run
    outtext = "runs/{}/results/*all_station_parameters.txt".format(run)

    for result in glob.glob(outtext):
            rf = open(result, "r")
            text = rf.read()
# create a string to get the number out of it
            index = text

# create a list to count the place, where the calib is
            li = [text]
            nbli = int(li[0].find("Calib"))
            rf.close

# define the CRPS number out of the results
            CRPS = float(index[nbli+6:nbli+18])

# append current CRPS to list of results
            C_opt_4.append(CRPS)


            print(("run number: ")+str(run)+(" CRPS = ")+str(CRPS))


# search for minimum element index in list of CPRS and define the related parameters of input_array_light
P_opt_4 = input_array_4[C_opt_4.index(min(C_opt_4))]

# save resulting CRPS list
with open("C_opt_4.txt", "w") as output:
    output.write(str(C_opt_4))

# print the resulting optimization of AtmoSwingOptimizer
print(("min CRPS is ") + str(min(C_opt_4)))
print(("optimized parameters are ")+str(P_opt_4))


################################################################################################################################################
# delete all subfolders in run
shutil.rmtree("runs")
os.mkdir("runs")
################################################################################################################################################
# reopen after closing program
input_array_4 = np.loadtxt("input_array_4.txt")

f = open("C_opt_4.txt", "r")
x = f.read()
#C_opt_11 = list(x)
C = x.split(",")
C_opt_4 = list(np.float_(C))





##########################################################
# create lists out of input_array columns and plot run 4
p1r4 = input_array_4[:, 0].tolist()
p2r4 = input_array_4[:, 1].tolist()
p3r4 = input_array_4[:, 2].tolist()
p4r4 = input_array_4[:, 3].tolist()
p5r4 = input_array_4[:, 4].tolist()


plt.scatter(p2r4, C_opt_4, s=7, c="r", marker="o", label="x_min")
plt.scatter(p5r4, C_opt_4, s=7, c="m", marker="o", label="y_points_nb")
plt.scatter(p3r4, C_opt_4, s=7, c="y", marker="o", label="x_points_nb")
plt.scatter(p4r4, C_opt_4, s=7, c="g", marker="o", label="y_min")
plt.scatter(p1r4, C_opt_4, s=7, c="b", marker="o", label="analogs_number")
plt.locator_params(axis="x", nbins=10)
plt.locator_params(axis="y", nbins=30)
xint = range(-5, 50)
plt.title("run 4")
plt.xlabel("input parameters []")
plt.ylabel("CRPS")
plt.legend(loc="upper left");
plt.grid()
plt.show
#####################################################################################
#####################################################################################

# plot all results
plt.scatter(p2r1, C_opt_1, s=2, c="lightgrey", marker="o", label="run1")
plt.scatter(p2r2, C_opt_2, s=2, c="dimgrey", marker="o", label="run2")
plt.scatter(p2r3, C_opt_3, s=2, c="k", marker="o", label="run3")
plt.scatter(p2r4, C_opt_4, s=2, c="r", marker="o", label="x_min_run4")

plt.scatter(p5r1, C_opt_1, s=2, c="lightgrey", marker="o")
plt.scatter(p5r2, C_opt_2, s=2, c="dimgrey", marker="o")
plt.scatter(p5r3, C_opt_3, s=2, c="k", marker="o")
plt.scatter(p5r4, C_opt_4, s=2, c="m", marker="o", label="y_points_nb_run4")

plt.scatter(p3r1, C_opt_1, s=4, c="lightgrey", marker="1")
plt.scatter(p3r2, C_opt_2, s=2, c="dimgrey", marker="o")
plt.scatter(p3r3, C_opt_3, s=2, c="k", marker="o")
plt.scatter(p3r4, C_opt_4, s=2, c="y", marker="o", label="x_points_nb_run4")

plt.scatter(p4r1, C_opt_1, s=4, c="lightgrey", marker="1")
plt.scatter(p4r2, C_opt_2, s=2, c="dimgrey", marker="o")
plt.scatter(p4r3, C_opt_3, s=2, c="k", marker="o")
plt.scatter(p4r4, C_opt_4, s=2, c="g", marker="o", label="y_min_run4")

plt.scatter(p1r1, C_opt_1, s=4, c="lightgrey", marker="1", label="analogs_number_run1")
plt.scatter(p1r2, C_opt_2, s=2, c="dimgrey", marker="o", label="analogs_number_run2")
plt.scatter(p1r3, C_opt_3, s=1, c="k", marker="o", label="analogs_number_run3")
plt.scatter(p1r4, C_opt_4, s=1, c="b", marker="o", label="analogs_number_run4")


plt.locator_params(axis="x", nbins=10)
plt.locator_params(axis="y", nbins=30)
plt.ylabel("CRPS")
plt.title("run 1 to run 4")
plt.xlabel("analogs_number []")
plt.legend(loc="upper left");
plt.grid()
plt.show

############################################