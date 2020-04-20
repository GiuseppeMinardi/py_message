""" 
This scripts reads Whatsapp chat log and prints some graphs. 
Giuseppe Minardi 
Jan 2019 
""" 
from datetime import datetime 
import string 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
import matplotlib.dates as mdates

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

plt.style.use('seaborn-dark') 

from math import pi
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
    plt.close()

def plotMeanMsgLength(data):
    fig, ax = plt.subplots(2, 1, sharex= True, sharey= True, figsize = (16, 9))
    plt.title("Mean message length")

    for idx, name in enumerate(data.name.unique()):

        conversator = data[data["name"] == name]
        date = pd.to_datetime(conversator.index.values)

        sns.barplot(x = date, y = conversator["msgLen"], ax = ax[idx])

        ax[idx].set_xticklabels(date.strftime("%Y-%b"), 
                           rotation = 65, 
                           rotation_mode = "anchor",
                           horizontalalignment= "right", 
                           verticalalignment= "top")
        ax[idx].set(ylabel=name)

    plt.savefig("MeanMsgLength.png")

def plotMedia(data):
    fig, ax = plt.subplots()

    sns.countplot(x="name", data=data, ax = ax)
    plt.xlabel("")
    plt.title("Photosm videos or audio exchanged")
    plt.ylabel("Media number")

    plt.savefig("numberOfMedia.png")
    plt.close()

def radialPlot(data):
    conversationHourly = data.groupby([data.index.hour, "name"]).size().reset_index()
    conversationHourly.columns = ["DateTime", "name", "sums"]

    conversationHourly = conversationHourly.pivot(index='name', columns='DateTime', values='sums').reset_index()
    conversationHourly.columns = [str(name) for name in conversationHourly.columns]

    total = [column for column in conversationHourly.columns if column != "name"]
    proportions = conversationHourly[total].div(conversationHourly[total].sum(axis=1), axis=0)
    conversationHourly[total] = proportions

    maxValue = conversationHourly[total].max().max() 
    spacer = [round(number, 3) for number in np.linspace(0, maxValue, num=4)]

    #print(conversationHourly[total].sum(axis=1))
    #print(conversationHourly)
    #data['msgLen'] = data.msg.apply(lambda x: len(x.split())) 

    # ------- PART 1: Create background

# number of variable
    categories=list(conversationHourly)[1:]
    N = len(categories)

# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

# Initialise the spider plot
    ax = plt.subplot(111, polar=True)

# If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

# Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories)

# Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(spacer, [str(number) for number in spacer], color="grey", size=7)
    plt.ylim(0,maxValue)


# ------- PART 2: Add plots

# Plot each individual = each line of the data
# I don't do a loop, because plotting more than 3 groups makes the chart unreadable

# Ind1
    values=conversationHourly.loc[0].drop('name').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label= conversationHourly["name"].iloc[0])
    ax.fill(angles, values, 'b', alpha=0.1)

# Ind2
    values=conversationHourly.loc[1].drop('name').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=conversationHourly["name"].iloc[1])
    ax.fill(angles, values, 'r', alpha=0.1)

# Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.3, 0.1))
    plt.savefig("radialPlot.png")



if __name__ == '__main__':

    conversationDF = dataManipulation(pd.DataFrame(wapp_parsing(log)))
    print("Wait... I'm making the first plot")
    plotTotal(conversationDF)
    print("Wait... I'm making the second plot")
    radialPlot(conversationDF)





    conversationMedia ,conversationNoMedia = separateMedia(conversationDF)
    print("Wait... I'm making the third plot")
    plotMedia(conversationMedia)

    conversationNoMedia = aggregateMonthName(conversationNoMedia)
    print("Wait... I'm making the 4th plot")
    plotMeanMsgLength(conversationNoMedia)

