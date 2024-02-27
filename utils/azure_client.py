"""
Connecting to Azure Services
Initial intention is to retrieve secrets from Key Vault
"""
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def get_secret(secret_name):
    """Getting a secret by name"""
    vault_url_prefix = os.getenv("vault_url_prefix")
    key_vault_url = f"https://{vault_url_prefix}.vault.azure.net/"

    # Use DefaultAzureCredential to authenticate
    credential = DefaultAzureCredential()
    secret_client = SecretClient(
        vault_url=key_vault_url, credential=credential
        )

    return secret_client.get_secret(secret_name).value

# Retrieve the secret
# secret_value = secret_client.get_secret(secret_name).value
