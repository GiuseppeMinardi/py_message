from bs4 import BeautifulSoup
from lxml import etree

with open("./message_1.html") as ig_conv:
    soup = BeautifulSoup(ig_conv, "html.parser")
    conversation = soup.find("div", {"class": "_4t5n"})
    messages = conversation.findChildren()
    for message in messages:
        name = message.find("div", {"class": "_3-95 _2pim _2lek _2lel"})
        text = message.find("div", {"class": "_3-95 _2let"})
        date = message.find("div", {"class": "_3-94 _2lem"})
        print(date, name)
