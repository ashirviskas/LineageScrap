from lxml import html
import requests
page = requests.get("https://download.lineageos.org/")
tree = html.fromstring(page.content)
for devicename in tree.xpath("//ul/li/div/ul/li/a/@href"): #selector.xpath()    #response.css('li.')
    print(devicename)
    page_device=requests.get("https://download.lineageos.org"+devicename)
    tree_device=html.fromstring(page_device.content)
    for date_device in tree_device.xpath("//table/tbody/tr/td[4]/text()"):
        print(date_device)