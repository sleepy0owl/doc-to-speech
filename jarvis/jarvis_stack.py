from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
import aws_cdk
from constructs import Construct
from aws_cdk import aws_s3, aws_lambda, aws_lambda_event_sources, aws_iam, aws_sns, aws_sns_subscriptions

class JarvisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.STACKPREFIX = "jarvis"
        self.file_bucket = aws_s3.Bucket(self,
            id=f"{self.STACKPREFIX}-command-bucket",
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        self.sns_topic = aws_sns.Topic(self,
            id=f"{self.STACKPREFIX}-sns-long-audio-topic",
            display_name=f"{self.STACKPREFIX}-async-syth-topic",
        )
        
        self.sns_processor_lambda = aws_lambda.Function(self,
            id=f"{self.STACKPREFIX}-sns-processor-lambda",
            description="This lambda function processes notification that async speech syth sends to sns topic",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.AssetCode.from_asset('src'),
            handler="notification_processor.handler",
        )

        self.sns_topic.add_subscription(subscription=aws_sns_subscriptions.EmailSubscription(email_address='sourav.mondal@antstack.io'))
        self.sns_topic.add_subscription(subscription=aws_sns_subscriptions.LambdaSubscription(fn=self.sns_processor_lambda))
        
        self.text_processor_lambda = aws_lambda.Function(self,
            id=f"{self.STACKPREFIX}-text-processor",
            description="This Lambda function gets text file and converts the text to speech",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.AssetCode.from_asset('src'),
            handler='main.handler',
            environment={
                "OUTPUTBUCKET": self.file_bucket.bucket_name,
                "SNSTOPICARN": self.sns_topic.topic_arn
            }
        )

        self.text_processor_lambda.add_event_source(
            source=aws_lambda_event_sources.S3EventSource(
                bucket=self.file_bucket,
                events=[aws_s3.EventType.OBJECT_CREATED],
                filters=[aws_s3.NotificationKeyFilter(prefix='files/')]
            )
        )

        self.text_processor_lambda.add_to_role_policy(
            statement=aws_iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[f"{self.file_bucket.bucket_arn}/*"]
            )
        )

        self.text_processor_lambda.add_to_role_policy(
            statement=aws_iam.PolicyStatement(
                actions=[
                    "polly:SynthesizeSpeech",
                    "polly:StartSpeechSynthesisTask",
                    "polly:GetSpeechSynthesisTask",
                    "polly:ListSpeechSynthesisTasks"
                ],
                resources=["*"]
            )
        )

        self.text_processor_lambda.add_to_role_policy(
            statement=aws_iam.PolicyStatement(
                actions=['sns:Publish'],
                resources=[self.sns_topic.topic_arn]
            )
        )
