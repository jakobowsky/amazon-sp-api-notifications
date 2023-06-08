import requests
from datetime import datetime, timedelta, date
import time
from typing import List
from sp_api.api import Orders, Sales, Products, Inventories, Catalog, CatalogItems, Sellers, Reports, Notifications, ListingsItems, ProductFees
from sp_api.base import Marketplaces, Granularity, ReportType, ProcessingStatus
from sp_api.api import Notifications
import json
from pprint import pprint
import csv
import seaborn
import boto3



###### SETUP ################################
q_arn = 'arn:aws:sqs:us-east-1:XXXXX'
q_url = 'https://sqs.us-east-1.amazonaws.com/XXXXX'


secrets = 'keys.json'
with open(secrets) as f:
    KEYS = json.loads(f.read())

def get_secret(setting) -> List[any]:
    try:
        return KEYS[setting]
    except KeyError:
        msg = 'Set the {} environment variable'.format(setting)
        raise KeyError(msg)

LWA_APP_ID = get_secret('lwa_app_id')
LWA_CLIENT_SECRET = get_secret('lwa_client_secret')
AWS_SECRET_KEY = get_secret('aws_secret_key')
AWS_ACCESS_KEY = get_secret('aws_access_key')
ROLE_ARN = get_secret('role_arn')
CLIENT_REFRESH_TOKEN = get_secret('clients_refresh_token')
credentials=dict(
        refresh_token=CLIENT_REFRESH_TOKEN,
        lwa_app_id=LWA_APP_ID,
        lwa_client_secret=LWA_CLIENT_SECRET,
        aws_secret_key=AWS_SECRET_KEY,
        aws_access_key=AWS_ACCESS_KEY,
        role_arn=ROLE_ARN,
    )

######################



######## NOTIFICATIONS ##########
notifications_client = Notifications(
    credentials=credentials,
    marketplace=Marketplaces.PL,
)
print("Creating a new SQS destination")
sqs_destination_response = notifications_client.create_destination(
    name="sp-api-destination",
    arn=q_arn,
)
print(sqs_destination_response)
sqs_dest_id = sqs_destination_response.destinationId

print("SQS destination id: "+sqs_dest_id)


sqs_notification_types = [
    "ACCOUNT_STATUS_CHANGED",
    "ANY_OFFER_CHANGED",
    "B2B_ANY_OFFER_CHANGED",
    "FBA_INVENTORY_AVAILABILITY_CHANGES",
    "FBA_OUTBOUND_SHIPMENT_STATUS",
    "FEE_PROMOTION",
    "FEED_PROCESSING_FINISHED",
    "FULFILLMENT_ORDER_STATUS",
    "MFN_ORDER_STATUS_CHANGE",
    "ORDER_STATUS_CHANGE",
    "PRICING_HEALTH",
    "REPORT_PROCESSING_FINISHED",
]



for sqs_notification_type in sqs_notification_types:
    print('----------')
    print(sqs_notification_type)
    try:
        sqs_subscription_response = notifications_client.create_subscription(
                sqs_notification_type, destination_id=sqs_dest_id
            )
        print(sqs_notification_type)
        print(sqs_subscription_response)
    except Exception as e:
        pass


############################################



##### REPORTS ###########
print("Reports API start...")
report_type = ReportType.GET_MERCHANT_LISTINGS_ALL_DATA
res = Reports(credentials=credentials, marketplace=Marketplaces.PL)
data = res.create_report(reportType=report_type)
report = data.payload
data = res.get_report(report['reportId'])
data.payload



sqs = boto3.client(
    "sqs",
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# Receive message from SQS queue
response = sqs.receive_message(
    QueueUrl=q_url,
    AttributeNames=["All"],
    MaxNumberOfMessages=1,
    MessageAttributeNames=["All"],
    VisibilityTimeout=0,
    WaitTimeSeconds=0,
)



for i in response['Messages']:
    print(i)
    print('')


############################################