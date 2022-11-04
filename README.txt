Here is the initial code for the indexing of the IDs. This code also does the SSH into the instance.

To run the code, go into command prompt/terminal and type "python test.py ec2-44-202-235-11.compute-1.amazonaws.com" and make sure you have user.pem downloaded and in the same location (for the sake of convenience, I hard coded the user.pem to be in the ssh so that we would not have to also provide user.pem as an argument in the command line, but that will be changed in the final product since each ssh may have different keys). If you want to test on other instances, just change the command line argument to the address of that instance. 

There are comments in the code that does some explaining, but if you have any questions or concerns let me know