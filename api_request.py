# -*- coding: utf-8 -*-
import os 
import bottlenose
from BeautifulSoup import BeautifulSoup
import random
import time
from urllib2 import HTTPError
import boto3

ADV_API_AWS_ACCESS_KEY_ID=os.environ['ADV_API_AWS_ACCESS_KEY_ID']
ADV_API_AWS_SECRET_ACCESS_KEY=os.environ['ADV_API_AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ASSOCIATE_TAG=os.environ['AWS_ASSOCIATE_TAG']

TOPIC_ARN = 'arn:aws:sns:ap-northeast-1:517180089186:nintendo_switch_start_selling' # Mail
REGION = 'ap-northeast-1'

ITEM_ID='B01N5QLLT3' # Switch
TARGET_PRICE = 34000

def error_handler(err):
  ex = err['exception']
  if isinstance(ex, HTTPError) and ex.code == 503:
    time.sleep(random.expovariate(0.1))
    return True

def send_sms_message(store_url, price):
    sns = boto3.client('sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name = REGION
    )
    subject = 'Switch'
    message = '''
PRICE: {0}
Started selling nintendo switch!!! at {1}
        '''.format(price, store_url)
    print 'came here'
    response = sns.publish(
        TopicArn = TOPIC_ARN,
        Subject = subject,
        Message = message
    )
    return response


amazon = bottlenose.Amazon(ADV_API_AWS_ACCESS_KEY_ID, ADV_API_AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG,Region="JP",ErrorHandler=error_handler)
response = amazon.ItemLookup(
             ItemId=ITEM_ID,
             ResponseGroup="OfferSummary",
             ErrorHandler=error_handler)
soup = BeautifulSoup(response)
item = soup.find("item")

price = min([int(item.offersummary.lowestnewprice.amount.contents[0]), int(item.offersummary.lowestusedprice.amount.contents[0]), int(item.offersummary.lowestcollectibleprice.amount.contents[0])]) 
if price < TARGET_PRICE:
  #send sms
  send_sms_message('https://amazon.co.jp/dp/' + ITEM_ID, price)
