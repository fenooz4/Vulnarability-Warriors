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

def lambda_handler(event, context):
    if event:
        instance =  DBupload()
        body = json.loads(event['body'])
        tasktype = body['tasktype']
        
        if tasktype  == "create":
            create_result =  instance.Create_data(body['data'])
            return create_result
        elif tasktype == "read":
            read_result =  instance.Read_data(body['data'])
            return read_result
        elif tasktype == "delete":
            delete_result =  instance.Delete_data(body['data'])
            return delete_result   
            
        else :
            return {
                'statusCode': '404',
                'body': 'Not found'
            }