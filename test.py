import sys
from paramiko import SSHClient, AutoAddPolicy

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(sys.argv[1], username='ec2-user', key_filename='user.pem') #ssh into the instance given 
stdin, stdout, stderr = client.exec_command('docker container ls -q --no-trunc') #run command to get id of containers that already exist
out = stdout.read().decode("utf8") #read the output of the command and convert it into string since it is in bit format

ind = out.splitlines() #store the output in a list

#uncomment the line below to see if all of the ids are in the list
#print(ind) #print the list to see how the id's are stored

stdin, stdout, stderr = client.exec_command('docker images -a -q') #run command to get id of all images that already exist
out = stdout.read().decode("utf8") #read the output of the command and convert it into string since it is in bit format

img = out.splitlines() #store the output in a list

#uncomment to see if all the image ids are being stored correctly
#print(img) #this shows the list with the image ids

stdin, stdout, stderr = client.exec_command("docker events --filter 'type=container' --filter 'event=start' --format '{{.ID}}' --since '1h' --until '0s'") #run command that get id of new containers that started in the past hour (i can modify the time but this is just to test for now)
out = stdout.read().decode("utf8") 
ind = ind + out.splitlines() #add the output into the list

#uncomment to see if all the new container ids are being captured
#print(ind) #this prints the list so that we can see that it is storing the new id

#this does the same thing as above but with image id
stdin, stdout, stderr = client.exec_command("docker events --filter 'type=image' --filter 'event=start' --format '{{.ID}}' --since '1h' --until '0s'")
out = stdout.read().decode("utf8")
img = img + out.splitlines() #add the output into the list

#uncomment to see if all new image ids are captured
#print(img)

stdin.close()
stdout.close()
stderr.close()
client.close()
