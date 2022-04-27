# Ikea Stock Notifier

The ikea stock notifier checks for avaliable stock of a certain item at Ikea and notifies you when it becomes available as well as the expected date it will become available. 

There are two example scripts provided, one for a nightstand and one for a dresser, adjust as you like. 

## How to Use
- set your slack webhook url at the top
- set a uniquie item description, this is both for the db and notificaitons
- Look up the store ID numbers in `Ikea Store Number List.txt` for the stores you would like to check and set them in the storeIDs list
- set the item number variable with the item number you are looking for

## Testing
- run `python3 ikea_stock_notifier.py test` to confirm that script runs and you receive a slack notificaiton

## Running

- create a cron job that runs every 10 minutes and logs to an output file, example on next line.
- ```*/10 * * * * python3 /Ikea/night_stand.py > /Ikea/log_night_stand.tx```

You will receive a notificaiton within 10 minutes of your item becoming available at one of the stores, and each night at 12:10am you will receive a summary notification which details which stores currently have it in stock and any delieveries that are scheulded for that specific item.


