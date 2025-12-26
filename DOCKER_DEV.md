# Docker Development Guide

This guide explains how to use Docker Compose with auto-reload functionality for efficient development.

## Quick Start

```bash
# Set your API key
export GEMINI_API_KEY=your_key_here

# Start all services with auto-reload
docker-compose up --build
```

That's it! Now you can edit code and see changes automatically reload.

## What's Enabled

### Backend Auto-Reload

The backend service uses uvicorn's `--reload` flag and mounts your source code:

- **Volume Mount**: `./backend/app:/app/app`
- **Command**: `uvicorn app.main:app --reload`
- **Debug Mode**: Enabled for better error messages

**Changes trigger reload:**
- `.py` files in `backend/app/`
- API routes, models, services, etc.

### Frontend Hot Reload

The frontend uses Next.js development server with hot module replacement:

- **Volume Mounts**:
  - `./frontend/src:/app/src` (source code)
  - `./frontend/public:/app/public` (static assets)
- **Command**: `npm run dev`
- **HMR**: Automatic browser refresh on file changes

**Changes trigger reload:**
- `.tsx`, `.ts`, `.jsx`, `.js` files in `frontend/src/`
- CSS, SCSS files
- Public assets

## Development Workflow

### Starting Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Making Changes

1. Edit files in `backend/app/` or `frontend/src/`
2. Save the file
3. Changes automatically reload:
   - Backend: ~1-2 seconds
   - Frontend: ~1-2 seconds (browser auto-refreshes)

### Rebuilding

If you change dependencies, rebuild:

```bash
# Rebuild all services
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Stopping Services

```bash
# Stop services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

## File Structure

```
simple_rag/
├── docker-compose.yml       # Development config (auto-reload)
├── docker-compose.prod.yml  # Production config (optimized)
├── backend/
│   ├── Dockerfile           # Production image
│   └── app/                 # Mounted for auto-reload
└── frontend/
    ├── Dockerfile           # Production image
    ├── Dockerfile.dev       # Development image
    └── src/                 # Mounted for auto-reload
```

## Production Deployment

For production, use the optimized configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Differences:**
- No volume mounts for source code
- Multi-stage builds for smaller images
- No debug mode
- Optimized for performance, not reload speed

## Troubleshooting

### Changes Not Reloading

**Backend:**
```bash
# Check if volume is mounted
docker-compose exec backend ls -la /app/app

# Check uvicorn is running with --reload
docker-compose exec backend ps aux | grep uvicorn
```

**Frontend:**
```bash
# Check if volume is mounted
docker-compose exec frontend ls -la /app/src

# Check Next.js dev server is running
docker-compose exec frontend ps aux | grep next
```

### Permission Issues

If you encounter permission errors:

```bash
# Fix ownership (Linux/Mac)
sudo chown -R $USER:$USER backend/app frontend/src
```

### Port Conflicts

If ports 3000 or 8000 are in use:

```bash
# Check what's using the port
lsof -ti:3000
lsof -ti:8000

# Kill the process
lsof -ti:3000 | xargs kill -9
```

### Clean Rebuild

If something seems broken:

```bash
# Nuclear option: clean everything and rebuild
docker-compose down -v
docker system prune -f
docker-compose up --build
```

## Performance Tips

1. **Use bind mounts wisely**: Only mount directories that need auto-reload
2. **Exclude node_modules**: The volumes configuration excludes these for performance
3. **Use .dockerignore**: Excludes unnecessary files from build context
4. **Keep dependencies in image**: Don't mount dependency folders

## Best Practices

1. **Development**: Always use `docker-compose.yml` (auto-reload enabled)
2. **Production**: Always use `docker-compose.prod.yml` (optimized)
3. **Commit often**: Changes are live, easy to break things
4. **Test in production mode**: Before deploying, test with production config
5. **Monitor logs**: Keep `docker-compose logs -f` running during development

## Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_key_here
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpassword
POSTGRES_DB=ragdb
```

Docker Compose automatically loads this file.

## Advanced Usage

### Run Commands in Container

```bash
# Backend shell
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Frontend shell
docker-compose exec frontend sh

# Run linter
docker-compose exec frontend npm run lint
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U raguser -d ragdb

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Multiple Instances

To run multiple instances (e.g., different projects):

```bash
# Use project name flag
docker-compose -p rag-dev up
docker-compose -p rag-staging up
```

## Support

Issues? Check [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md) for more information.
