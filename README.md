# Text-to-Image Microservice

A production-ready FastAPI microservice that generates high-quality images from text prompts using Amazon Bedrock's Stable Diffusion XL model. Built for scalability and easy deployment.

## 🚀 Features

- **AI-Powered Image Generation**: Uses Amazon Bedrock's Stable Diffusion XL for high-quality 1024x1024 images
- **RESTful API**: Clean, documented endpoints with automatic OpenAPI/Swagger docs
- **File Management**: Automatic image storage and serving with unique filenames
- **Health Monitoring**: Built-in health check endpoint for monitoring
- **CI/CD Pipeline**: Automated testing, building, and deployment via GitHub Actions
- **Infrastructure as Code**: Terraform templates for AWS App Runner deployment
- **Docker Ready**: Containerized with layer caching for fast builds
- **Cloud Native**: Optimized for AWS App Runner with auto-scaling

## 📋 Prerequisites

### AWS Requirements
- **AWS Account** with Bedrock access
- **IAM User/Role** with the following permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:InvokeModel"
        ],
        "Resource": "arn:aws:bedrock:*::foundation-model/stability.stable-diffusion-xl-v1"
      }
    ]
  }
  ```
- **Model Access**: Request access to Stability AI SDXL in AWS Bedrock console

![AWS Bedrock Model Access](screenshots/bedrock-model-access.png)

### System Requirements
- **Python 3.11+**
- **Docker** (for containerized deployment)
- **2GB+ RAM** (for image processing)

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/franklynux/text-to-image-microservice.git
   cd text-to-image-microservice
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the service**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

![FastAPI Swagger Documentation](screenshots/fastapi-swagger-docs.png)

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t text-to-image-service .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name text-to-image \
     -p 8000:8000 \
     -v $(pwd)/generated_images:/app/generated_images \
     text-to-image-service
   ```

### AWS App Runner Deployment

#### Using Terraform (Recommended)
1. **Navigate to terraform directory**
   ```bash
   cd terraform_app_runner
   ```

2. **Initialize and apply**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

#### Manual Setup
1. **Push to ECR** (automated via GitHub Actions)
2. **Create App Runner service** with:
   - **Port**: 8000
   - **Health check path**: `/health`
   - **ECR Image**: `536697239284.dkr.ecr.us-east-1.amazonaws.com/text_to_image_service:latest`

![AWS App Runner Configuration](screenshots/apprunner-configuration.png)

## 📚 API Documentation

### Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

#### Generate Image
```http
POST /generate-image
Content-Type: application/json

{
  "prompt": "A majestic dragon flying over a medieval castle at sunset"
}
```

**Response:**
```json
{
  "image_url": "a1b2c3d4.png"
}
```

**Image Generation Parameters:**
- **Resolution**: 1024x1024 pixels
- **Steps**: 30 (quality vs speed balance)
- **CFG Scale**: 7 (prompt adherence)
- **Format**: PNG

#### Download Image
```http
GET /download/{filename}
```

**Example:**
```http
GET /download/a1b2c3d4.png
```

**Response:** Binary image file (PNG format)

### API Testing Example

![API Testing with Generated Image](screenshots/api-testing-example.png)

### Example Usage

#### Using curl
```bash
# Generate image
curl -X POST "http://localhost:8000/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cyberpunk cityscape at night"}'

# Download image
curl -o generated_image.png "http://localhost:8000/download/a1b2c3d4.png"
```

#### Using Python
```python
import requests

# Generate image
response = requests.post(
    "http://localhost:8000/generate-image",
    json={"prompt": "A serene mountain landscape"}
)
result = response.json()
filename = result["image_url"]

# Download image
image_response = requests.get(f"http://localhost:8000/download/{filename}")
with open("my_image.png", "wb") as f:
    f.write(image_response.content)
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_main.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Generate test image
curl -X POST http://localhost:8000/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test image"}'
```

## 💰 Cost Considerations

### Amazon Bedrock Pricing (Stability AI SDXL)
- **Cost per image**: ~$0.072 (1024x1024)
- **Monthly estimates**:
  - 100 images: ~$7.20
  - 1,000 images: ~$72.00
  - 10,000 images: ~$720.00

### Cost Optimization Tips
- Use smaller image sizes when possible
- Implement caching for repeated prompts
- Set up usage monitoring and alerts
- Consider batch processing for multiple images

## 🔧 Configuration

### Model Configuration
The service uses these Bedrock parameters:
```json
{
  "text_prompts": [{"text": "your_prompt"}],
  "cfg_scale": 7,
  "steps": 30,
  "width": 1024,
  "height": 1024
}
```

## 🚨 Troubleshooting

### Common Issues

#### "Model access denied"
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to "Stability AI SDXL"
4. Wait for approval (usually instant)

#### "Health check failed" (App Runner)
- Ensure port 8000 is configured
- Verify `/health` endpoint responds

#### "Image not found" (404)
- Check if `generated_images` directory exists
- Verify file permissions
- Ensure Docker volume mounting is correct

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

## 🔄 CI/CD Pipeline

The project includes automated CI/CD using GitHub Actions:

### Workflow Features
- **Automated Testing**: Runs pytest on every push to main
- **Docker Build**: Builds and pushes images to Amazon ECR
- **Auto Deployment**: App Runner automatically deploys new ECR images
- **Docker Layer Caching**: Speeds up builds using GitHub Actions cache

### Setup GitHub Secrets
Add these secrets in your GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

### Workflow Triggers
- Push to `main` branch triggers: Test → Build → Deploy
- Failed tests prevent deployment

![GitHub Actions Workflow](screenshots/github-actions-workflow.png)

## 📁 Project Structure
```
text-to-image-microservice/
├── .github/
│   └── workflows/
│       └── build-and-deploy.yaml  # CI/CD pipeline
├── app/
│   ├── __init__.py
│   └── main.py                    # FastAPI application
├── generated_images/              # Generated image storage
├── terraform_app_runner/          # Infrastructure as Code
│   ├── main.tf                   # App Runner service
│   ├── values.tf                 # Variables
│   └── output.tf                 # Outputs
├── tests/
│   └── test_main.py              # Unit tests
├── .env.example                  # Environment template
├── .gitignore                   # Git ignore rules
├── dockerfile                   # Container configuration
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🔒 Security Best Practices

- **Never commit AWS credentials** to version control
- **Use IAM roles** instead of access keys when possible
- **Implement rate limiting** for production use
- **Add input validation** for prompts
- **Use HTTPS** in production
- **Monitor usage** and set up billing alerts

## 🚀 Production Deployment

### AWS App Runner (Recommended)
1. Build and push Docker image to ECR
2. Create App Runner service
3. Set up custom domain (optional)

### AWS ECS/Fargate
1. Create ECS cluster
2. Define task definition
3. Create service with load balancer
4. Configure auto-scaling

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: text-to-image-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: text-to-image-service
  template:
    metadata:
      labels:
        app: text-to-image-service
    spec:
      containers:
      - name: text-to-image-service
        image: your-registry/text-to-image-service:latest
        ports:
        - containerPort: 8000
```

## 📈 Monitoring & Observability

### Health Monitoring
```bash
# Basic health check
curl -f http://localhost:8000/health || exit 1
```

### Metrics to Monitor
- **Response time**: Image generation latency
- **Error rate**: Failed requests percentage
- **Throughput**: Requests per minute
- **AWS costs**: Bedrock usage costs

![App Runner Monitoring Dashboard](screenshots/apprunner-monitoring.png)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **AWS Support**: [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

---

**Built with ❤️ using FastAPI and Amazon Bedrock**
