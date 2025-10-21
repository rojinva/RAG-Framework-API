import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Define environment and subscription
environ = os.getenv("ENVIRON", "dev")
keyvault_resource_name = f"kvlamuswoai{environ}eng01"
keyvault_url = f"https://{keyvault_resource_name}.vault.azure.net/"

print("environment:", environ)

# Authenticate to Azure
credential = DefaultAzureCredential()
client = SecretClient(vault_url=keyvault_url, credential=credential)

# Define the .env file location
ENV_FILE = ".env"
# Create or clear the .env file
with open(ENV_FILE, "w") as f:
    pass

# Function to fetch secret from Key Vault
def fetch_secret(secret_name):
    secret = client.get_secret(secret_name)
    return secret.value

# Read the .env.template file and process each line
with open(".env.template", "r") as template_file, open(ENV_FILE, "a") as env_file:
    for line in template_file:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            env_file.write(line + "\n")
            continue

        # Ensure the line contains an '=' character
        if "=" not in line:
            env_file.write(line + "\n")
            continue

        # Extract the variable name and value
        var_name, var_value = line.split("=", 1)

        # Check if the variable is sensitive
        if var_value.startswith("@keyvault$"):
            # Split the value to remove the prefix and fetch the secret from Key Vault
            _, secret_name = var_value.split("@keyvault$", 1)
            secret_value = fetch_secret(secret_name)
            env_file.write(f"{var_name}={secret_value}\n")
        else:
            # Add static variables to the .env file
            env_file.write(line + "\n")

print("Finished adding secrets to the .env file.")