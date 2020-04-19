""" 
This scripts reads Whatsapp chat log and prints some graphs. 
Giuseppe Minardi 
Jan 2019 
03/08/16, 20:14 - Federica Selene Saltori Satta: Comunque non penso, uscire di casa presuppone lavarmi e darmi un aspetto umano
""" 
from datetime import datetime 
import string 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
import matplotlib.dates as mdates
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

plt.style.use('seaborn-dark') 

from os import path 
from PIL import Image 
from wordcloud import WordCloud, ImageColorGenerator 
from nltk.corpus import stopwords 
stopWords = stopwords.words('italian')

log = "./ChatWhatsApp.txt"

def wapp_parsing(file):     
    """     
    This function parses the log file avoiding non-text lines, and avoiding     
    problems from messages sent by the same person in one minute     
    """     
    Data = {"DateTime":[], "name":[], "msg":[]}

    def lineSplitter(line):
        """
            This function splits each line of the log
        """
        if line.find(":") == 12:
            splitted = line.split(' - ')
            Data["DateTime"].append(splitted[0])

            splitted = splitted[1].split(":")
            Data["name"].append(splitted[0])

            Data["msg"].append(splitted[1][0:-1])


    print("Loading... Parsing the file.")     

    with open(file) as f:         
        prev = ""
        for line in f:             
            if (len(line)!=0):                 
                if (line[0] in string.digits) and (line[1] in string.digits):                     
                    prev = line[0: line.find(":", 14, -1)+1]                     
                    lineSplitter(line)
                else:                     
                    line = prev + line                     
                    lineSplitter(line)
    return Data

def dataManipulation(data): 
    """ 
    This function manipulates the dataframe and extracts info 
    """ 
    data['DateTime'] = pd.to_datetime(data['DateTime'], dayfirst=True, infer_datetime_format=True) 
    data['msgLen'] = data.msg.apply(lambda x: len(x.split())) 
    data.set_index("DateTime", inplace = True)
    return data

def aggregateMonthName(data):
    finalDF = pd.DataFrame()

    for name, DF in data.groupby(data["name"]):
        temp = DF.resample("M").mean()
        temp["name"] = name
        finalDF = pd.concat([finalDF, temp])

    return(finalDF)

def separateMedia(data, hotkey = "<Media omessi>"):

    media = data[data["msg"].str.contains(hotkey, regex=False)]
    notMedia = data[~data["msg"].str.contains(hotkey, regex=False)]

    return (media, notMedia)

def plotTotal(conversationDF):

    conversationDF = conversationDF.resample('M').count()


    date = pd.to_datetime(conversationDF.index.values)
    fig, ax = plt.subplots(figsize=(32, 18))

#    ax.bar(conversationDF.index.values, conversationDF["msgLen"])
    sns.barplot(x = date, y = conversationDF["msgLen"], ax = ax)


    ax.set_xticklabels(date.strftime("%Y-%b"), 
                       rotation = 65, 
                       size = 30, 
                       rotation_mode = "anchor",
                       horizontalalignment= "right", 
                       verticalalignment= "top")
    ax.tick_params(axis='y', labelsize=30)
    plt.ylabel("Number of messages", size = 35)
    plt.savefig("TotalMsgMonth.png")

def plotMeanMsgLength(data):
    fig, ax = plt.subplots(2, 1, sharex='col', sharey= True, figsize = (16, 9))
    plt.title("Mean message length")

    for index, name in enumerate(conversationDF.name.unique()):

        conversator = conversationDF[conversationDF["name"] == name]
        date = pd.to_datetime(conversator.index.values)

        sns.barplot(x = date, y = conversator["msgLen"], ax = ax[index])

        ax[index].set_xticklabels(date.strftime("%Y-%b"), 
                           rotation = 65, 
                           rotation_mode = "anchor",
                           horizontalalignment= "right", 
                           verticalalignment= "top")
        ax[index].set(ylabel=name)

    plt.savefig("MeanMsgLength.png")

def plotMedia(data):
    fig, ax = plt.subplots()

    sns.countplot(x="name", data=data, ax = ax)
    plt.xlabel("")
    plt.title("Photosm videos or audio exchanged")
    plt.ylabel("Media number")

    plt.savefig("numberOfMedia.png")




if __name__ == '__main__':

    conversationDF = dataManipulation(pd.DataFrame(wapp_parsing(log)))
    print("Wait... I'm making the first plot")
    plotTotal(conversationDF)

    conversationMedia ,conversationNoMedia = separateMedia(conversationDF)
    print("Wait... I'm making the second plot")
    plotMedia(conversationMedia)

    conversationNoMedia = aggregateMonthName(conversationNoMedia)
    print("Wait... I'm making the third plot")
    plotMeanMsgLength(conversationNoMedia)

