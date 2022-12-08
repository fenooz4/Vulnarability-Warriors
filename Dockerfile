FROM python:3

RUN pip3 install boto3

RUN pip3 install requests

RUN pip3 install jsonlib

ADD test1.py / 

CMD [ "python", "./test1.py" ]
