# pip install azure-storage-file-share
# pip install azure-identity

from azure.storage.fileshare import ShareFileClient
import os
from azure.identity import DefaultAzureCredential

service = ShareFileClient.from_connection_string(conn_str="https://hackathonfilesstorage.file.core.windows.net/DefaultEndpointsProtocol=https;AccountName=hackathonfilestorage;AccountKey=gdZHKPvMvlkDnpMcxMxu2diC/bRqvjptH7qJlbx5VI/95L/p6H932ZOTZwg5kuWbyUJ6Y8TCrh3nqIlyG+YD2g==;EndpointSuffix=core.windows.net", share_name="hackathon/Model_Package", file_path="aimanager.py")

with open("aimanager.py", "rb") as source_file:
    service.upload_file(source_file)


# with open("deployer2.log", "wb") as file_handle:
#     data = service.download_file()
#     data.readinto(file_handle)