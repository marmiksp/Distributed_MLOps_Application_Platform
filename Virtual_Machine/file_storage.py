# pip install azure-storage-file-share
# pip install azure-identity

from azure.storage.fileshare import ShareFileClient
import os
from azure.identity import DefaultAzureCredential


def upload_file(file_name, file_path):
    service = ShareFileClient.from_connection_string(
        conn_str="https://hackathonfilesstorage.file.core.windows.net/DefaultEndpointsProtocol=https;AccountName=hackathonfilestorage;AccountKey=gdZHKPvMvlkDnpMcxMxu2diC/bRqvjptH7qJlbx5VI/95L/p6H932ZOTZwg5kuWbyUJ6Y8TCrh3nqIlyG+YD2g==;EndpointSuffix=core.windows.net",
        share_name="hackathon/Applications_Docker_Image",
        file_path=file_name
    )
    print(file_path)
    with open(file_path, "rb") as source_file:
        service.upload_file(source_file)


def download_file(file_name, file):
    service = ShareFileClient.from_connection_string(
        conn_str="https://hackathonfilesstorage.file.core.windows.net/DefaultEndpointsProtocol=https;AccountName=hackathonfilestorage;AccountKey=gdZHKPvMvlkDnpMcxMxu2diC/bRqvjptH7qJlbx5VI/95L/p6H932ZOTZwg5kuWbyUJ6Y8TCrh3nqIlyG+YD2g==;EndpointSuffix=core.windows.net",
        share_name="hackathon/Applications_Docker_Image", 
        file_path=file_name
    )

    with open(file, "wb") as source_file:
        data = service.download_file()
        data.readinto(source_file)



# with open("deployer2.log", "wb") as file_handle:
#     data = service.download_file()
#     data.readinto(file_handle)