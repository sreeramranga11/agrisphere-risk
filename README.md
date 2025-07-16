# Precision Risk for Agriculture

## Overview
A precision agriculture risk assessment system that leverages Palantir Foundry and AIP API to provide hyper-local crop insurance underwriting. This system integrates geospatial data, weather patterns, and AI to deliver accurate risk scoring at the individual farm level.

## Key Features
- **Digital Farm Ontology**: High-resolution data integration for satellite imagery, weather data, topography, and historical yields
- **Micro-Climate Risk Engine**: AI-powered field-level risk scoring for various perils (drought, flood, pestilence)
- **Automated Damage Assessment**: Real-time satellite imagery analysis for post-event damage estimation
- **Premium Optimization**: Algorithm-driven insurance premium calculation based on hyper-local risk factors
- **Underwriter's Workbench**: Interactive dashboard for insurance professionals

## Architecture
```
agrisphere-risk/
├── frontend/                 # React-based user interface
├── backend/                  # Python FastAPI backend
├── palantir-integration/     # Foundry and AIP API integration
├── ai-models/               # Risk assessment and damage detection models
├── data-pipelines/          # Data ingestion and processing
├── docs/                    # Documentation
└── deployment/              # Docker and deployment configs
```

## Technology Stack
- **Frontend**: React, TypeScript, Mapbox GL JS, Material-UI
- **Backend**: Python FastAPI, PostgreSQL, Redis
- **AI/ML**: TensorFlow, OpenCV, scikit-learn
- **Geospatial**: GDAL, GeoPandas, PostGIS
- **Palantir**: Foundry Platform, AIP API
- **Data Sources**: NOAA, USDA, Satellite APIs

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL with PostGIS extension
- Redis
- Palantir Foundry access
- Palantir AIP API access

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd agrisphere-risk
```

### 2. Environment Configuration

Create environment files for the backend:

```bash
# Backend environment
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://agrisphere_user:agrisphere_password@localhost:5432/agrisphere_risk
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secure-secret-key-here

# Palantir Configuration
FOUNDRY_URL=https://your-foundry-instance.palantirfoundry.com
FOUNDRY_TOKEN=your-foundry-token
FOUNDRY_DATASET_ID=your-dataset-id

AIP_API_URL=https://your-aip-instance.palantirfoundry.com
AIP_API_TOKEN=your-aip-token

# External APIs
NOAA_API_KEY=your-noaa-api-key
USDA_API_KEY=your-usda-api-key
SATELLITE_API_KEY=your-satellite-api-key
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## API Endpoints

### Farms
- `GET /api/v1/farms` - List all farms
- `POST /api/v1/farms` - Create new farm
- `GET /api/v1/farms/{id}` - Get farm details
- `PUT /api/v1/farms/{id}` - Update farm
- `DELETE /api/v1/farms/{id}` - Delete farm

### Risk Assessment
- `POST /api/v1/risk/assess/{farm_id}` - Assess farm risk
- `GET /api/v1/risk/assess/{farm_id}/latest` - Get latest assessment
- `GET /api/v1/risk/assess/{farm_id}/history` - Get assessment history
- `POST /api/v1/risk/assess/batch` - Batch risk assessment
- `GET /api/v1/risk/portfolio/summary` - Portfolio summary

### Weather Data
- `GET /api/v1/weather/stations` - List weather stations
- `GET /api/v1/weather/data/{station_id}` - Get weather data
- `GET /api/v1/weather/forecast/{lat}/{lon}` - Get weather forecast

### Damage Analysis
- `POST /api/v1/damage/analyze` - Analyze crop damage
- `POST /api/v1/damage/satellite-analysis` - Satellite damage analysis
- `GET /api/v1/damage/history/{farm_id}` - Damage history

## Palantir Integration

### Foundry Configuration

1. **Dataset Setup**: Create datasets in Foundry for:
   - Satellite imagery
   - Weather data
   - Soil data
   - Historical farm data

2. **API Access**: Configure API tokens and endpoints

3. **Data Pipeline**: Set up data ingestion pipelines

### AIP Configuration

1. **Model Deployment**: Deploy risk assessment models
2. **API Endpoints**: Configure AIP API endpoints
3. **Authentication**: Set up API authentication

## Database Schema

### Core Tables

- **farms**: Farm information with geospatial data
- **farm_assessments**: Historical risk assessments
- **weather_stations**: Weather station locations
- **weather_data**: Historical weather data
- **climate_events**: Significant climate events

### Geospatial Features

- PostGIS extension for spatial operations
- Farm boundaries stored as polygons
- Weather station locations as points
- Spatial indexing for performance

## Monitoring and Logging

### Application Logs

```bash
# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec postgres psql -U agrisphere_user -d agrisphere_risk

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public';
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **API Keys**: Rotate API keys regularly
3. **Database**: Use strong passwords and limit access
4. **Network**: Configure firewalls and VPN access
5. **SSL/TLS**: Enable HTTPS in production

## Production Deployment

### Environment Variables

Set production environment variables:

```env
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/agrisphere_risk
SECRET_KEY=production-secret-key
```

### Scaling

- Use multiple backend instances behind a load balancer
- Configure Redis clustering for caching
- Set up database read replicas
- Use CDN for static assets

### Monitoring

- Set up application performance monitoring (APM)
- Configure log aggregation
- Set up alerting for critical metrics
- Monitor database performance

## Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL is running and accessible
2. **Redis Connection**: Verify Redis service is healthy
3. **Palantir API**: Check API tokens and network connectivity
4. **Geospatial Data**: Ensure PostGIS extension is enabled

### Debug Commands

```bash
# Check service health
docker-compose ps

# View detailed logs
docker-compose logs backend

# Test database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check API health
curl http://localhost:8000/health
```

## Development Roadmap

### Phase 1: Foundation (Current)
- ✅ Basic project structure
- ✅ Database models and schemas
- ✅ API endpoints
- ✅ Frontend dashboard
- ✅ Docker containerization

### Phase 2: AI Integration
- [ ] Real Palantir Foundry integration
- [ ] AIP model deployment
- [ ] Satellite imagery processing
- [ ] Advanced risk algorithms

### Phase 3: Advanced Features
- [ ] Real-time weather integration
- [ ] Automated damage detection
- [ ] Premium optimization
- [ ] Mobile application

### Phase 4: Scale & Optimize
- [ ] Performance optimization
- [ ] Advanced analytics
- [ ] Multi-region support
- [ ] Enterprise features

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review application logs
3. Consult API documentation
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.