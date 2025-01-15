import boto3
import json
import os
import uuid
import sys
import face_recognition
from botocore.exceptions import ClientError
aws_access_key_id = 'AKIAQ3EGSSVX7X76NGOE'
aws_secret_access_key = '' #to be filled
aws_region = 'us-east-1'

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/058264294767/1229519982-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/058264294767/1229519982-resp-queue'

input_bucket = '1229519982-in-bucket'
output_bucket = '1229519982-out-bucket'

sqs = boto3.client('sqs', region_name=aws_region)
s3 = boto3.client('s3', region_name=aws_region)

def process_message(message):
    try:
        message_body = json.loads(message['Body'])
        original_filename = message_body.get('filename', 'unknown_filename')
        request_id = message_body.get('uuid')
        input_filename,result = run_face_recognition(original_filename)
        print("result=", input_filename)
        
        if result and result.strip():
            message= {
                'input_filename':input_filename,
                'result':result,
                'uuid' : request_id
            } 

            upload_to_s3(result, input_filename)
            send_response_to_queue(message)
        else:
            print("Invalid result. Not sending to the response queue.")

    except Exception as e:
        print(f"Error processing message: {str(e)}")

def run_face_recognition(input_filename):
    try:
        # Call the face_match function from face_recognition.py
        image_path = f'face_images_1000/{input_filename}'
        result = face_recognition.face_match(image_path, 'data.pt')
        print("result", result)
        if result:
            return input_filename,result[0]
        else:

            print("Error running face_recognition.py. Check the command and path.")
            return "Unknown"
        
    except Exception as e:
        print(f"Error running face_recognition.py: {str(e)}")
        return "Unknown"



def send_response_to_queue(message):
    try:
        response = sqs.send_message(QueueUrl=response_queue_url, MessageBody=json.dumps(message))
        print(f"sent response for {message.get('uuid')}")

    except Exception as e:
        print(f"Error sending response to queue: {str(e)}")

def upload_to_s3(result, filename):
    try:
        filename_without_extension = filename.split('.',1)[0]
        s3.put_object(Bucket=output_bucket, Key=filename_without_extension, Body=result.encode())
        print(f"Uploaded result for {filename_without_extension}")

    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")

def main():
    while True:
        try:
            request_message = sqs.receive_message(
                QueueUrl=request_queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )

            if 'Messages' in request_message and request_message['Messages']:
                print("recieved message:" )
                for message in request_message['Messages']:
                    process_message(message)
                    sqs.delete_message(QueueUrl=request_queue_url, ReceiptHandle=message['ReceiptHandle'])
                    
            else:
                print("No messages found in the queue.")

        except Exception as e:
            print(f"Error in main loop: {str(e)}")

if __name__ == "__main__":
    main()
        