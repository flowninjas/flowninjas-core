# FlowNinjas Core - Workflow Builder Backend

A powerful backend API for building and managing Google Cloud Workflows with AI-powered code generation.

## Features

- 🚀 **WYSIWYG Workflow Builder**: Visual workflow creation with drag-and-drop interface support
- 🤖 **AI-Powered Code Generation**: Uses Google Gemini to generate optimized workflow code
- ☁️ **Google Cloud Integration**: Native support for Cloud Functions, Cloud Run, Pub/Sub, and more
- 📦 **Automated Deployment**: Generate deployment configurations and scripts
- 🔧 **Template Library**: Pre-built workflow templates for common patterns
- 📊 **Validation & Preview**: Real-time workflow validation and YAML preview
- 🎯 **Material Design Ready**: API designed to support Google Cloud Console-like UI

## Architecture

### Tech Stack
- **Backend**: FastAPI with Python 3.11+
- **Package Management**: uv (ultra-fast Python package installer)
- **AI Integration**: Google Gemini API
- **Cloud Services**: Google Cloud Platform
- **Logging**: Structured logging with Rich console output
- **Validation**: Pydantic models with comprehensive validation

### Project Structure
```
flowninjas-core/
├── app/
│   ├── api/v1/           # API endpoints
│   ├── core/             # Core configuration and utilities
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   └── main.py           # FastAPI application entry point
├── scripts/              # Utility scripts
├── tests/                # Test suite
└── generated_workflows/  # Generated workflow files
```

## Quick Start

### Prerequisites
- Python 3.11+
- uv package manager
- Google Cloud Project (optional for basic usage)
- Google Gemini API key (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flowninjas-core
   ```

2. **Make the start script executable**
   ```bash
   chmod +x scripts/start.sh
   ```

3. **Run the start script**
   ```bash
   ./scripts/start.sh
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Create a `.env` file from the template
   - Start the development server

4. **Configure environment variables**
   Edit the `.env` file with your configuration:
   ```bash
   # Required for AI features
   GEMINI_API_KEY=your-gemini-api-key
   
   # Optional for Google Cloud integration
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Root: http://localhost:8000/api/v1

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Workflow Management

- `POST /api/v1/workflows/generate` - Generate workflow code and configurations
- `POST /api/v1/workflows/validate` - Validate workflow definition
- `POST /api/v1/workflows/preview` - Preview generated YAML
- `POST /api/v1/workflows/save/{workflow_id}` - Save generated files locally
- `GET /api/v1/workflows/templates` - Get predefined workflow templates
- `GET /api/v1/workflows/node-types` - Get available node types

### Example Usage

#### Generate Workflow Code
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "id": "example-workflow",
      "metadata": {
        "name": "example-workflow",
        "description": "Example workflow",
        "project_id": "your-project-id"
      },
      "nodes": [...],
      "connections": [...]
    },
    "ai_enhance": true,
    "include_deployment": true
  }'
```

#### Get Workflow Templates
```bash
curl "http://localhost:8000/api/v1/workflows/templates"
```

## Workflow Node Types

The system supports various Google Cloud services:

- **Start/End**: Workflow entry and exit points
- **Cloud Function**: Execute serverless functions
- **Cloud Run**: Call containerized services
- **Pub/Sub**: Publish/subscribe messaging
- **HTTP Request**: External API calls
- **Condition**: Conditional branching
- **Parallel**: Concurrent execution
- **Delay**: Timed delays
- **Assign**: Variable assignment
- **Call**: Subworkflow calls
- **Switch**: Multi-condition branching
- **For Loop**: Iteration over collections
- **Try/Catch**: Error handling

## AI-Powered Features

### Code Generation
- **Workflow YAML**: Generate Google Cloud Workflow definitions
- **Cloud Functions**: Create Python function code with proper structure
- **Cloud Run Services**: Generate containerized service code and Dockerfiles
- **Configuration Enhancement**: AI-suggested optimizations and best practices

### Smart Suggestions
- Resource allocation recommendations
- Security best practices
- Performance optimizations
- Error handling patterns

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `GEMINI_API_KEY` | Google Gemini API key | Required for AI features |
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | Optional |
| `WORKFLOWS_STORAGE_PATH` | Generated files path | `./generated_workflows` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Google Cloud Setup

1. **Create a Google Cloud Project**
2. **Enable required APIs**:
   - Cloud Workflows API
   - Cloud Functions API
   - Cloud Run API
   - Pub/Sub API
3. **Create a service account** with appropriate permissions
4. **Download the service account key** and set `GOOGLE_APPLICATION_CREDENTIALS`

### Gemini API Setup

1. **Get API access** at [Google AI Studio](https://makersuite.google.com/)
2. **Generate an API key**
3. **Set the `GEMINI_API_KEY` environment variable**

## Development

### Code Quality Tools

The project includes comprehensive development tools:

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pre-commit install
```

## Generated Files Structure

When generating workflow code, files are organized as:

```
generated_workflows/{workflow_id}/
├── workflow.yaml              # Main workflow definition
├── functions/                 # Cloud Functions
│   └── {function_name}/
│       ├── main.py
│       └── requirements.txt
├── services/                  # Cloud Run services
│   └── {service_name}/
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── terraform/                 # Infrastructure as Code
│   └── main.tf
├── cloudbuild.yaml           # CI/CD configuration
└── deploy.sh                 # Deployment script
```

## Future Roadmap

- 🔐 **Authentication & Authorization**: User management and API security
- 🗄️ **MongoDB Integration**: Persistent workflow storage
- 📊 **Execution Monitoring**: Real-time workflow execution tracking
- 🔄 **LangChain Integration**: Advanced AI framework support
- 💰 **Usage Billing**: Track and bill workflow executions
- 🚀 **Auto Deployment**: Direct deployment to Google Cloud
- 📱 **Frontend Integration**: React-based workflow builder UI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the example workflows in `/api/v1/workflows/templates`

---

Built with ❤️ for the Google Cloud community
