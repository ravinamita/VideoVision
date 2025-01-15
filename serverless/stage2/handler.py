#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import boto3
import os
import json
import urllib.parse
from face_recognition_code import face_recognition_function

def handler(event, context):
    try:
        print("entered face-recog handler")
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        
        image_file_path = f"/tmp/{key}"
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, key, image_file_path)
        
        # Calling the face recognition function
        recognized_name = face_recognition_function(image_file_path)
        print("recognized_name", recognized_name)
        
        # Saving the recognized name in a .txt file
        output_file = os.path.splitext(key)[0] + ".txt"
        save_path = "/tmp/"+ output_file
        with open(save_path, 'w+') as f:
            f.write(recognized_name)

        # Uploading the result to the output bucket
        s3.upload_file(save_path, "1229519982-output", output_file)

        return {
            'statusCode': 200,
            'body': 'Face recognition completed successfully.'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Face recognition failed.'
        }