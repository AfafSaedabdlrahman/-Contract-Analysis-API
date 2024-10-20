import os
import random
import string
import fitz  # PyMuPDF for PDF processing
from fastapi import FastAPI, UploadFile, HTTPException
import docx  # Library to handle DOCX files
import json
import re
# Function to save file to local directory
def save_file_to_directory(file: UploadFile, upload_dir: str) -> str:
    """
    Saves an uploaded file to a specified directory.

    Args:
        file (UploadFile): The uploaded file object.
        directory (str): The target directory for saving the file.

    Returns:
        str: The path of the saved file.
    """
    file_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    file_path = os.path.join(upload_dir, f"{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    absolute_file_path = os.path.abspath(file_path)  # Create absolute path
    print(f"File saved at: {absolute_file_path}")  # Print absolute path
    return absolute_file_path  # Return the absolute path


# Function to extract text and detect headers from a PDF
def extract_text_from_pdf(absolute_file_path):
    """
    Extracts text content from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        dict: Extracted text with page numbers as keys.
    """
    doc = fitz.open(absolute_file_path)
    headers_and_content = {}

    # Loop through pages to extract text
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Here, we check font size to determine if it's a header
                        font_size = span["size"]
                        text_content = span["text"].strip()
                        
                        # Heuristic: Consider a text block a header if its font size is large
                        if font_size > 12:  # Adjust threshold based on your document's font sizes
                            headers_and_content[text_content] = ""
                        elif text_content:  # Otherwise, it's body text
                            if headers_and_content:
                                # Append content to the last detected header
                                last_header = list(headers_and_content.keys())[-1]
                                headers_and_content[last_header] += text_content + " "
                            else:
                                headers_and_content["Body Text"] = headers_and_content.get("Body Text", "") + text_content + " "
    
    # Return the extracted headers and their content
    return headers_and_content

def extract_text_from_docx(file_path: str) -> dict:
    """
    Extracts text content from a DOCX file.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        dict: Extracted text with section numbers as keys.
    """
    doc = docx.Document(file_path)
    headers_and_content = {"Body Text": ""}
    last_header = "Body Text"

    for para in doc.paragraphs:
        text_content = para.text.strip()
        if text_content:
            if para.style.name.startswith('Heading'):
                headers_and_content[text_content] = ""
                last_header = text_content  # Update last header
            else:
                headers_and_content[last_header] += text_content + " "

    # Clean up any trailing spaces
    headers_and_content = {header: content.strip() for header, content in headers_and_content.items()}

    return headers_and_content

def clean_and_format_to_json_Identify_Endpoint(raw_text):
    """
    Clean the input raw text and format it to valid JSON.

    Args:
    raw_text (str): The raw text to be cleaned and formatted.

    Returns:
    str: The formatted JSON string or an error message.
    """
    try:
        # Remove leading/trailing whitespaces and specific markers
        cleaned_text = raw_text.strip().replace("```json", "").replace("```", "").strip()

        # Replace escaped newlines and tabs with spaces
        cleaned_text = cleaned_text.replace("\\n", " ").replace("\\t", " ")
        
        # Replace escaped quotes with actual quotes
        cleaned_text = cleaned_text.replace('\\"', '"')

        # Handle incomplete values (assuming placeholders like ____ or (DATE) are to be replaced with an empty string)
        cleaned_text = re.sub(r'____|\(DATE\)', '', cleaned_text)

        # Remove trailing commas before closing brackets
        cleaned_text = re.sub(r',\s*([}\]])', r'\1', cleaned_text)

        # Remove excess whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        # Debugging output
        print(f"Debug Info: cleaned_text = {repr(cleaned_text)}")

        # Handling invalid or empty input
        if not cleaned_text:
            print("Error: The input text is empty.")
            return "Error: The input text is empty."

        # Convert the cleaned text into a valid JSON object
        json_data = json.loads(cleaned_text)

        # Debugging output
        print(f"Debug Info: json_data loaded successfully = {json_data}")

        # Iterate and clean each entry further if needed
        for entry in json_data:
            for key, value in entry.items():
                if value:
                    cleaned_value = value.replace("\n", " ").replace("\\n", " ").strip()
                    cleaned_value = cleaned_value.replace("  ", " ").replace(" .", ".")
                    entry[key] = cleaned_value

        # Convert the cleaned Python object back to a JSON string
        return json.dumps(json_data, indent=4, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"Debug Info: JSONDecodeError cleaned_text={repr(cleaned_text)}")
        return f"JSONDecodeError: {e}"


def clean_and_format_to_json_Suggestion_Endpoint(raw_text):
    """
    Clean the input raw text and format it to valid JSON.
    
    Args:
    raw_text (str): The raw text to be cleaned and formatted.
    
    Returns:
    str: The formatted JSON string.
    """
    cleaned_data = []
    # Remove "```json" from the input
    raw_text = raw_text.replace("```json", "").replace("```", "")
    for entry in raw_text.split("},"):
        entry = entry.replace("\"Original Text\": \"", "").replace("\"Suggestion\": \"", "")
        parts = entry.split("\",")
        if len(parts) == 2:
            original_text = parts[0].strip().replace("\n", "")
            suggestion = parts[1].strip().replace("},", "").replace("\"", "").replace("\n", "")
            cleaned_data.append({
                "Original Text": original_text,
                "Suggestion": suggestion
            })
    return json.dumps(cleaned_data, indent=4, ensure_ascii=False)





