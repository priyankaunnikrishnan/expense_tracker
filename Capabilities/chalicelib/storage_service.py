import boto3

class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location

    def get_storage_location(self):
        return self.bucket_name

    def upload_file(self, file_bytes, file_name):
        self.client.put_object(Bucket=self.bucket_name,
                               Body=file_bytes,
                               Key=file_name)

        return {'fileId': file_name,
                'fileUrl': "http://" + self.bucket_name + ".s3.amazonaws.com/" + file_name}

    def read_text_file(self, file_name):
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_name)
            text_content = response['Body'].read().decode('utf-8')  # Decoding the byte stream to string
            return text_content
        except Exception as e:
            print(f"Error reading file {file_name}: {e}")
            return None
