FROM python:2.7-onbuild
ENV PYTHONPATH /usr/src/app
WORKDIR /app
ADD requirements.txt /app
RUN pip install --upgrade pip && pip install --requirement /app/requirements.txt
ADD producer.py /app
CMD ["python", "producer.py", "-p", "5672", "-s", "rabbitmq", "-m", "'Hello'", "-r", "30"]
