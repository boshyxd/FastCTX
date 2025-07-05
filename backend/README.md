# Neo4j Python Docker Setup

This project provides a Docker Compose setup for running a Neo4j database with a Python application using uv for package management.

## Services

- **Neo4j Database**: Community edition with APOC plugin
- **Python Application**: Sample application that connects to Neo4j

## Quick Start

1. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

2. **Access Neo4j Browser:**
   - URL: http://localhost:7474
   - Username: `neo4j`
   - Password: `password123`

3. **Check the Python application logs:**
   ```bash
   docker-compose logs -f python-app
   ```

## Configuration

### Neo4j
- **HTTP Port**: 7474
- **Bolt Port**: 7687
- **Username**: neo4j
- **Password**: password123 (change this in production!)

### Python Application
- **Port**: 8000
- **Environment Variables**:
  - `NEO4J_URI`: bolt://neo4j:7687
  - `NEO4J_USER`: neo4j
  - `NEO4J_PASSWORD`: password123

## Development

The Python application uses uv for package management. To add new dependencies:

```bash
uv add package-name
```

Then rebuild the Docker container:
```bash
docker-compose up --build python-app
```

## Useful Commands

```bash
# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build python-app

# Execute commands in running container
docker-compose exec python-app bash
docker-compose exec neo4j cypher-shell -u neo4j -p password123
```

## Production Notes

- Change the default Neo4j password
- Use environment variables for sensitive configuration
- Consider using named volumes for data persistence
- Review security settings for production deployment
