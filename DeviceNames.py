from lxml import html
import requests
from pymongo import MongoClient
from pymongo import ReplaceOne
from datetime import datetime

uri = open("database.config", "r").readline()
client = MongoClient("localhost")
Releases_col = client.LineageReleases.releases
Log_col = client.LineageReleases.log


def get_device_dates(device_name):
    page_device = requests.get("https://download.lineageos.org" + device_name)
    tree_device = html.fromstring(page_device.content)
    dates_device = tree_device.xpath("//table/tbody/tr/td[4]/text()")
    return dates_device


def get_devices(address="https://download.lineageos.org/", device_xpath="//ul/li/div/ul/li/a/@href"):
    page = requests.get(address)
    tree = html.fromstring(page.content)
    devicenames = tree.xpath(device_xpath)
    return devicenames


def updatesert_device(device, dates_s):
    name = device[1:]
    requests = []
    for date_s in dates_s:
        device_ob = {}
        device_ob['device'] = name
        device_ob['released'] = datetime.strptime(date_s, '%Y-%m-%d %H:%M:%S ')
        requests.append(ReplaceOne(device_ob, device_ob, upsert=True))
    result = Releases_col.bulk_write(requests)
    return result


def update_all_devices():
    devices = get_devices()
    logs = {}
    for device in devices:
        dates = get_device_dates(device)
        result = updatesert_device(device, dates)
        logs[device] = {'date': datetime.now(), 'inserted': result.inserted_count, 'modified': result.modified_count, 'deleted': result.deleted_count}
    Log_col.insert_one(logs)

if __name__ == "__main__":
    update_all_devices()
