import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import google.generativeai as genai
from dotenv import load_dotenv
import json
import random
import string
import fitz  # PyMuPDF for PDF processing
from dotenv import load_dotenv
import docx  # Library to handle DOCX files


from Extraction import (
    save_file_to_directory,
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_and_format_to_json_Identify_Endpoint,
    clean_and_format_to_json_Suggestion_Endpoint
)


# Initialize FastAPI app and load environment variables
app = FastAPI()
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel('gemini-pro')


def identify_key_concepts(headers_and_content: dict) -> str:
    """
    Identifies key clauses or concepts using the LLM.

    Args:
        headers_and_content (dict): Extracted text and headers from the document.

    Returns:
        str: Raw response from the LLM containing identified clauses.
    """
    

    prompt_for_llm = f"""
    You are an AI language model tasked with extracting key clauses from a contract document. Follow these steps carefully:

    1. **Identify Key Clauses**:
       Extract all major clauses from the contract. Include, but are not limited to:
       - Duties of Consultant
       - Compensation
       - Term of Agreement
       - Early Termination
       - Indemnification for Damages, Taxes, and Contributions
       - Insurance Requirements
       - Compliance with Federal, State, and Local Laws
       - Equal Employment Opportunity
       - Harassment Policy
       - Licenses
       - Independent Consultant Status
       - Retention and Audit of Records
       - Inspection of Work
       - Ownership of Work Products
       - Safety Compliance
       - Modification of Agreement
       - Disputes and Dispute Resolution
       - Audit Review Procedures
       - Subcontracting
       - Non-assignment of Agreement
       - Prohibition of Rebates, Kickbacks, or Unlawful Consideration
       - Notification and Communications
       - Complete Agreement and Attachments

    2. **Extract Full Text for Each Clause**:
       - For each clause, extract the entire text including all relevant sub-clauses, definitions, and detailed terms.
       - Ensure completeness, capturing all the important legal language and specific terms mentioned.

    3. **Output Format**:
       - Present the extracted clauses as a list of dictionaries.
       - Each dictionary should have the clause title as the key (e.g., "Duties of Consultant") and the complete text of the clause as the value.
       - Ensure the clause text is clear and well-formatted, respecting the structure of the contract.
       - Example output format:
         ```json
         [
           {{"Duties of Consultant": "Full text of the Duties of Consultant clause..."}},
           {{"Compensation": "Full text of the Compensation clause..."}},
           {{"Termination": "Full text of the Termination clause..."}},
           {{"Insurance": "Full text of the Insurance clause..."}}
         ]
         ```

    **Example Output**:
    ```json
    [
      {{"Duties of Consultant": "The consultant agrees to perform specific services as outlined in Exhibit A, including..."}},
      {{"Compensation": "The total compensation shall not exceed $X for services provided, with progress payments made..."}},
      {{"Termination": "The agreement can be terminated by either party with 30 days' written notice for convenience, or..."}},
      {{"Insurance": "The consultant must maintain general liability insurance with a minimum coverage of..."}}
    ]
    ```

    Data to extract:
    {headers_and_content}
    """
    messages = [{"role": "user", "parts": [prompt_for_llm]}]
    
    # Debug step: Print the prompt to ensure it is structured correctly
    #print(f"Prompt sent to LLM: {prompt_for_llm}")

    response = llm.generate_content(messages)
    
    # Debug step: Print the raw response from the LLM
   # print(f"Raw response from LLM: {response.text}")
    
    return response.text

def generate_review(headers_and_content: dict) -> str:
    """
    Generates negotiation suggestions using the LLM.

    Args:
        headers_and_content (dict): Extracted text and headers from the document.

    Returns:
        str: Raw response from the LLM containing suggestions.
    """
    prompt_for_llm = f"""
    You are an AI language model tasked with generating negotiation suggestions based on the document content. Follow these steps:

    1. **Analyze Content**: Identify sections with negotiation potential.
    2. **Generate Suggestions**: Provide tailored advice for each identified section.
    3. **Format the Output**: Return suggestions as a list of dictionaries formatted as:
    ```json
    [
        {{"Original Text": "Section text...", "Suggestion": "Advice..."}}
    ]
    ```

    Data to extract:
    {headers_and_content}
    """

    messages = [{"role": "user", "parts": [prompt_for_llm]}]
    
    # Debug step: Print the prompt to ensure it is structured correctly
    print(f"Prompt sent to LLM: {prompt_for_llm}")

    response = llm.generate_content(messages)
    
    # Debug step: Print the raw response from the LLM
   # print(f"Raw response from LLM: {response.text}")
    
    return response.text


# Endpoint to simulate the upload of a contract file
@app.post("/simulate_upload/")
async def simulate_upload(file: UploadFile):
    upload_dir = "./uploads"  # Define your local upload directory
    os.makedirs(upload_dir, exist_ok=True)

    try:
        file_path = save_file_to_directory(file, upload_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Determine contract type
    contract_type = "PDF" if file.filename.endswith('.pdf') else "DOCX" if file.filename.endswith('.docx') else "Unknown"

    # Generate a mock URL reflecting a local environment
    mock_url = f"http://localhost:8000/contracts/{os.path.basename(file_path)}"

    return {
        "mock_url": mock_url,
        "contract_type": contract_type,
        "message": "Contract upload simulated successfully."
    }


# Endpoint to identify key concepts from the uploaded contract
@app.post("/identify_upload/")
async def identify_upload(file: UploadFile):
    """
    Identifies key concepts from the uploaded contract.

    Args:
        file (UploadFile): The uploaded contract file.

    Returns:
        JSONResponse: Extracted key clauses in JSON format.
    """
async def upload_contract(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = save_file_to_directory(file, upload_dir)
    
    if file.filename.endswith('.pdf'):
        headers_and_content = extract_text_from_pdf(file_path)
    elif file.filename.endswith('.docx'):
        headers_and_content = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Generate response from the LLM using the headers and content extracted
    #response_json = generate_response(headers_and_content)
    
    # # Generate response from the LLM using the headers and content extracted
    response_text = identify_key_concepts(headers_and_content)
    
    
    #  Clean and parse the response into valid JSON
     
    formatted_json = clean_and_format_to_json_Identify_Endpoint(response_text)
    
    return JSONResponse(content=json.loads(formatted_json))


@app.post("/suggestion/")
async def upload_contract(file: UploadFile):
    """
    Generates negotiation suggestions for the uploaded contract.

    Args:
        file (UploadFile): The uploaded contract file.

    Returns:
        JSONResponse: Negotiation suggestions in JSON format.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = save_file_to_directory(file, upload_dir)
    
    if file.filename.endswith('.pdf'):
        headers_and_content = extract_text_from_pdf(file_path)
    elif file.filename.endswith('.docx'):
        headers_and_content = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # Generate response from the LLM using the headers and content extracted
    #response_json = generate_response(headers_and_content)

    # Generate response from the LLM using the headers and content extracted
    response_text = generate_review(headers_and_content)
    
    # Clean and parse the response into valid JSON
    formatted_json = clean_and_format_to_json_Suggestion_Endpoint(response_text)
    
    return JSONResponse(content=json.loads(formatted_json))

@app.get("/contracts/{filename}")
async def get_contract(filename: str):
    """
    Serves the uploaded contract files.

    Args:
        filename (str): Name of the file to retrieve.

    Returns:
        FileResponse: The requested file if it exists, otherwise 404 error.
    """
    file_path = os.path.join("./uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")
