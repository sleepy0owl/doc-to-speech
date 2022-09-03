import os
import boto3

def handler(event, context):
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        s3_client = boto3.client('s3')

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=key
        )

        file_name = key.split('.')[0]
        data = response['Body'].read().decode('utf-8')

        polly_client = boto3.client('polly')

        output_bucket_name = os.environ.get('OUTPUTBUCKET')
        sns_topic_arn = os.environ.get('SNSTOPICARN')
        response = polly_client.start_speech_synthesis_task(
            Engine='standard',
            Text=data,
            OutputFormat="mp3",
            VoiceId="Joanna",
            SampleRate="16000",
            OutputS3BucketName=output_bucket_name,
            OutputS3KeyPrefix='audio/',
            SnsTopicArn=sns_topic_arn
        )
    except Exception as e:
        # write to sns topic
        print(e)
