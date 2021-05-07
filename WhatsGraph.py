""" 
This scripts reads Whatsapp chat log and prints some graphs. 
Giuseppe Minardi 
Jan 2019 
"""
import argparse
import string
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

plt.style.use('seaborn-dark')

from math import pi
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords


# ===============================================================================
def parseArgouments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log",
                        type=str,
                        help="File txt containing the chat log, downloaded with WhatsApp")
    parser.add_argument("--mask",
                        type=str,
                        default=None,
                        help="Eventual image")
    parser.add_argument("--lang",
                        type=str,
                        default="english",
                        help="Language of the conversation")
    args = parser.parse_args()
    return (args)


def wapp_parsing(file):
    """     
    This function parses the log file avoiding non-text lines, and avoiding     
    problems from messages sent by the same person in one minute     
    """
    Data = {"DateTime": [], "name": [], "msg": []}

    def lineSplitter(line):
        """
            This function splits each line of the log
        """
        if line.find(":") == 12:
            splitted = line.split(' - ')
            Data["DateTime"].append(splitted[0])

            splitted = splitted[1].split(":")
            Data["name"].append(splitted[0])
            print(splitted)
            Data["msg"].append(splitted[1][0:-1].lower())

    print("Loading... Parsing the file.")
    # if the same person sent 2 messages in a minutes the second message
    # misses the date
    with open(file) as f:
        prev = ""
        for line in f:
            if (len(line) != 0):
                if (line[0] in string.digits) and (line[1] in string.digits):
                    prev = line[0: line.find(":", 14, -1) + 1]
                    lineSplitter(line)
                else:
                    line = prev + line
                    lineSplitter(line)
    print("File Parsed!")
    return Data


# ===============================================================================

def dataManipulation(data):
    """ 
    This function manipulates the dataframe and extracts info 
    """
    data['DateTime'] = pd.to_datetime(data['DateTime'], dayfirst=True, infer_datetime_format=True)
    data['msgLen'] = data.msg.apply(lambda x: len(x.split()))
    data.set_index("DateTime", inplace=True)
    return data


# ===============================================================================

def aggregateMonthName(data):
    """
        This function returns a dataframe grouped by the month and the name of who sent the messages
        with the number of text sent by the user during each month
    """
    finalDF = pd.DataFrame()

    for name, DF in data.groupby(data["name"]):
        temp = DF.resample("M").mean()
        temp["name"] = name
        finalDF = pd.concat([finalDF, temp])

    return (finalDF)


# ===============================================================================

def separateMedia(data, hotkey="<.*>"):
    """
    This function returns a tuple containing a dataframe with only media and one without media
    """

    media = data[data["msg"].str.contains(hotkey, regex=True)]
    notMedia = data[~data["msg"].str.contains(hotkey, regex=True)]

    return (media, notMedia)


# ===============================================================================

def plotTotal(conversationDF):
    """
        Save a bar plot thescribing the total number of messages sent each month
    """

    conversationDF = conversationDF.resample('M').count()

    date = pd.to_datetime(conversationDF.index.values)
    fig, ax = plt.subplots(figsize=(32, 18))

    sns.barplot(x=date, y=conversationDF["msgLen"], ax=ax)

    ax.set_xticklabels(date.strftime("%Y-%b"),
                       rotation=65,
                       size=30,
                       rotation_mode="anchor",
                       horizontalalignment="right",
                       verticalalignment="top")
    ax.tick_params(axis='y', labelsize=30)
    plt.ylabel("Number of messages", size=35)
    plt.savefig("TotalMsgMonth.png")
    plt.close()


# ===============================================================================

def plotMeanMsgLength(data):
    """
        Plots two bar plot describing the mean lenght of the messages for each month by the two users
    """
    fig, ax = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(16, 9))
    plt.title("Mean message length")

    for idx, name in enumerate(data.name.unique()):
        conversator = data[data["name"] == name]
        date = pd.to_datetime(conversator.index.values)

        sns.barplot(x=date, y=conversator["msgLen"], ax=ax[idx])

        ax[idx].set_xticklabels(date.strftime("%Y-%b"),
                                rotation=65,
                                rotation_mode="anchor",
                                horizontalalignment="right",
                                verticalalignment="top")
        ax[idx].set(ylabel=name)

    plt.savefig("MeanMsgLength.png")


# ===============================================================================

def plotMedia(data):
    """
        Returns the number of media sent by each user
    """
    fig, ax = plt.subplots()

    sns.countplot(x="name", data=data, ax=ax)
    plt.xlabel("")
    plt.title("Photosm videos or audio exchanged")
    plt.ylabel("Media number")

    plt.savefig("numberOfMedia.png")
    plt.close()


# ===============================================================================

def radialPlot(data):
    """
        Saves a radial plot of the proportion of messages sent each hour of the day
    """
    # group the data by user and hour of the day
    conversationHourly = data.groupby([data.index.hour, "name"]).size().reset_index()
    conversationHourly.columns = ["DateTime", "name", "sums"]
    # Each column is an hour, each cell the number of text sent
    conversationHourly = conversationHourly.pivot(index='name',
                                                  columns='DateTime',
                                                  values='sums').reset_index()

    # Transform the number of text sent to the proportion of text sent
    conversationHourly.columns = [str(name) for name in conversationHourly.columns]
    total = [column for column in conversationHourly.columns if column != "name"]
    proportions = conversationHourly[total].div(conversationHourly[total].sum(axis=1), axis=0)
    conversationHourly[total] = proportions

    # Set the ticks of the plot and the limits of the axis
    maxValue = conversationHourly[total].max().max()
    spacer = [round(number, 3) for number in np.linspace(0, maxValue, num=4)]

    # ------- PART 1: Create background

    # Number of variables
    categories = list(conversationHourly)[1:]
    N = len(categories)

    #   What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    #   Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    #   First axis on top
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(spacer, [str(number) for number in spacer], color="grey", size=7)
    plt.ylim(0, maxValue)

    # ------- PART 2: Add plots

    # Plot each individual = each line of the data
    # I don't do a loop, because plotting more than 3 groups makes the chart unreadable

    # Ind1
    values = conversationHourly.loc[0].drop('name').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1,
            linestyle='solid', label=conversationHourly["name"].iloc[0])
    ax.fill(angles, values, 'b', alpha=0.1)

    # Ind2
    values = conversationHourly.loc[1].drop('name').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1,
            linestyle='solid', label=conversationHourly["name"].iloc[1])
    ax.fill(angles, values, 'r', alpha=0.1)

    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.3, 0.1))
    plt.savefig("radialPlot.png")


# ===============================================================================
def WordCloudPlot(Data, mask=None):
    """
        Create a wordcloud from all the text sent. In given a ong image the wordcloud will have the image of the mask colored with words
    """

    def transform_format(val):
        if val == 0:
            return 255
        else:
            return val

    if mask != None:
        maskImage = np.array(Image.open(mask))
        maxWords = 50000
        maxFont = 10
    else:
        maskImage = None
        maxWords = 200
        maxFont = None

    txt = ' '.join(msg for msg in Data['msg'])

    wordcloud = WordCloud(width=1920, height=1080,
                          max_words=maxWords,
                          max_font_size=maxFont,
                          background_color="white",
                          mode='RGBA',
                          stopwords=stopWords,
                          mask=maskImage).generate(txt)
    if mask == None:
        plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
    else:
        img_colors = ImageColorGenerator(maskImage)
        plt.figure()
        plt.imshow(wordcloud.recolor(color_func=img_colors),
                   interpolation="bilinear")
    plt.axis("off")
    wordcloud.to_file("WhatsApp_WordCloud.png")

    plt.close()


# ===============================================================================

def createReport(data):
    f = open("report.txt", "w+")

    chatDayLength = data.index.max() - data.index.min()
    f.write("Average number of messages per day {}\n".format(round(chatDayLength.days / data.shape[0], 2)))

    numberOfChar = data.msg.apply(lambda x: len(x)).sum() / data.shape[0]
    f.write("Average letters per message {}\n".format(round(numberOfChar, 2)))

    numberOfwords = data.msg.apply(lambda x: len(x.split())).sum() / data.shape[0]
    f.write("Average words per message {}\n".format(round(numberOfwords, 2)))

    activeDay = data.resample("D").count()["msg"]
    f.write(
        "Most active day was {} with {} messages\n".format(activeDay.idxmax().strftime("%d-%b-%Y"), activeDay.max()))

    activeDay = data.resample("D").count()["msg"]

    startInactivity = None
    stopInactivity = None
    inactivityTime = 0
    previousDayActive = False
    endingList = [None, None, 0]
    for index, value in activeDay.items():
        if value == 0:
            # if day before active and current day inactive
            if previousDayActive:
                # start inactivity and reset end inactivity 
                startInactivity = index
                stopInactivity = None
                previousDayActive = False
            # if day before inactive and current day inactive
            else:
                # set end inactivity
                stopInactivity = index
            inactivityTime += 1
        else:
            if startInactivity != None and stopInactivity != None:
                if endingList[2] < inactivityTime:
                    endingList[0] = startInactivity
                    endingList[1] = stopInactivity
                    endingList[2] = inactivityTime

            startInactivity = None
            stopInactivity = None
            previousDayActive = True
            inactivityTime = 0

    f.write("Most inactive time:\n\tfrom {} to {}, duration: {} days".format(endingList[0].strftime("%d-%b-%Y"),
                                                                             endingList[1].strftime("%d-%b-%Y"),
                                                                             endingList[2]))
    f.close()


if __name__ == '__main__':
    args = parseArgouments()
    stopWords = stopwords.words(args.lang)

    log = args.log
    mask = args.mask

    go = time.time()
    conversationDF = dataManipulation(pd.DataFrame(wapp_parsing(log)))
    print("\nI'm calculating the number of messages for each month!")
    plotTotal(conversationDF)
    print("I'm calculating the message frequency for each hour of the day!")
    radialPlot(conversationDF)

    print("I'm creating the report!")
    createReport(conversationDF)

    conversationMedia, conversationNoMedia = separateMedia(conversationDF)
    print("I'm calculating how many media you shared!")
    plotMedia(conversationMedia)

    print("I'm making a wordcloud with your messages!")
    WordCloudPlot(conversationNoMedia, mask=mask)

    print("I'm calculating the mean message length!")
    conversationNoMedia = aggregateMonthName(conversationNoMedia)
    plotMeanMsgLength(conversationNoMedia)

    print("\nDone! execution time: {} seconds".format(round(time.time() - go)))
