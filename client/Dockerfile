
FROM cogment/cogment-py-sdk:v1.0.0-alpha1

ENV PYTHONPATH /app

# Uncomment following and set specific version if required for only this service
#ENV COGMENT_VERSION 0.3.0a5
RUN pip install /cogment-py-sdk
# Comment following if above is used
#ADD requirements.txt .
#RUN pip install -r requirements.txt

WORKDIR /app

ADD client .
ADD cog_settings.py .
ADD *_pb2.py .

CMD ["python", "client/main.py"]
