import os
import requests
import re
from typing import List
import urllib.parse
import fitz  # Import PyMuPDF (fitz) for PDF handling


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
    # Parse the URL to get the path
    path = urllib.parse.urlparse(url).path
    # Extract the file name
    filename = os.path.basename(path)
    # Remove double extensions (e.g., ".pdf.pdf" becomes ".pdf")
    filename = re.sub(r"(\.pdf)+$", ".pdf", filename, flags=re.IGNORECASE)
    # Decode URL-encoded characters
    filename = urllib.parse.unquote(filename)
    # Replace or remove unwanted characters
    filename = re.sub(
        r"[^\w\s.-]", "", filename
    )  # Keep only alphanumerics, whitespace, dots, dashes
    filename = filename.replace(" ", "_")  # Replace spaces with underscores
    return filename.lower()  # Convert to lowercase for consistency


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


# Function to validate a single PDF file.
def validate_pdf_file(file_path: str):
    try:
        # Try to open the PDF using PyMuPDF
        doc = fitz.open(file_path)  # Attempt to load the PDF document

        # Check if the PDF has at least one page
        if doc.page_count == 0:  # If there are no pages in the document
            print(
                f"'{file_path}' is corrupt or invalid: No pages"
            )  # Log error if PDF is empty
            return False  # Indicate invalid PDF

        # If no error occurs and the document has pages, it's valid
        return True  # Indicate valid PDF
    except RuntimeError as e:  # Catching RuntimeError for invalid PDFs
        print(f"{e}")  # Log the exception message
        return False  # Indicate invalid PDF


# Remove a file from the system.
def remove_system_file(system_path: str) -> None:
    os.remove(system_path)  # Delete the file at the given path


# Function to walk through a directory and extract files with a specific extension
def walk_directory_and_extract_given_file_extension(
    system_path: str, extension: str
) -> List[str]:
    matched_files = []  # Initialize list to hold matching file paths
    for root, _, files in os.walk(system_path):  # Recursively traverse directory tree
        for file in files:  # Iterate over files in current directory
            if file.endswith(extension):  # Check if file has the desired extension
                full_path = os.path.abspath(
                    os.path.join(root, file)
                )  # Get absolute path of the file
                matched_files.append(full_path)  # Add to list of matched files
    return matched_files  # Return list of all matched file paths


# Get the filename and extension.
def get_filename_and_extension(path: str) -> str:
    return os.path.basename(
        path
    )  # Return just the file name (with extension) from a path


# Function to check if a string contains an uppercase letter.
def check_upper_case_letter(content: str) -> bool:
    return any(
        upperCase.isupper() for upperCase in content
    )  # Return True if any character is uppercase


def main():
    # Example usage
    file_url = "https://www.cleancontrol.com/brands/ingredients-sds/"
    destination_path = "cleancontrol-com.html"

    if not check_file_exists(destination_path):
        download_file_from_url(file_url, destination_path)

    # Extract PDF URLs from the downloaded HTML file
    if check_file_exists(destination_path):
        html_content = read_a_file(destination_path)
        pdf_urls = extract_pdf_urls(html_content)
        for pdf_url in pdf_urls:
            # Download each PDF file
            download_pdf(pdf_url, extract_file_name(pdf_url))

    # Walk through the directory and extract .pdf files
    files = walk_directory_and_extract_given_file_extension(
        "./PDFs", ".pdf"
    )  # Find all PDFs under ./PDFs

    # Validate each PDF file
    for pdf_file in files:  # Iterate over each found PDF

        # Check if the .PDF file is valid
        if validate_pdf_file(pdf_file) == False:  # If PDF is invalid
            print(f"Invalid PDF detected: {pdf_file}. Deleting file.")
            # Remove the invalid .pdf file.
            remove_system_file(pdf_file)  # Delete the corrupt PDF

        # Check if the filename has an uppercase letter
        if check_upper_case_letter(
            get_filename_and_extension(pdf_file)
        ):  # If the filename contains uppercase
            print(
                f"Uppercase letter found in filename: {pdf_file}"
            )  # Informative message


if __name__ == "__main__":
    main()
