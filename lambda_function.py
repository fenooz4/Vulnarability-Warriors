import boto3
import json

class DBupload:
    
    def __init__(self):
        client = boto3.resource('dynamodb')
        self.table=client.Table('labels')
        
    def Create_data(self,event):
        response=self.table.put_item(
            Item={
                'instanceID' : event['id'],
                'imageID' : event['imageid'],
                'labels' : event['labels']
            }
        )
        return{
            'statusCode' : response['ResponseMetadata']['HTTPStatusCode'],
            'body' : 'Record ' + event['id'] + ' added'
        }
         
    def  Read_data(self , event):
        response = self.table.get_item(
            Key={
                'instanceID': event['id']
            }
        )
        if 'Item' in response:
            return response['Item']
        else:
            return {
                'statusCode': '404',
                'body': 'Not found'
            }     
            
    def  Delete_data(self , event):
        response = self.table.delete_item(
            Key={
                'instanceID': event['id']
            }
        )
        return {
                'statusCode': '200',
                'body': 'Deleted the item with id :' + event['id']
            }

def lambda_handler(event, context):
    if event:
        instance =  DBupload()
        if event['tasktype']  == "create":
            create_result =  instance.Create_data(event['data'])
            return create_result
        elif event['tasktype']  == "read":
            read_result =  instance.Read_data(event['data'])
            return read_result
        elif event['tasktype']  == "delete":
            delete_result =  instance.Delete_data(event['data'])
            return delete_result
        else :
            return {
                'statusCode': '404',
                'body': 'Not found'
            }