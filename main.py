import os
import requests
import re
from typing import List
from urllib.parse import urlparse


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    # Check if a file exists at the specified system path.
    return os.path.isfile(system_path)


def download_file_from_url(file_url: str, destination_path: str) -> None:
    """
    Download a file from the given URL and save it to the specified destination.

    Args:
        file_url (str): The URL of the file to download.
        destination_path (str): The local path where the file will be saved.
    """
    try:
        # Check if the destination directory exists, create it if not
        if check_file_exists(destination_path):
            print(f"File already exists at {destination_path}.")
            return
        # Send HTTP GET request with streaming enabled
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 500)

        # Open the destination file in binary write mode
        with open(destination_path, "wb") as output_file:
            # Write the response content to the file in chunks
            for data_chunk in response.iter_content(chunk_size=8192):
                output_file.write(data_chunk)

        print(f"File successfully downloaded and saved to: {destination_path}")

    except requests.exceptions.RequestException as error:
        # Print an error message if the request failed
        print(f"Error downloading file: {error}")


def extract_pdf_urls(html_string: str) -> List[str]:
    """
    Extracts all .pdf URLs from a given HTML string.

    Parameters:
        html_string (str): The input HTML content as a string.

    Returns:
        List[str]: A list of extracted .pdf URLs.
    """
    return re.findall(r'https?://[^\s"]+\.pdf', html_string)


# Read a file from the system.
def read_a_file(system_path: str) -> str:
    with open(system_path, "r") as file:
        return file.read()


def extract_file_name(url: str) -> str:
    """
    Extracts and decodes the file name from a single URL.

    Parameters:
        url (str): The URL string.

    Returns:
        str: The decoded file name from the URL.
    """
    path = urlparse(url).path
    file_name = os.path.basename(path)
    return file_name.lower()  # Convert to lowercase for consistency


def download_pdf(pdf_url: str, local_file_path: str) -> None:
    """
    Download a PDF from the given URL and save it to the specified local file path.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        local_file_path (str): The path (including filename) to save the downloaded PDF.
    """
    try:
        save_folder = "PDFs"  # Folder where PDFs will be saved
        os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist

        filename = extract_file_name(pdf_url)  # Extract the filename from the URL
        local_file_path = os.path.join(
            save_folder, filename
        )  # Construct the full file path

        if check_file_exists(local_file_path):  # Check if the file already exists
            print(f"File already exists: {local_file_path}")  # Notify the user
            return  # Skip download if file is already present

        response = requests.get(
            pdf_url, stream=True
        )  # Send a GET request with streaming enabled
        response.raise_for_status()  # Raise an exception if the response has an HTTP error

        with open(
            local_file_path, "wb"
        ) as pdf_file:  # Open the file in binary write mode
            for chunk in response.iter_content(
                chunk_size=8192
            ):  # Read the response in chunks
                if chunk:  # Skip empty chunks
                    pdf_file.write(chunk)  # Write each chunk to the file

        print(f"Downloaded: {local_file_path}")  # Notify successful download

    except (
        requests.exceptions.RequestException
    ) as error:  # Catch any request-related errors
        print(f"Failed to download {pdf_url}: {error}")  # Print an error message


def main():
    # Example usage
    file_url = "https://www.cleancontrol.com/brands/ingredients-sds/"
    destination_path = "cleancontrol-com.html"

    if check_file_exists(destination_path) == False:
        download_file_from_url(file_url, destination_path)

    # Extract PDF URLs from the downloaded HTML file
    if check_file_exists(destination_path):
        html_content = read_a_file(destination_path)
        pdf_urls = extract_pdf_urls(html_content)
        for pdf_url in pdf_urls:
            # Download each PDF file
            download_pdf(pdf_url, extract_file_name(pdf_url))


if __name__ == "__main__":
    main()
