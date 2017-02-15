"""
  This script will go to www.nasdaqtrader.com website and
  fetch all the multicast groups, multicast sources, source ports,
  and their descriptions in a tabular format so you can run custom scripts on 
  that data.
"""

import urllib
import urllib.request
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import requests

url = 'http://www.nasdaqtrader.com/Trader.aspx?id=FeedMIPs'
def make_soup(url):
    page = urllib.request.urlopen(url)
    soupdata = BeautifulSoup(page, "html.parser")
    #print(soupdata)  <---  this will print in HTML format
    return soupdata

soup = make_soup(url)
multicast_data = []
for record in soup.findAll('tr'):
    tds = record.findAll('td')
    if len(tds)>=5:
        #print("Site: %s, Channel Purpose: %s, Group: %s, Port: %s, Source IP Address: %s\n" % \
        #      (tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text))
        multicast_data.append([tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text])
table = PrettyTable(["Site","Channel Purpose","Group","Port","Source IP Address"])
for items in multicast_data:
    table.add_row(items)
    #print(items)
print (table)
