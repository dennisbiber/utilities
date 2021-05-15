import csv
import numpy as np
import pandas as pd
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

# Numpy Statistical Functions

def getMedian(valueList):
	return np.median(valueList)

def getMean(valueList):
	return np.mean(valueList)

def getVariance(valueList):
	return np.var(valueList)

def getSTD(valueList):
	return np.std(valueList)

# Hashing Functions

def getSHA256(msg):
	return hashlib.sha256(msg.encode("utf-8")).hexdigest()

def getSHA224(msg):
	return hashlib.sha224(new.encode("utf-8")).hexdigest()

def getMD5Hash(msg):
	return hashlib.md5(msg).hexdigest()

