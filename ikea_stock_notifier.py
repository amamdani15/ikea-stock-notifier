import requests
import json
from datetime import datetime, time
from slack_webhook import Slack
import sys
from os.path import exists

slack = Slack(url='https://hooks.slack.com/services/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')
itemDesc = 'dresser'
storeIDs = ["399", "162", "167", "413", "166"]
db_file = f'db_{itemDesc}.json'
itemNo = '00103343'


def main():

    headers = {
        'authority': 'api.ingka.ikea.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'accept': 'application/json;version=2',
        'x-client-id': 'da465052-7912-43b2-82fa-9dc39cdccef8',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'origin': 'https://www.ikea.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.ikea.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('itemNos', f'{itemNo}'),
        ('expand', 'StoresList,Restocks'),
    )

    response = requests.get('https://api.ingka.ikea.com/cia/availabilities/ru/us', headers=headers, params=params)
    inventory = response.json()['availabilities']


    headers = {
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.ikea.com/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }

    response = requests.get('https://ww8.ikea.com/ext/iplugins/v2/en_US/data/localstorefinder/data.json', headers=headers)
    stores = response.json()

    # print(inventory)
    file_exists = exists(db_file)
    if not file_exists:
        db = {}
        with open(db_file, "w+") as f:
            json.dump(db, f)


    with open(db_file) as f:
        db = json.load(f)
    main_message = ''
    for sub_inventory in  inventory:
        storeCode = sub_inventory['classUnitKey']['classUnitCode']
        if storeCode in storeIDs:
            storelist = list(filter(lambda store: store['storeNumber'] == storeCode, stores))
            if storeCode in db:
                if sub_inventory['availableForCashCarry'] != db[storeCode]['cashCarry'] and sub_inventory['availableForCashCarry'] == True:
                    main_message += (f" found cashCarry inventory at {storelist[0]['storeCity']} of {itemDesc}\n")
                    db[storeCode]['cashCarry'] = sub_inventory['availableForCashCarry']
                if sub_inventory['availableForClickCollect'] != db[storeCode]['clickCollect'] and sub_inventory['availableForClickCollect'] == True:
                    main_message += (f"found clickCollect inventory at {storelist[0]['storeCity']} of {itemDesc}\n")
                    db[storeCode]['clickCollect'] = sub_inventory['availableForClickCollect']
                with open(db_file, "w") as f:
                    json.dump(db, f)

            else:
                db[storeCode] = {}
                db[storeCode]['cashCarry'] = False
                db[storeCode]['clickCollect'] = False
                with open(db_file, "w") as f:
                    json.dump(db, f)
    if main_message:
        slack.post(text=main_message)



    if is_time_between(time(00,5), time(00,15), datetime.now().time()) or 'test' in str(sys.argv):
        message = f'{itemDesc}: \n'
        for inventory in  inventory:
            storeCode = inventory['classUnitKey']['classUnitCode']
            if storeCode in storeIDs:
                storelist = list(filter(lambda store: store['storeNumber'] == storeCode, stores))
                stock = inventory['buyingOption']['cashCarry']['availability']['probability']['thisDay']['messageType']

                message += f"{storelist[0]['storeCity']}: currently {stock}. \n"
                if inventory['buyingOption']['cashCarry']['availability']['probability']['thisDay']['messageType'] == 'OUT_OF_STOCK':
                    if 'restocks' in inventory['buyingOption']['cashCarry']['availability']:
                        start_date = inventory['buyingOption']['cashCarry']['availability']['restocks'][0]['earliestDate']
                        end_date = inventory['buyingOption']['cashCarry']['availability']['restocks'][0]['latestDate']
                        quantity = inventory['buyingOption']['cashCarry']['availability']['restocks'][0]['quantity']
                        message += f"\t restock of {quantity} will be happening between {start_date} and {end_date}.\n"
                    else:
                        message += f"\t restock date unknown.\n"
        slack.post(text=message)


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


if __name__ == "__main__":
    main()