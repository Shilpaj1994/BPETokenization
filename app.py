#!/usr/bin/env python3
"""
FastAPI app to handle data processing for text data.

Author: Shilpaj Bhalerao
Date: Oct 29, 2024
"""
# Standard imports
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
import os
from pathlib import Path

# Local imports
from byte_pair_encoding import BPETokenizer

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Add a request model for text processing
class TextRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload"""
    content_type = file.content_type
    content = await file.read()
    
    try:
        print(f"Received file: {file.filename}")

        if content_type.startswith('text'):
            print("Text file detected")
            # Convert bytes to string
            text = content.decode()
            return {"type": "text", "text": text}
        else:
            print("Unsupported file type")
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a text file.")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_data(file: UploadFile = File(...)):
    """Process the uploaded text file by tokenizing it using BPE"""
    content_type = file.content_type
    content = await file.read()
    
    if content_type.startswith('text'):
        # Load tokenizer and process text
        tokenizer = BPETokenizer.load("tokenizer.json")
        text = content.decode()
        tokens = tokenizer.encode(text)
        return {"type": "text", "processed_data": tokens}
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a text file.")


@app.get("/sample/{sample_number}")
async def get_sample(sample_number: int):
    """Get sample text file content"""
    try:
        sample_path = Path(f"samples/sample{sample_number}.txt")
        if not sample_path.exists():
            raise HTTPException(status_code=404, detail="Sample file not found")
            
        with open(sample_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return {"type": "text", "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add this new route to handle direct text processing
@app.post("/process_text")
async def process_text(text_request: TextRequest):
    """Process text directly without file upload"""
    try:
        # Load tokenizer and process text
        tokenizer = BPETokenizer.load("tokenizer.json")
        tokens = tokenizer.encode(text_request.text)
        return {"type": "text", "processed_data": tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add this new route to handle token decoding
@app.post("/decode_text")
async def decode_text(text_request: TextRequest):
    """Decode the tokenized text back to original form"""
    try:
        # Load tokenizer and decode tokens
        tokenizer = BPETokenizer.load("tokenizer.json")
        
        # Clean and parse the token string
        token_str = text_request.text.strip('[]').replace(' ', '')  # Remove brackets and spaces
        if not token_str:
            raise ValueError("Empty token string")
            
        # Split by comma and convert to integers
        tokens = [int(t) for t in token_str.split(',') if t]
        
        decoded_text = tokenizer.decode(tokens)
        return {"type": "text", "decoded_text": decoded_text}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid token format: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
