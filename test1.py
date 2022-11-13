import sys
import os
import time
import boto3
import awscli
from paramiko import SSHClient, AutoAddPolicy


Images = [] #list to store all the image objects
Containers = [] #list to store all the container objects

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(sys.argv[1], username='ec2-user', key_filename='user.pem') #ssh into the instance given 

#obtains AWS instanceID
stdin, stdout, stderr = client.exec_command('ec2-metadata -i')  
out = stdout.read().decode("utf-8")
instance = out.split(':')
AWSinstanceID = instance[1]
#print(AWSinstanceID)  

#DynamoDB init
tablename = "labels"
pKey_name = 'instanceID'
pKey = 0
columns = ["imageID","Label Types", "Label Names", "isDuplicate"]
client = boto3.client('dynamodb')
db = boto3.resource('dynamodb')
table = db.Table(tablename)

#Dynamo DB create table
def create_table():
    table = client.create_table(
		tablename = 'labels',
  		KeySchema=[
	  		{
		  		'AttributeName' : 'instanceID',
				'KeyType': 'HASH'
	  		},
     		{
				'AttributeName' : 'imageID',
				'KeyType' : 'RANGE'
	 		},
    	],
		AttributeDefinitions = [
			{
				'AttributeName' : 'instanceID',
				'AttributeType' : 'S'
			},
			{
				'AttributeName' : 'imageID',
				'AttributeType' : 'S'
			},
		],
		ProvisionedThroughput = {
			'ReadCapacityUnits' : 5,
			'WriteCapacityUnits' : 5
		}
	)    
    

#DockerImage object that stores the information for docker images
class DockerImage:
	id = ''
	imgId = ''
	def __init__(i):
		i.labelTypes = []
		i.labelNames = []
		
	def addLabel(i, l, l2):
		i.labelTypes.append(l)
		i.labelNames.append(l2)
	#can add various other information to this

#DockerContainer object that stores the information for docker containers
class DockerContainer:
	id = ''
	imgId = ''
	def __init__(i):
		i.labelTypes = []
		i.labelNames = []
	def addLabel(i, l, l2):
		i.labelTypes.append(l)
		i.labelNames.append(l2)
		#can add various other information to this

#function used to compare labels of a container to labels of an image
def labelCompare(c):
	for i in Images: #for every image 
		if c.imgID == i.imgID: #compare container's imageID to the imageID to find a match
			j=0
			k=0
			#iterative nested loop, loops through every labelType in the image and every labelType in the container
			#if the labelTypes are equal, then it compares the labelNames 
			while j < len(i.labelTypes):
				while k < len(c.labelTypes):
					if i.labelTypes[j] == c.labelTypes[k]:
						if i.labelNames[j] == c.labelNames[k]:
							print(i.labelNames[j] +", "+c.labelNames[k]) #outputs the label names of the image and the container if they match
							
					k+=1
				j+=1
				
#function used to obtain labels from containers and images				
def obtainLabels(c):
	stdin, stdout, stderr = client.exec_command('docker inspect -f "{{json .Config.Labels}}" ' +c.id) #get the labels for the current docker image
	outLbl = stdout.read().decode("utf-8")
	outLbl = outLbl.replace("{", '')
	outLbl = outLbl.replace("}", '')
	dockerLbls = outLbl.split(',')#splits each label
	#print(dockerLbls)
	#categorizes the label into labelType and labelName and adds them to their respective lists
	for label in dockerLbls:
		label = label.strip()
		line = label.split(':')
		if len(line) > 1:
			c.addLabel(line[0], line[1])


def parseDockerImages(img):
	img = img.strip()
	i = DockerImage()
	i.id = img
	stdin, stdout, stderr = client.exec_command('docker inspect -f "{{.ID}}" ' +img) #adds 64 character imageID to image object
	outID = stdout.read().decode("utf-8")
	outID = outID.strip()
	line = outID.split(":")
	i.imgID = line[1]
	obtainLabels(i)
	Images.append(i)
	
def parseDockerContainers(container):
	container = container.strip()
	c = DockerContainer()
	c.id = container
	stdin, stdout, stderr = client.exec_command('docker inspect -f "{{.Image}}" ' +container) #adds 64 character imageID to container object
	outID = stdout.read().decode("utf-8")
	outID = outID.strip()
	line = outID.split(":")
	c.imgID = line[1]
	obtainLabels(c)
	#print(c.imgID)
	#add label names to docker label name list
	Containers.append(c)
	labelCompare(c)

def obtainVals(i):
	#used to obtain various values for images
	print(i)

#monitors container events
def containerEvents():
	stdin, stdout, stderr = client.exec_command("docker events --filter 'type=container' --filter 'event=start' --format '{{.ID}}' --since '0.5s' --until '0s'") #run command that get id of new containers that started in the past hour (i can modify the time but this is just to test for now)
	out = stdout.read().decode("utf8") 
	dockerContainers = out.splitlines() #add the output into the list
	if dockerContainers != []:
		print(dockerContainers)
		for container in dockerContainers:
			parseDockerContainers(container)	

#monitors image events	
def imageEvents():
	stdin, stdout, stderr = client.exec_command("docker events --filter 'type=image' --filter 'event=start' --format '{{.ID}}' --since '0.5s' --until '0s'")
	out = stdout.read().decode("utf8")
	dockerImgs = out.splitlines() #add the output into the list
	for img in dockerImgs:
		parseDockerImages(img, Images)
	
stdin, stdout, stderr = client.exec_command('docker container ls -a -q --no-trunc') #run command to get id of containers that already exist
out = stdout.read().decode("utf8") #read the output of the command and convert it into string since it is in bit format
dockerContainers = out.splitlines() #store the output in a list



    
# DynamoDB put function   
def dbupload(c):
    for i in Images:
        pKey = AWSinstanceID
        j = 0
        while j < len(i.labelTypes):
            response = table.putitem(
			Item = {
				pKey_name:pKey,
				columns[0]:	i.imageID,
				columns[1][j]: i.labelTypes[j],
				columns[2][j]: i.labelNames[j],   
			}
			)
        





#uncomment the line below to see if all of the ids are in the list
#print(ind) #print the list to see how the id's are stored

stdin, stdout, stderr = client.exec_command('docker images -a -q') #run command to get id of all images that already exist
out = stdout.read().decode("utf8") #read the output of the command and convert it into string since it is in bit format
dockerImgs = out.splitlines() #store the output in a list

#uncomment to see if all the image ids are being stored correctly
#print(dockerImgs) #this shows the list with the image ids

#uncomment to see if all the new container ids are being captured
#print(dockerContainers) #this prints the list so that we can see that it is storing the new id

#uncomment to see if all new image ids are captured
#print(dockerImgs)


#loop through each found docker image ID, create an Images object for that ID and add the various information to that object
for img in dockerImgs:
	parseDockerImages(img)
	

#loop and docker inspect each container
for container in dockerContainers:
	parseDockerContainers(container)


#monitors docker events every minute
def main(_):
	while True:
		imageEvents()
		containerEvents()
		#time.sleep(1)
		
if __name__=="__main__":
    main(sys.argv[1:])

stdin.close()
stdout.close()
stderr.close()
client.close()


