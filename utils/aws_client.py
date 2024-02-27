"""
Connecting to AWS Services
Initial intention is to retrieve secrets from the Secret Manager
"""
import base64
import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name, region_name="us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=region_name
        )

    try:
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)

        # Check if the secret has a 'SecretString' or 'SecretBinary' field
        if "SecretString" in response:
            secret_value = response["SecretString"]
        else:
            # Decode base64-encoded secret binary
            secret_value = base64.b64decode(
                response["SecretBinary"]).decode("utf-8")

        return secret_value

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"The secret with name '{secret_name}' was not found.")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            print(f"Invalid request for the secret '{secret_name}'.")
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            print(f"Invalid parameter for the secret '{secret_name}'.")
        else:
            print(f"Error retrieving the secret '{secret_name}': {str(e)}")


secret_name = "your-secret-name"

# Call the function to retrieve the secret
secret_value = get_secret(secret_name)

# Use the retrieved secret value in your application
print(f"The secret value is: {secret_value}")
