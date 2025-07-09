from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import boto3
import json
import base64
import uuid
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

class GenerateImageRequest(BaseModel):
    prompt: str

class GenerateImageResponse(BaseModel):
    image_url: str

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/download/{filename}")
def download_image(filename: str):
    """Download generated image file."""
    filepath = f"generated_images/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.post("/generate-image", response_model=GenerateImageResponse)
def generate_image(request: GenerateImageRequest):
    """
    Generate an image from a text prompt using Amazon Bedrock.
    """
    prompt = request.prompt
    
    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        body = json.dumps({
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "steps": 30,
            "width": 1024,
            "height": 1024
        })
        
        response = bedrock.invoke_model(
            modelId='stability.stable-diffusion-xl-v1',
            body=body
        )
        
        result = json.loads(response['body'].read())
        image_data = result['artifacts'][0]['base64']
        
        # Save image locally with unique filename
        os.makedirs('generated_images', exist_ok=True)
        filename = f"{uuid.uuid4().hex[:8]}.png"
        filepath = f"generated_images/{filename}"
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        return GenerateImageResponse(image_url=filename)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
