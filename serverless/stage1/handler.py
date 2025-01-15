import urllib.parse
import boto3
from video_splitting_cmdline import video_splitting_cmdline
import os
import json

def handler(event, context):
    try:
        print("entered handler")
        inputBucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        videoFilePath = '/tmp/{}'.format(key)

        s3 = boto3.client('s3')
        s3.download_file(inputBucket, key, videoFilePath)
        
        # Changing directory to /tmp for processing
        os.chdir('/tmp')
        
        # Processing the video
        outFilePath = video_splitting_cmdline(videoFilePath)
        print("outFilePath", outFilePath)
        
        # Uploading the output .jpg file to S3
        uploadToS3(outFilePath, "1229519982-stage-1")

        print("os.path.basename(outFilePath)", os.path.basename(outFilePath))

        invoke_lambda("1229519982-stage-1", os.path.basename(outFilePath))

        print("Video processing complete! File uploaded to 1229519982-stage-1")
        
        # Cleaning up temporary files
        os.remove(videoFilePath)
        os.remove(outFilePath)
        
        return {
            'statusCode': 200,
            'body': 'Video frames upload|ed.'
        }
    except Exception as e: 
        print(e)


def invoke_lambda(bucket_name, image_key):
    lambdaClient = boto3.client('lambda')
    payload = {"Records": [{"s3": {"bucket": {"name": bucket_name}, "object": {"key": image_key}}}]}

    # Invoking the face recognition lambda
    response = lambdaClient.invoke(
        FunctionName='arn:aws:lambda:us-east-1:730335656599:function:face-recognition',
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    print(response) 


def uploadToS3(outputFilePath, outputBucket):
    s3 = boto3.client('s3')
    s3_object_key = os.path.basename(outputFilePath)
    s3.upload_file(outputFilePath, outputBucket, s3_object_key)
    print(f"Uploaded: {s3_object_key}")
