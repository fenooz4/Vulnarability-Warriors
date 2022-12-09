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
                'imageID' : event['imgID'],
                'name' : event['Name'],
                'ENV' : event['Env'],
                'Cmd' : event['Cmd'],
                'Volumes': event['Volumes'],
                'WorkingDir' : event['WorkingDir'],
                'EntryPoint' : event['EntryPoint'],
                'labels': event['labels'],
                'labelErrors': event['labelErrors']
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
        else :
            return {
                'statusCode': '404',
                'body': 'Not found'
            }