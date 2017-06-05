#!/usr/bin/python3
# encoding=utf-8

import requests
from lxml import html
from pymongo import MongoClient, ReplaceOne
from datetime import datetime
from pprint import pprint

uri = open("database.config", "r").readline()
client = MongoClient("localhost")
Releases_col = client.LineageReleases.releases
Log_col = client.LineageReleases.log


def get_device_properties(device_name):
    device_properties = {}
    page = requests.get("https://download.lineageos.org" + device_name)
    tree = html.fromstring(page.content)
    device_properties['dates'] = tree.xpath("//table/tbody/tr/td[4]/text()")
    device_properties['links'] = tree.xpath("//table/tbody/tr/td[3]/a/@href")
    device_properties['md5sums'] = tree.xpath("//table/tbody/tr/td[3]/small/text()")
    device_properties['versions'] = tree.xpath("//table/tbody/tr/td[2]/text()")
    device_properties['types'] = tree.xpath("//table/tbody/tr/td[1]/text()")
    device_properties['changelogs'] = tree.xpath("//table/tbody/tr/td[5]/a/@href")
    return device_properties


def get_devicenames(address="https://download.lineageos.org/", device_xpath="//ul/li/div/ul/li/a/@href"):
    page = requests.get(address)
    tree = html.fromstring(page.content)
    devicenames = tree.xpath(device_xpath)
    return devicenames


def updatesert_device(device, device_properties):
    name = device[1:]
    replace_requests = []
    for i in range(len(device_properties['dates'])):
        device_ob = {}
        device_ob['device'] = name
        device_ob['released'] = datetime.strptime(device_properties['dates'][i], '%Y-%m-%d %H:%M:%S ')
        device_ob['link'] = device_properties['links'][i]
        device_ob['md5sum'] = device_properties['md5sums'][i]
        device_ob['version'] = device_properties['versions'][i]
        device_ob['type'] = device_properties['types'][i]
        device_ob['changelog_link'] = device_properties['changelogs'][i]
        replace_requests.append(ReplaceOne(device_ob, device_ob, upsert=True))
    result = Releases_col.bulk_write(replace_requests)
    return result


def update_all_devices():
    devicenames = get_devicenames()
    logs = {}
    for devicename in devicenames:
        device_properties = get_device_properties(devicename)
        # print(device_properties)
        result = updatesert_device(devicename, device_properties)
        Log_col.insert_one({'device': devicename[1:], 'date': datetime.now(), 'inserted': result.inserted_count,
                            'modified': result.modified_count, 'deleted': result.deleted_count,
                            'upserted': result.upserted_count})
    Log_col.insert_one(logs)

if __name__ == "__main__":
    update_all_devices()
