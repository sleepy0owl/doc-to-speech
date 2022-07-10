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

        response = polly_client.synthesize_speech(
            Text=data,
            OutputFormat="mp3",
            VoiceId="Joanna",
            SampleRate="16000"
        )
        audio_stream = response['AudioStream'].read()

        response = s3_client.put_object(
            Body=audio_stream,
            Bucket=bucket_name,
            Key=f"speech-{file_name}.mp3"
        )
    except Exception as e:
        # write to sns topic
        print(e)
