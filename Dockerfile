FROM python:3.9

COPY processing.py .
COPY yolov5s.pt .
COPY requirements.txt  .

RUN  apt-get update \
     && pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

ENTRYPOINT python processing.py \
    --file_id ${FILE_ID} \
    --access_token ${ACCESS_TOKEN}