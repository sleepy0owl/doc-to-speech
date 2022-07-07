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

        data = response['Body'].read().decode('utf-8')

        polly_client = boto3.client('polly')

        response = polly_client.synthesize_speech(
            Text=data,
            OutputFormat="mp3",
            VoiceId="Joanna",
            SampleRate="16000"
        )
        audio_stream = response['AudioStream'].read()
        with open(f'{key}-t2s.mp3', 'wb') as file:
            file.write(audio_stream)

        
    except Exception as e:
        # write to sns topic
        print(e)
