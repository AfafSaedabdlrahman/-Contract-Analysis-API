
# Contract Analysis API

A FastAPI-based solution for processing contract documents, identifying key clauses, and generating negotiation suggestions using Google's Gemini AI (Generative AI). This API supports PDF and DOCX file formats, providing automated extraction of important contract sections and tailored negotiation advice.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Environment Variables](#environment-variables)
5. [Usage](#usage)
   - [Start the Server](#start-the-server)
   - [API Endpoints](#api-endpoints)
6. [Project Structure](#project-structure)
7. [Logic Explanation](#logic-explanation)
   - [Extraction Logic](#extraction-logic)
   - [Identification of Key Clauses Logic](#identification-of-key-clauses-logic)
   - [Review Suggestions Logic](#review-suggestions-logic)
8. [Contributing](#contributing)
9. [License](#license)

## Features

- **Contract Upload**: Upload PDF or DOCX contract files for analysis.
- **Key Clause Extraction**: Uses AI to extract important clauses from the contract.
- **Negotiation Suggestions**: Provides negotiation advice based on contract content.
- **Local File Storage Simulation**: Stores uploaded contracts locally for testing purposes.

## Requirements

- Python 3.7+
- FastAPI
- PyMuPDF (fitz) for PDF processing
- `python-docx` for DOCX file handling
- `google.generativeai` for using Google's Gemini AI
- `python-dotenv` for environment variable management
- Other dependencies listed in `requirements.txt`



2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**
   - Create a `.env` file in the root directory.
   - Add the following environment variable:
     ```
     GEMINI_API_KEY=your_google_gemini_api_key
     ```

## Environment Variables

The `.env` file should contain:
- `GEMINI_API_KEY`: Your Google Gemini API key used for Generative AI.

## Usage

### Start the Server

Run the FastAPI server using:
```bash
uvicorn main:app --reload
```

The server will be accessible at `http://localhost:8000`.

### API Endpoints

#### 1. Upload Contract File
- **Endpoint**: `/simulate_upload/`
- **Method**: `POST`
- **Description**: Simulates the upload of a contract file (PDF or DOCX).
- **Request Body**:
    - `file`: The contract file to be uploaded.
- **Response**:
    ```json
    {
        "mock_url": "http://localhost:8000/contracts/{filename}",
        "contract_type": "PDF or DOCX",
        "message": "Contract upload simulated successfully."
    }
    ```

#### 2. Identify Key Clauses
- **Endpoint**: `/identify_upload/`
- **Method**: `POST`
- **Description**: Extracts key clauses from the uploaded contract.
- **Request Body**:
    - `file`: The contract file (PDF or DOCX).
- **Response**:
    - Returns a JSON list containing key clauses identified in the document.

#### 3. Generate Negotiation Suggestions
- **Endpoint**: `/suggestion/`
- **Method**: `POST`
- **Description**: Provides negotiation suggestions based on the contract content.
- **Request Body**:
    - `file`: The contract file (PDF or DOCX).
- **Response**:
    - Returns a JSON list of suggestions for negotiating the contract.

#### 4. Serve Uploaded Contract
- **Endpoint**: `/contracts/{filename}`
- **Method**: `GET`
- **Description**: Retrieves an uploaded contract file by filename.
- **Response**:
    - Returns the file if it exists, otherwise a 404 error.

## Project Structure

```
contract-analysis-api/
│
├── main.py                   # Main FastAPI application file
├── Extraction.py             # Utility functions for file handling and text extraction
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables file
└── uploads/                  # Directory for uploaded files (created at runtime)
```

### Key Files

- **`main.py`**: The main entry point for the FastAPI application, defining the API endpoints.
- **`Extraction.py`**: Contains helper functions for processing PDF and DOCX files, as well as cleaning and formatting text for JSON output.
- **`uploads/`**: A local directory for storing uploaded contract files during simulation.

## Logic Explanation

### 1. Extraction Logic

The extraction process involves retrieving text content from PDF and DOCX files and preparing it for further analysis. Here's how it works:

- **File Handling**:
  - The uploaded file is first saved to a specified directory on the server.
  - The type of the file (PDF or DOCX) is determined based on the file extension.

- **Text Extraction for PDF Files**:
  - Uses the PyMuPDF library (`fitz`) to open the PDF file.
  - The library extracts text from each page, which is then consolidated into a single string or list of sections.
  - Additional processing may be applied to identify headers, section titles, and content blocks.

- **Text Extraction for DOCX Files**:
  - Uses the `python-docx` library to open and read the DOCX file.
  - The library reads the text from each paragraph, and the text is collected into a coherent structure, similar to the PDF processing.

- **Text Cleaning**:
  - After extracting text, a cleaning process ensures consistency by removing any non-printable characters, excess whitespace, and unwanted formatting.
  - The cleaned text is then prepared for further analysis.

The extraction output is typically structured as a dictionary, with keys representing headers/sections and values containing the corresponding text.

### 2. Identification of Key Clauses Logic

The identification of key clauses is performed using a Language Model (LLM), specifically Google Gemini's Generative AI. This process involves creating a prompt and sending it to the LLM to extract important sections from the contract:

- **Prompt Construction**:
  - A detailed prompt is created, instructing the LLM to identify specific clauses, such as "Duties of Consultant," "Compensation," "Termination," and other key sections typically found in contracts.
  - The prompt includes examples of how the output should be formatted, guiding the LLM to return results in a structured format (e.g., a list of dictionaries with clause titles and full texts).

- **Sending Request to LLM**:
  - The prompt, along with the cleaned and extracted text, is sent to the LLM as a message. The AI processes this input and generates a response containing the identified clauses.

- **Post-Processing the Response**:
  - The raw response from the LLM may need cleaning and formatting. The `clean_and_format_to_json_Identify_Endpoint` function is used to convert the LLM's response into valid JSON.
  - The function addresses common issues, such as incomplete JSON structures, trailing commas, or placeholders in the text.

The result is a well-structured JSON output with the identified key clauses and their corresponding content.

### 3. Review Suggestions Logic

The review suggestion process provides negotiation advice based on the contents of the contract. The LLM is used to generate suggestions for improving or negotiating the terms of the contract:

- **Prompt Construction for Suggestions**:
  - A prompt is created to guide the LLM in analyzing the contract sections. It instructs the AI to identify areas that have negotiation potential and to generate tailored suggestions.
  - The prompt specifies the desired output format, which should include both the original contract section text and the corresponding negotiation advice.

- **Generating the Review Suggestions**:
  - Similar to the key clause identification process, the prompt is sent to the LLM along with the extracted contract content.
  - The LLM processes the prompt and generates a response, containing negotiation suggestions formatted as a list of dictionaries (each dictionary containing an "Original Text" and "Suggestion" field).

- **Cleaning and Formatting the Response**:
  - The `clean_and_format_to_json_Suggestion_Endpoint` function is used to convert the LLM’s output into a valid JSON format, addressing any common formatting issues.
  - The final output is a JSON list of suggestions, ready to be returned to the user.


