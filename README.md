# 🏥 MEDAI - Advanced Electronic Health Record System with AI

[![CI Pipeline](https://github.com/drguilhermecapel/medai/actions/workflows/ci.yml/badge.svg)](https://github.com/drguilhermecapel/medai/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/drguilhermecapel/medai/branch/main/graph/badge.svg)](https://codecov.io/gh/drguilhermecapel/medai)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, scalable Electronic Health Record (EHR) system built with FastAPI, SQLModel, and AI diagnostic capabilities. Designed for medical compliance, security, and performance.

## ✨ Features

- 🚀 **High Performance**: FastAPI with async/await support
- 🔒 **Medical Compliance**: HIPAA, GDPR, and FDA 21 CFR Part 11 compliant
- 🤖 **AI Integration**: Built-in AI diagnostic capabilities
- 📊 **Real-time Analytics**: Patient data insights and reporting
- 🔐 **Security First**: End-to-end encryption and audit trails
- 📱 **API-First**: RESTful API with automatic OpenAPI documentation
- 🐳 **Containerized**: Docker and Docker Compose ready

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   MEDAI API     │    │   Database      │
│                 │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│  Web, Mobile    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AI Service    │
                       │  (Diagnostics)  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose (optional)
- PostgreSQL 16 (if running locally)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/drguilhermecapel/medai.git
   cd medai
   ```

2. **Install dependencies with Poetry**:
   ```bash
   poetry install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run with Docker Compose** (recommended):
   ```bash
   docker-compose up -d
   ```

   Or **run locally**:
   ```bash
   poetry run uvicorn medai.api.main:app --reload
   ```

5. **Access the application**:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/healthz

## 📁 Project Structure

```
medai/
├── src/medai/                 # Main application code
│   ├── api/                   # FastAPI application
│   │   └── main.py           # Application entry point
│   ├── database/             # Database configuration
│   │   └── __init__.py       # SQLModel setup
│   └── settings.py           # Pydantic settings
├── tests/                    # Test suite
│   └── test_health.py        # Health check tests
├── docs/                     # Documentation
│   ├── architecture/         # Architecture diagrams
│   └── adr/                  # Architecture Decision Records
├── docker-compose.yml        # Service orchestration
├── Dockerfile               # Container configuration
├── pyproject.toml           # Poetry dependencies
└── .pre-commit-config.yaml  # Code quality hooks
```

## 🛠️ Development

### Setup Development Environment

1. **Install development dependencies**:
   ```bash
   poetry install --with dev
   ```

2. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

3. **Run tests**:
   ```bash
   poetry run pytest
   ```

4. **Run with coverage**:
   ```bash
   poetry run pytest --cov=src --cov-report=html
   ```

### Code Quality

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast linting and code analysis
- **mypy**: Static type checking
- **pytest**: Testing framework

Run all quality checks:
```bash
poetry run black src/
poetry run ruff check src/
poetry run mypy src/
poetry run pytest
```

## 🐳 Docker Deployment

### Production Build

```bash
# Build the image
docker build -t medai:latest .

# Run with external database
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e SECRET_KEY="your-secret-key" \
  medai:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 📚 API Documentation

### Available Endpoints

- `GET /healthz` - Health check endpoint
- `GET /` - Root endpoint with service information
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Authentication

The API uses JWT-based authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

## 🔒 Security & Compliance

### Medical Compliance
- **HIPAA**: Patient data encryption and audit trails
- **GDPR/LGPD**: Data privacy and consent management
- **FDA 21 CFR Part 11**: Electronic records compliance

### Security Features
- JWT authentication with secure token handling
- Database encryption at rest
- TLS 1.3 for data in transit
- Comprehensive audit logging
- Role-based access control

## 🧪 Testing

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Health Checks**: Service availability testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test files
poetry run pytest tests/test_health.py

# Run with specific markers
poetry run pytest -m "not slow"
```

## 📊 Monitoring & Observability

### Health Checks
The application provides comprehensive health checks:

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "service": "MEDAI",
  "version": "1.0.0",
  "database": "healthy"
}
```

### Logging
Structured logging with configurable levels:
- Development: DEBUG level with detailed output
- Production: INFO level with JSON formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run quality checks: `poetry run pre-commit run --all-files`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines
- Follow the existing code style (Black, Ruff)
- Add type hints for all functions
- Write tests for new features
- Update documentation as needed
- Ensure all CI checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍⚕️ Author

**Dr. Guilherme Capel**  
Specialist in Medical Technology  
Email: drguilhermecapel@gmail.com

## 🆘 Support

For support and questions:
- 📧 Email: drguilhermecapel@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/drguilhermecapel/medai/issues)
- 📖 Documentation: [Architecture Overview](docs/architecture/overview.md)

---

**MEDAI - Revolutionizing Healthcare with Artificial Intelligence** 🏥⚕️