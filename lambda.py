import boto3


def lambda_handler(event, context):
    file_id = event["file_id"]
    access_token = event["access_token"]
    try:
        params = {"file_id": file_id, "access_token": access_token}

        print(params)

        client = boto3.client("ecs")

        response = client.run_task(
            cluster="test-firewall-cluster",
            launchType="FARGATE",
            taskDefinition="dropbox-video-processing-task-definition:2",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": [
                        "subnet-1",
                        "subnet-2",
                        "subnet-x",
                    ],
                    "assignPublicIp": "ENABLED",
                }
            },
            overrides={
                "taskRoleArn": "arn:aws:iam::<account_num>:role/ecsTaskRole-test-firewall",
                "containerOverrides": [
                    {
                        "name": "firewall-processor",
                        "environment": [
                            {"name": "FILE_ID", "value": file_id},
                            {"name": "ACCESS_TOKEN", "value": access_token},
                        ],
                    }
                ],
            },
        )

        print(response)
        return {
            "statusCode": 200,
            "body": f"File ID {file_id} is being processed from Dropbox.",
        }

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
