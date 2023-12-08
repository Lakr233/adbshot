FROM python:latest

# install adb
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-fastboot \
    && rm -rf /var/lib/apt/lists/*

# set adh HOME to /adb/
ENV HOME /adb/

# copy files
COPY ./requirements.txt /app/
WORKDIR /app

# install python3 packages
RUN pip3 install -r requirements.txt

# now copy source code
COPY ./*.py /app/

# run python3 script
CMD ["python3", "main.py"]
EXPOSE 5650