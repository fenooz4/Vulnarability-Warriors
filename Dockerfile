FROM python:3

RUN pip3 install boto3

RUN pip3 install requests

ADD test1.py / 

CMD [ "python", "./test1.py" ]
