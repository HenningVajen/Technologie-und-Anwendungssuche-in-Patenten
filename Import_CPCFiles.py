#loads .csv files with CPC titles and stores them into a dict and saves the dict in a pickle file

import csv
import os
import utility_Datenbearbeitung

#-----------------------    CONFIG   -----------------------
inputPath = os.path.join(os.getcwd(), "input", "CPC_Definitions")
outputPath = os.path.join(os.getcwd(), "output")
outputFile = "CPCDict.pkl"
#-----------------------------------------------------------

filelist = os.listdir(inputPath)
CPCdict = {}
print(filelist)

for file in filelist:
    with open(os.path.join(inputPath, file) , mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter =";")
        for row in csv_reader:
            CPCdict[row["CPC"]] = {
                 str(row["title"])
            }

utility_Datenbearbeitung.speichereObjekt(CPCdict,outputPath, outputFile)
