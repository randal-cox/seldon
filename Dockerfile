FROM openjdk:8u265-slim
COPY --from=python:3.8 / /

RUN mkdir -p /root/saved && touch /root/saved/log

WORKDIR /code

# copy the dependencies file to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip \
    && pip install awscli \
    && pip install -r requirements.txt \
    && wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/2.7.4/hadoop-aws-2.7.4.jar \
    && mv hadoop-aws-2.7.4.jar /usr/local/lib/python3.6/site-packages/pyspark/jars/ \
    && wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.7.4/aws-java-sdk-1.7.4.jar \
    && mv aws-java-sdk-1.7.4.jar /usr/local/lib/python3.6/site-packages/pyspark/jars/ \
    && apt-get update \
    && apt-get -y install apt-utils \
    && apt-get install nano


ENV SPARK_HOME=/usr/local/lib/python3.8/site-packages/pyspark


ENTRYPOINT [ "/code/bin/seldon" ]