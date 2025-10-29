import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",  # URL do seu container MinIO
    aws_access_key_id="minio",
    aws_secret_access_key="minio123",
    region_name="us-east-1",  # padrão usado pelo MinIO
)