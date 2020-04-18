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
plt.style.use('seaborn-dark')

from os import path
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
from nltk.corpus import stopwords
stopWords = stopwords.words('italian')
stopWords.extend(["pi","poi","cosa","perch",
    "te","me","so","co","fatto","cos", "quando",
    "quindi", "si", "no"])


log = "./ChatWhatsApp.txt"


Data = {'Date&Time':[],
        'name':[],
        'msg':[]
       }
prev = ""
#=============================================================================
def wapp_split(line):
    """
    This Function splits each line of the log in a dictionary
    """
    if line.find(':',14)!=-1:
        splitted = line.split(' - ')
        Data['Date&Time'].append(splitted[0])
        splitted = splitted[1].split(':')
        Data['name'].append(splitted[0])
        Data['msg'].append(splitted[1][0:-1])
#=============================================================================
def wapp_parsing(file):
    """
    This function parses the log file avoiding non-text lines, and avoiding
    problems from messages sent by the same person in one minute
    """
    print("Loading... Parsing the file.")

    with open(file) as f:
        for line in f:

            if (len(line)!=0):
                if (line[0] in string.digits) and (line[1]in string.digits):

                    prev = line[0:line.find(':',15)+1]
                    wapp_split(line)
                else:

                    line = prev + line
                    wapp_split(line)
#=============================================================================
def BarPlotMonth(Data):
    """
    This function plots a barplot for the number of message sent for each
    month and the mean length of the messages for each month
    """

    fig,axes = plt.subplots(2,1,
            figsize=(18,10),
            sharex = True)



    group_by_month_per_user = Data.groupby([
        Data['Date&Time'].dt.strftime('%Y-%m'), 'name']
        ).count().unstack()

    group_by_month_per_user['msg_len'].plot(kind='bar',
            stacked=True,
            legend=['name'],
            ax = axes[0])
    axes[0].set_title('Number of text per month')
    axes[0].set_ylabel('Count')

    group_by_month_per_user = Data.groupby([
        Data['Date&Time'].dt.strftime('%Y-%m'), 'name']
        ).mean().unstack()

    group_by_month_per_user['msg_len'].plot(kind='bar',
            stacked=True,
            legend=['name'],
            ax = axes[1])
    axes[1].set_title('Mean lenght of a message per month')
    axes[1].set_ylabel('Mean lenght')
    axes[1].set_xlabel('Year-Month')

    axes[1].legend()

    plt.xticks(rotation=90)
    plt.savefig('WhatsApp_conversations.png')
    #plt.show()
#=============================================================================
def BarPlotPeople(Data):
    """
    This function plots the number of message set by each person and the mean
    length of each message wth errorbars
    """
    fig,axes = plt.subplots(2,1,
            figsize=(18,10),
            sharex = True)

    for i,j in Data.groupby('name'):
        axes[0].bar(i, j['msg_len'].count())
        axes[1].bar(i, j['msg_len'].mean())
    axes[0].set_ylabel('Number of message')
    axes[1].set_ylabel('Mean words for message')

    axes[0].set_title('Number of message for each person')
    axes[1].set_title('Mean message length (words number) for each person')

    plt.savefig('WhatsApp_people.png')
    #plt.show()
#=============================================================================
def WordCloudPlot(Data, mask = None):
    def transform_format(val):
        if val == 0:
            return 255
        else:
            return val

    if mask == None:
        maskImage = None
    else:
        maskImage = np.array(Image.open(mask))

    Data = Data[Data['msg'] != ' <Media omessi>']
    txt = ' '.join(msg for msg in Data['msg'])

    wordcloud = WordCloud(max_words=50000,
            max_font_size = 10,
            background_color="white",
            mode = 'RGBA',
            stopwords = stopWords,
            mask = maskImage).generate(txt)

    if mask == None:
        plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
    else:
        img_colors = ImageColorGenerator(maskImage)
        plt.figure()
        plt.imshow(wordcloud.recolor(color_func = img_colors), interpolation="bilinear")
    plt.axis("off")
    #plt.show()
    wordcloud.to_file("WhatsApp_WordCloud.png")
#=============================================================================
def BarPlotMedia(Data):
    """
    This function plots a barplot for the number of message sent for each
    month and the mean length of the messages for each month
    """

    fig,axes = plt.subplots(figsize=(18,10))



    group_by_month_per_user = Data.groupby([
        Data['Date&Time'].dt.strftime('%Y-%m'), 'name']
        ).count().unstack()

    group_by_month_per_user['msg'].plot(kind='bar',
            stacked=True,
            legend=['name'],
            ax = axes)
    axes.set_title('Number of media per month (Images, video or audio)')
    axes.set_ylabel('Count')
    axes.set_xlabel('Year-Month')

    axes.legend()

    plt.xticks(rotation=90)
    plt.savefig('WhatsApp_Media.png')
    #plt.show()
#=============================================================================


if __name__ == '__main__':
    # Pass the log to the parser

    wapp_parsing(log)

    # DataFrame creation

    Data = pd.DataFrame(Data)



    # DataFrame handling
    Data['Date&Time']=pd.to_datetime(Data['Date&Time'], dayfirst=True,
                                     infer_datetime_format=True)

    Data['msg_len'] = Data.msg.apply(lambda x: len(x.split()))

    print("Loading... Plot (1/4)")
    BarPlotMonth(Data)
    print("Loading... Plot (2/4)")
    BarPlotPeople(Data)
    print("Loading... Plot (3/4)")
    WordCloudPlot(Data, mask = './mask.png')

    OnlyMedia = Data[Data["msg"] == ' <Media omessi>']
    print("Loading... Plot (4/4)")
    BarPlotMedia(OnlyMedia)


    print('Done.')


