"""
This is a system test for the project.
It will invoke the lambda function:
    dropbox-video-processing
and pass it the following event:
    {
        "file_id: "id:1234567890",
        "access_token": "1234567890"
    }
"""
import boto3
import json

access_token = ""
file_id = ""


def invoke_lambda():
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName="dropbox-video-processing",
        InvocationType="RequestResponse",
        Payload=json.dumps({"file_id": file_id, "access_token": access_token}),
    )
    return response


invoke_lambda()
