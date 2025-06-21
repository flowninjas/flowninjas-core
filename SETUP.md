# FlowNinjas Setup Guide

This guide will help you set up both the backend (FlowNinjas Core) and frontend (FlowNinjas Web) for the workflow builder application.

## Prerequisites

- Python 3.11+
- Node.js 18+ and yarn
- uv package manager for Python
- Google Cloud Project (optional)
- Google Gemini API key (optional for AI features)

## Backend Setup (FlowNinjas Core)

### 1. Install uv (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Setup Backend

```bash
cd flowninjas-core

# Make start script executable
chmod +x scripts/start.sh

# Run the setup and start script
./scripts/start.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` file from template
- Start the development server

### 3. Configure Environment (Optional)

Edit the `.env` file to add your API keys:

```bash
# For AI features
GEMINI_API_KEY=your-gemini-api-key

# For Google Cloud integration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### 4. Test Backend

```bash
# Run the demo script
python demo.py

# Run tests
pytest

# Check API documentation
# Visit: http://localhost:8000/docs
```

## Frontend Setup (FlowNinjas Web)

### 1. Install Dependencies

```bash
cd ../flowninjas-web

# Install dependencies with yarn
yarn install
```

### 2. Start Development Server

```bash
yarn start
```

The frontend will be available at: http://localhost:3000

### 3. Build for Production

```bash
yarn build
```

## Manual Backend Setup (Alternative)

If the start script doesn't work, you can set up manually:

```bash
cd flowninjas-core

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Manual Frontend Setup (Alternative)

If you prefer npm over yarn:

```bash
cd flowninjas-web

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Verification

### Backend Verification

1. **Health Check**: Visit http://localhost:8000/health
2. **API Docs**: Visit http://localhost:8000/docs
3. **Run Demo**: Execute `python demo.py`
4. **Run Tests**: Execute `pytest`

### Frontend Verification

1. **Development Server**: Visit http://localhost:3000
2. **Build**: Run `yarn build` and check `build/` directory

## API Endpoints

Once the backend is running, you can test these endpoints:

- `GET /health` - Health check
- `GET /api/v1/` - API root
- `GET /api/v1/workflows/node-types` - Available node types
- `GET /api/v1/workflows/templates` - Workflow templates
- `POST /api/v1/workflows/validate` - Validate workflow
- `POST /api/v1/workflows/preview` - Preview workflow YAML
- `POST /api/v1/workflows/generate` - Generate workflow code

## Example API Usage

### Get Node Types
```bash
curl http://localhost:8000/api/v1/workflows/node-types
```

### Get Templates
```bash
curl http://localhost:8000/api/v1/workflows/templates
```

### Validate Workflow
```bash
curl -X POST http://localhost:8000/api/v1/workflows/validate \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test",
    "metadata": {"name": "test"},
    "nodes": [],
    "connections": []
  }'
```

## Troubleshooting

### Backend Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **Port Already in Use**: Change port in `.env` file or kill existing process
3. **Missing Dependencies**: Run `uv pip install -e .` again

### Frontend Issues

1. **Module Not Found**: Run `yarn install` or `npm install`
2. **Port Already in Use**: React will prompt to use a different port
3. **Build Errors**: Check TypeScript errors and fix them

### Common Issues

1. **CORS Errors**: Make sure backend allows frontend origin in `ALLOWED_HOSTS`
2. **API Connection**: Verify backend is running on correct port
3. **Environment Variables**: Check `.env` file configuration

## Development Workflow

1. **Start Backend**: `./scripts/start.sh` in `flowninjas-core/`
2. **Start Frontend**: `yarn start` in `flowninjas-web/`
3. **Make Changes**: Edit code in respective directories
4. **Test**: Run tests and verify functionality
5. **Build**: Create production builds when ready

## Production Deployment

### Backend Deployment

```bash
# Build production image
docker build -t flowninjas-core .

# Or deploy to Google Cloud Run
gcloud run deploy flowninjas-core --source .
```

### Frontend Deployment

```bash
# Build for production
yarn build

# Deploy to static hosting (Netlify, Vercel, etc.)
# Or serve with nginx/apache
```

## Next Steps

1. Configure Google Cloud credentials for full functionality
2. Set up Gemini API key for AI features
3. Customize the frontend components
4. Add authentication and user management
5. Set up MongoDB for data persistence
6. Configure CI/CD pipelines

## Support

- Check the API documentation at `/docs`
- Review the example workflows in templates
- Run the demo script for testing
- Check logs for debugging information

---

Happy building with FlowNinjas! 🥷⚡
