import boto3
import json

def lambda_handler(event,context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('labels')
    
    iid=event["id"]
    imageid = event["imageid"]
    labelnames = event["labelnames"]
    labeltypes=event["labeltypes"]
    
    response = table.put_item(
        Item={
            "id":iid,
            "imageid":imageid,
            "labeltypes":labeltypes,
            "labelnames":labelnames
        }
    )
    
    return response