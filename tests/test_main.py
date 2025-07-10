from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import base64
import json
import os

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# def test_generate_image_success(monkeypatch, tmp_path):
#     # Mock OpenAI API response
#     class MockResponse:
#         def __getitem__(self, item):
#             return [{"url": "https://fakeimg.com/image.png"}]
#     def mock_create(*args, **kwargs):
#         return {"data": [{"url": "https://fakeimg.com/image.png"}]}
#     monkeypatch.setenv("OPENAI_API_KEY", "test-key")
#     with patch("openai.Image.create", mock_create):
#         response = client.post("/generate-image", json={"prompt": "A cat riding a bike"})
#         assert response.status_code == 200
#         assert response.json()["image_url"].startswith("https://")

def test_generate_image_bedrock_success(tmp_path):
    # Mock Bedrock client and response
    mock_bedrock = MagicMock()
    fake_base64 = base64.b64encode(b"fakeimage").decode()
    mock_response = {
        'body': MagicMock(read=MagicMock(return_value=json.dumps({
            'artifacts': [{ 'base64': fake_base64 }]
        }).encode()))
    }
    mock_bedrock.invoke_model.return_value = mock_response
    with patch("boto3.client", return_value=mock_bedrock):
        # Patch os.makedirs to avoid actual file system writes
        with patch("os.makedirs"):
            # Patch open to write to a temp file
            with patch("builtins.open", create=True) as mock_open:
                response = client.post("/generate-image", json={"prompt": "A test prompt"})
                assert response.status_code == 200
                assert response.json()["image_url"].endswith(".png")

# def test_generate_image_no_api_key(monkeypatch):
#     monkeypatch.delenv("OPENAI_API_KEY", raising=False)
#     response = client.post("/generate-image", json={"prompt": "A cat riding a bike"})
#     assert response.status_code == 500
#     assert response.json()["detail"] == "OpenAI API key not set."

def test_download_image_found(tmp_path):
    # Create a fake image file
    os.makedirs("generated_images", exist_ok=True)
    filename = "testfile.png"
    filepath = f"generated_images/{filename}"
    with open(filepath, "wb") as f:
        f.write(b"fakeimage")
    response = client.get(f"/download/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    os.remove(filepath)

def test_download_image_not_found():
    response = client.get("/download/nonexistent.png")
    assert response.status_code == 404
    assert response.json()["detail"] == "Image not found"

