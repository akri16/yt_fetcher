FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./main /code/main
COPY ./run.py /code/run.py
ENTRYPOINT ["python", "run.py"]