"""
Additional required packages:
- azure-core==1.31.0
- azure-ai-documentintelligence==1.0.0b3
- azure-ai-formrecognizer==3.3.3
"""

import os
import sys
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult

from dotenv import load_dotenv
load_dotenv(override=True)

def pdf_to_bytes(file_path):
    """
    Reads a PDF file and returns its content as bytes.

    :param file_path: Path to the PDF file.
    :return: Content of the PDF file in bytes.
    """
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    return pdf_bytes

def is_pdf(file_path):
    """
    Checks if the provided file is a PDF based on its extension.

    :param file_path: Path to the file.
    :return: True if the file is a PDF, False otherwise.
    """
    return file_path.lower().endswith('.pdf')

def transform_pdf_to_markdown(file_path):
    """
    Converts a PDF file to a markdown file using Azure Document Intelligence.

    :param file_path: Path to the PDF file.
    """
    # Fetch endpoint and key from environment variables
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    # Validate environment variables
    if not endpoint or not key:
        raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables must be set.")

    # Validate the file type
    if not is_pdf(file_path):
        raise ValueError("The provided file is not a valid PDF.")

    # Create the output file path by changing the extension to .md
    output_file_path = os.path.splitext(file_path)[0] + ".md"

    # Initialize the Document Intelligence client
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Start the document analysis
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        AnalyzeDocumentRequest(bytes_source=pdf_to_bytes(file_path)),
        output_content_format="markdown",
    )
    result: AnalyzeResult = poller.result()

    # Save the result content as a markdown file with UTF-8 encoding
    with open(output_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(result.content)

    print(f"Content saved as markdown in {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_markdown.py <file_path>")
    else:
        transform_pdf_to_markdown(sys.argv[1])