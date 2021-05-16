import csv
import json
import numpy as np
import pandas as pd
import string
import time

__author__ = "Dennis Biber"

# Time Functions

def getTime():
	return time.time()

def getTimeElapsed(t0, t1):
	return t1-t0

# Read and Write CSV Functions

def readCSV(path):
	return open(path, "r")

def writeCSV(path):
	return open(path, "w")

# Pandas DataFrame Functions

def createDF(data, columnList):
	# Return Variable should be named "df"
	return pd.DataFrame(data,columns=columnList)

def readCSVToDF(path):
	# Return Variable should be named "df" since it converts a CSV to DataFrame
	return pd.read_csv(path)

def postDFToCSV(df, path):
	# Path = location and filename of the CSV we are writing the DataFrame to
	return df.to_csv(path)

def getDFColumns(df):
	# Returns: Column names from DataFrame
	return df.columns

def getDFInfo(df):
	return df.info()

def getDFStats(df):
	return df.describe()

def getNpFromDF(df):
	return df.to_numpy()

# Numpy Statistical Functions

def getMedian(valueList):
	return np.median(valueList)

def getWeightedMean(valueList, weight):
	return np.average(valueList, weight=weight)

def getMean(valueList):
	return np.mean(valueList)

def getVariance(valueList):
	return np.var(valueList)

def getSTD(valueList):
	return np.std(valueList)

def getNaN():
	return np.nan()

def getPercentile(valueList, percentile):
	return np.percentile(valueList, percentile)

def getQuantile(valueList, quantile):
	return np.quantile(valueList, quantile)

def getRange(valueList):
	return np.ptp(valueList)

def getMaxValue(valueList):
	return np.max(valueList)

def getMinValue(valueList):
	return np.min(valueList)

def getCovariance(vector1, vector2):
	return np.cov(vector1, vector2)

def getCorrelationCoefficientMatrix(vector1, vector2):
	return np.corrcoef(vector1, vector2)

# Numpy arrays

def getNumpyArange(start, end, steps):
	return np.arange(start, end, steps)

def getConcatArraysOnRow(arr1, arr2):
	return np.concatenate((arr1,arr2),axis=0)

def getConcatArrayOnColumns(arr1, arr2):
	return np.concatenate((arr1,arr2),axis=1)

# Numpy Scalar Math

def putNumberToElements(arr, number):
	return np.add(arr, number)

def putNegativeNumberToElements(arr, number):
	return np.subtract(arr, number)

# Hashing Functions

def getSHA256(msg):
	return hashlib.sha256(msg.encode("utf-8")).hexdigest()

def getSHA224(msg):
	return hashlib.sha224(new.encode("utf-8")).hexdigest()

def getMD5Hash(msg):
	return hashlib.md5(msg).hexdigest()

# String Manipulation

def getStringFromDict(kvp):
	return json.dump(kvp).encode("utf-8")

def getStringFromInt(integer):
	return f"{integer}"

def getStringFromList(listName):
	newString = ""
	for x in listName:
		newString = newString + f'{x}'
	return newString

def getLengthFromRange(rangeValue):
	return len(range(rangeValue))

def getConcat(string1, string2):
	return string1 + string2

def getStringAsTitle(string1):
	return string1.title()

def getIndexFromString(string1, idxValue):
	return string1.find(idxValue)

# Functions for creating specific lists

def getBase51AlphabetList():
	return string.ascii_lowercase + string.ascii_uppercase

def getBase10IntsList():
	return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def getBase10StrList():
	return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def getBase60AlphaNumericList():
	return getBase10StrList + getBase51AlphabetList

