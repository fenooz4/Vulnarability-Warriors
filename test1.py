import sys
import subprocess
import os
import threading
import re
import boto3
import requests
import json

containerPat = re.compile(r"^[a-z0-9]{64}")
Images = []  # list to store all the image objects
Containers = []  # list to store all the container objects
Commands = ['docker events --filter type=container --filter event=start --format {{.ID}}',
            'docker events --filter type=image --filter "event=pull"']
APIEndpoint = 'https://wo1kim4ak9.execute-api.us-east-1.amazonaws.com/prod/dbuploader'                         # REPLACE WITH APIENDPOINT URL
APIKEY = {'x-api-key' : '9L4NLcZOLMh8nI5ESocc5V7rTa0jnv23KcaOlEHa'}              # REPLACE WITH API KEY

# obtains AWS instanceID, and IP addresses, uncomment when uploading to AWS, cannot obtain when running locally
# out = subprocess.run(['ec2-metadata', '-i'], stdout = subprocess.PIPE) #get the labels for the current docker image
# out = out.stdout.decode("utf-8")
# localip = subprocess.run(['ec2-metadata', '--local-ipv4'], stdout = subprocess.PIPE)
# localip = localip.stdout.decode("utf-8")
# publicip = subprocess.run(['ec2-metadata', '--public-ipv4'], stdout = subprocess.PIPE)
# publicip = publicip.stdout.decode("utf-8")
# instance = out.split(':')
# AWSinstanceID = instance[1]
# print(AWSinstanceID)

# DockerImage object that stores the information for docker images
class DockerImage:
    id = ''
    imgId = ''
    Name = ''
    Env = ''
    Cmd = ''
    Volumes = ''
    WorkingDir = ''
    EntryPoint = ''
    

    def __init__(i):
        i.labelTypes = []
        i.labelNames = []
        i.labelErrors = []

    def addLabel(i, l, l2):
        i.labelTypes.append(l)
        i.labelNames.append(l2)


# can add various other information to this

# DockerContainer object that stores the information for docker containers
class DockerContainer:
    id = ''
    imgId = ''

    def __init__(i):
        i.labelTypes = []
        i.labelNames = []

    def addLabel(i, l, l2):
        i.labelTypes.append(l)
        i.labelNames.append(l2)


# can add various other information to this


# function used to compare labels of a container to labels of an image
def labelCompare(c):
    for i in Images:  # for every image
        if c.imgID == i.imgID:  # compare container's imageID to the imageID to find a match
            j = 0
            k = 0
            # iterative nested loop, loops through every labelType in the image and every labelType in the container
            # if the labelTypes are equal, then it compares the labelNames
            while j < len(i.labelTypes):
                while k < len(c.labelTypes):
                    if i.labelTypes[j] == c.labelTypes[k]:
                        if i.labelNames[j] != c.labelNames[k]:
                             i.labelErrors.append(i.labelTypes[j])#appends label type error to the image's label errors

                    k += 1
                j += 1
        imagedata = {}
        imagebody = {'body':{}}
        imagebody['body']['tasktype'] = 'create'
        imagedata['id'] = i.id
        imagedata['imgID'] = i.imgID
        imagedata['Name'] = i.Name
        imagedata['Env'] = i.Env
        imagedata['Cmd'] = i.Cmd
        imagedata['Volumes'] = i.Volumes
        imagedata['WorkingDir'] = i.WorkingDir
        imagedata['EntryPoint'] = i.EntryPoint
        imagebody['body']['data'] = imagedata
        imagejson = json.loads(json.dumps(imagebody))
        print(imagejson)
        postrequest = requests.post(APIEndpoint, headers=APIKEY, json=imagejson)


# function used to obtain labels from containers and images
def obtainLabels(c):
    outLbl = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.Labels}}"', c.id],
                            stdout=subprocess.PIPE)  # get the labels for the current docker image
    outLbl = outLbl.stdout.decode("utf-8")
    outLbl = outLbl.replace("{", '')
    outLbl = outLbl.replace("}", '')
    dockerLbls = outLbl.split(',')  # splits each label
    # print(dockerLbls)
    # categorizes the label into labelType and labelName and adds them to their respective lists
    for label in dockerLbls:
        label = label.strip()
        line = label.split(':')
        if len(line) > 1:
            c.addLabel(line[0], line[1])


# parses docker image information
def parseDockerImages(img):
    img = img.strip()
    i = DockerImage()  # creates new docker image object
    i.id = img  # sets id for the image object to the img id
    #i.Name = name #sets name for the image object to the img name
    outID = subprocess.run(['docker', 'inspect', '-f', '{{.ID}}', img], stdout=subprocess.PIPE)
    outID = outID.stdout.decode("utf-8")
    outID = outID.strip()
    line = outID.split(":")
    i.imgID = line[1]
    obtainLabels(i)  # obtains the labels for the image
    obtainVals(i)  #obtains various extraneous docker image information and applies 
    Images.append(i)  # adds docker image object to the docker image list



# parses docker container information
def parseDockerContainers(container):
    container = container.strip()
    c = DockerContainer()
    c.id = container  # sets container id to current container
    outID = subprocess.run(['docker', 'inspect', '-f', '{{.Image}}', container],
                           stdout=subprocess.PIPE)  # runs inspect on the current container to obtain the associated 64-char image ID
    outID = outID.stdout.decode("utf-8")
    outID = outID.strip()
    line = outID.split(":")
    # print(line)
    c.imgID = line[1]
    obtainLabels(c)  # obtains the labels for the container
    Containers.append(c)  # adds container to the container list
    labelCompare(c)  # compares labels for the container to its associated image


def obtainVals(i):
    # used to obtain various extraneous values for docker images
    env = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.Env}}"', i.id], stdout = subprocess.PIPE)
    i.Env = env.stdout.decode("utf-8").strip()
    cmd = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.Cmd}}"', i.id], stdout = subprocess.PIPE)
    i.Cmd = cmd.stdout.decode("utf-8").strip()
    volumes = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.Volumes}}"', i.id], stdout = subprocess.PIPE)
    i.Volumes = volumes.stdout.decode("utf-8").strip()
    workingDir = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.WorkingDir}}"', i.id], stdout = subprocess.PIPE)
    i.WorkingDir = workingDir.stdout.decode("utf-8").strip()
    entrypoint = subprocess.run(['docker', 'inspect', '-f', '"{{json .Config.Entrypoint}}"', i.id], stdout = subprocess.PIPE)
    i.EntryPoint = entrypoint.stdout.decode("utf-8").strip()


# monitors container events (currently does not work if imageEvents is running)
def containerEvents(std_outline):
    dockerContainers = std_outline
    dockerContainers = dockerContainers.strip()
    #print(dockerContainers)
    parseDockerContainers(dockerContainers)


# monitors image events (currently terminates program when images are removed from system for some reason)
def imageEvents(std_outline):
    # need to obtain the image name since the docker events command does not output the image ID on pull
    dockerImg = std_outline
    # print(dockerImg)
    dockerImg = dockerImg.strip()
    dockerSplit = dockerImg.split('name=')
    dockerName = dockerSplit[1]
    dockerName = dockerName[:-1]
    # print(dockerName)
    # obtains the docker image ID from the specified name
    outID = subprocess.run(['docker', 'inspect', dockerName, '-f', '{{.ID}}'], stdout=subprocess.PIPE)
    outID = outID.stdout.decode("utf-8")
    outID = outID.strip()
    # print("Test or something: " + outID)
    line = outID.split(":")
    if (dockerImg != '' and outID != ''):
        # print(line[1])
        parseDockerImages(line[1])  # parses the docker image based on its ID


# start imageEvents and containerEvents and read lines and parse them accordingly
def eventReader():
    processes = [subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True) for cmd in Commands]
    for std_outline in iter(processes[0].stdout.readline, ""):
        if re.match(containerPat, std_outline):
            #print("container")
            containerEvents(std_outline)
        else:
            #print("image")
            imageEvents(std_outline)
    for p in processes: p.wait()
    

# obtains a list of all running and previously ran docker container IDs and adds them to the dockerContainer list
out = subprocess.run(['docker', 'container', 'ls', '-a', '-q', '--no-trunc'],
                     stdout=subprocess.PIPE)  # runs the command line prompt
out = out.stdout.decode("utf-8")  # decodes output
dockerContainers = out.splitlines()  # store the output in a list

# obtains a list of docker image IDs and adds them to the dockerImage list
out = subprocess.run(['docker', 'images', '-q'],
                     stdout=subprocess.PIPE)  # runs command line prompt
out = out.stdout.decode("utf-8")  # decodes output
dockerImgs = out.splitlines()  # store the output in a list

# loop through each found docker image ID, create an Images object for that ID and add the various information to that object
for img in dockerImgs:
    parseDockerImages(img)

# loop and docker inspect each container
for container in dockerContainers:
    parseDockerContainers(container)


def main(_):
    # currently these cannot run simultaneously, need to figure out issue
    #imageEvents()
    #containerEvents()
    eventReader()



if __name__ == "__main__":
    main(sys.argv[1:])
