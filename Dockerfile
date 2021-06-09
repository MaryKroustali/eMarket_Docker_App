FROM ubuntu:18.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install flask pymongo
RUN mkdir /final
RUN mkdir -p /final/data
COPY appFinal.py /final/appFinal.py
ADD data /final/data
EXPOSE 5000
WORKDIR /final
ENTRYPOINT [ "python3","-u","appFinal.py" ]

