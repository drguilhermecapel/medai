# MEDAI System Architecture Overview

## High-Level Architecture

MEDAI is a modern Electronic Health Record (EHR) system built with a microservices architecture, designed for scalability, security, and medical compliance.

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Application]
        MOB[Mobile App]
        API_CLIENT[External API Clients]
    end

    subgraph "API Gateway"
        GATEWAY[FastAPI Gateway]
        AUTH[Authentication Service]
        RATE[Rate Limiting]
    end

    subgraph "Core Services"
        API[MEDAI API Service]
        AI[AI Diagnostic Service]
        NOTIFY[Notification Service]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL 16)]
        REDIS[(Redis Cache)]
        FILES[File Storage]
    end

    subgraph "External Services"
        FHIR[FHIR Server]
        ML[ML Model Registry]
        AUDIT[Audit Logging]
    end

    WEB --> GATEWAY
    MOB --> GATEWAY
    API_CLIENT --> GATEWAY

    GATEWAY --> AUTH
    GATEWAY --> RATE
    GATEWAY --> API

    API --> AI
    API --> NOTIFY
    API --> POSTGRES
    API --> REDIS

    AI --> ML
    AI --> POSTGRES

    API --> FHIR
    API --> AUDIT
    NOTIFY --> AUDIT

    classDef client fill:#e1f5fe
    classDef gateway fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec

    class WEB,MOB,API_CLIENT client
    class GATEWAY,AUTH,RATE gateway
    class API,AI,NOTIFY service
    class POSTGRES,REDIS,FILES data
    class FHIR,ML,AUDIT external
```

## Core Components

### 1. API Service (FastAPI)
- **Technology**: FastAPI + SQLModel + PostgreSQL
- **Responsibilities**:
  - Patient data management
  - Medical records CRUD operations
  - Authentication and authorization
  - Medical compliance enforcement
  - API documentation and validation

### 2. Database Layer
- **Primary Database**: PostgreSQL 16
  - Patient records
  - Medical data
  - User management
  - Audit trails
- **Cache Layer**: Redis
  - Session management
  - Frequently accessed data
  - Real-time notifications

### 3. AI Diagnostic Service
- **Technology**: Python + TensorFlow/PyTorch
- **Capabilities**:
  - Medical image analysis
  - Diagnostic recommendations
  - Risk prediction models
  - Natural language processing for clinical notes

## Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    participant AI Service
    participant Cache

    Client->>API: POST /api/v1/patients
    API->>API: Validate request
    API->>Database: Store patient data
    Database-->>API: Confirmation
    API->>Cache: Cache patient summary
    API->>AI Service: Trigger risk analysis
    AI Service-->>API: Risk score
    API->>Database: Store AI insights
    API-->>Client: Response with patient ID
```

## Security Architecture

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Medical professional verification
- Session management with Redis

### Data Protection
- End-to-end encryption
- Database encryption at rest
- TLS 1.3 for data in transit
- Regular security audits

### Medical Compliance
- HIPAA compliance
- GDPR/LGPD compliance
- FDA 21 CFR Part 11 compliance
- Audit logging for all operations

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        DEV_API[API Service]
        DEV_DB[(Dev Database)]
    end

    subgraph "Staging"
        STAGE_API[API Service]
        STAGE_DB[(Stage Database)]
    end

    subgraph "Production"
        PROD_LB[Load Balancer]
        PROD_API1[API Service 1]
        PROD_API2[API Service 2]
        PROD_DB_PRIMARY[(Primary DB)]
        PROD_DB_REPLICA[(Read Replica)]
        PROD_REDIS[(Redis Cluster)]
    end

    DEV_API --> DEV_DB
    STAGE_API --> STAGE_DB
    
    PROD_LB --> PROD_API1
    PROD_LB --> PROD_API2
    PROD_API1 --> PROD_DB_PRIMARY
    PROD_API2 --> PROD_DB_PRIMARY
    PROD_API1 --> PROD_REDIS
    PROD_API2 --> PROD_REDIS
    PROD_DB_PRIMARY --> PROD_DB_REPLICA
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **ORM**: SQLModel (SQLAlchemy 2.0)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Task Queue**: Celery (optional)

### Development & DevOps
- **Package Management**: Poetry
- **Code Quality**: Black, Ruff, mypy
- **Testing**: pytest, pytest-cov
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + Docker Compose

### Monitoring & Observability
- **Logging**: Structured logging with structlog
- **Metrics**: Prometheus (future)
- **Tracing**: OpenTelemetry (future)
- **Health Checks**: Built-in health endpoints

## API Design

### RESTful Endpoints
```
GET    /healthz              - Health check
GET    /api/v1/patients      - List patients
POST   /api/v1/patients      - Create patient
GET    /api/v1/patients/{id} - Get patient details
PUT    /api/v1/patients/{id} - Update patient
DELETE /api/v1/patients/{id} - Delete patient (soft delete)
```

### Data Models
- Patient management
- Medical records
- User authentication
- Audit trails
- AI diagnostic results

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Database read replicas
- Redis clustering
- Container orchestration ready

### Performance Optimization
- Database indexing strategy
- Redis caching layer
- Async/await throughout
- Connection pooling

### Future Enhancements
- Microservices decomposition
- Event-driven architecture
- CQRS pattern implementation
- GraphQL API gateway