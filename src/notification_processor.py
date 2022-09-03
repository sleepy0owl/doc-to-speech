import boto3

def handler(event, content):
    try:
        print(event)
    except Exception as e:
        print(e)