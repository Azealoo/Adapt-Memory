# Adapt-Memory Database Setup

This document explains how to set up and use the database system for storing user preferences in the Adapt-Memory project.

## Overview

The database system provides persistent storage for user preferences, interactions, and task history. It supports both local PostgreSQL and Neon cloud database, with backward compatibility to the existing file-based preference system.

## Features

- **Persistent Storage**: User preferences are stored in a PostgreSQL database
- **Cloud Support**: Works with Neon cloud database for easy deployment
- **Backward Compatibility**: Existing file-based preferences are migrated automatically
- **Rich Analytics**: Track user interactions, task completion, and preference learning
- **Flexible Schema**: Support for different preference types and confidence scores

## Database Schema

### Core Tables

- **users**: Store user/persona information
- **user_preferences**: Individual preference entries with confidence scores
- **user_interactions**: Log of all user-robot interactions
- **task_history**: Record of completed tasks and performance
- **preference_templates**: Reusable preference templates

## Quick Start

### 1. Install Dependencies

```bash
# Install database requirements
pip install -r requirements_db.txt

# Or run the setup script
python setup_database.py
```

### 2. Configure Database

Copy the environment template and configure your database:

```bash
cp env_example.txt .env
```

Edit `.env` with your database configuration:

```env
# For local PostgreSQL
ADAPT_DB_HOST=localhost
ADAPT_DB_PORT=5432
ADAPT_DB_NAME=adapt_memory
ADAPT_DB_USER=postgres
ADAPT_DB_PASSWORD=your_password

# For Neon cloud database (alternative)
ADAPT_NEON_DATABASE_URL=postgresql://username:password@hostname/database?sslmode=require
```

### 3. Test Database Connection

```bash
python database/test_database.py
```

### 4. Migrate Existing Preferences

```bash
python database/migrate_existing_preferences.py
```

## Usage

### Basic Usage

```python
from database.preference_manager import get_preference_manager

# Get preference manager
manager = get_preference_manager()

# Get preferences for a persona (compatible with existing system)
preferences = manager.get_preference_list("Juan")

# Get privileged summary
summary = manager.get_privileged_summary("Juan")

# Log task completion
manager.log_task_completion(
    persona_id="Juan",
    task="Make coffee",
    success=True,
    completion_time=120.5,
    final_reward=45.0
)
```

### Enhanced LLMAgent Integration

```python
from src.LLMAgent_Database import LLMAgent_Persona_Database

# Create persona with database support
persona = LLMAgent_Persona_Database(
    persona_id="Juan",
    model_name_base="your_model",
    skip_persona_syntax_failures=False,
    temperature_persona=0.7,
    use_database=True  # Enable database integration
)

# Use as normal - database integration is automatic
summary = persona.get_privileged_summary()
```

### Direct Database Operations

```python
from database.services import PreferenceService
from database.config import SessionLocal

# Get database session
db = SessionLocal()
service = PreferenceService(db)

# Add preference
preference = service.add_preference(
    user_id=1,
    preference_type="breakfast",
    preference_key="coffee_preference",
    preference_value="I prefer strong black coffee",
    confidence_score=1.0
)

# Get user preferences
preferences = service.get_user_preferences(user_id=1)
```

## Database Configuration Options

### Local PostgreSQL

1. Install PostgreSQL locally
2. Create database: `createdb adapt_memory`
3. Configure connection in `.env`

### Neon Cloud Database

1. Sign up at [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string to `.env` as `ADAPT_NEON_DATABASE_URL`

### Connection Pool Settings

```env
ADAPT_POOL_SIZE=5          # Number of connections in pool
ADAPT_MAX_OVERFLOW=10       # Additional connections beyond pool_size
ADAPT_POOL_TIMEOUT=30       # Timeout for getting connection
ADAPT_POOL_RECYCLE=3600     # Recycle connections after 1 hour
```

## Migration from File-Based System

The migration script automatically:

1. Creates database tables
2. Migrates existing persona preferences from files
3. Creates preference templates
4. Maintains backward compatibility

Run migration:
```bash
python database/migrate_existing_preferences.py
```

## API Reference

### PreferenceService

- `add_preference()`: Add or update user preference
- `get_user_preferences()`: Get all preferences for a user
- `get_preference_summary()`: Get formatted preference summary
- `log_interaction()`: Log user-robot interaction
- `log_task_completion()`: Log task completion

### AdaptPreferenceManager

- `get_preference_list()`: Get preferences (compatible with existing system)
- `get_privileged_summary()`: Get privileged summary
- `add_preference_from_interaction()`: Learn from user interaction
- `get_user_stats()`: Get user statistics

## Testing

Run the test suite:
```bash
python database/test_database.py
```

The test suite verifies:
- Database connection
- Table creation
- CRUD operations
- Integration with existing system

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in `.env`
   - Ensure PostgreSQL is running
   - Verify network connectivity for cloud databases

2. **Migration Failed**
   - Check file permissions
   - Ensure existing preference files are accessible
   - Verify database connection

3. **Import Errors**
   - Install requirements: `pip install -r requirements_db.txt`
   - Check Python path configuration

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- Use connection pooling for production
- Index frequently queried columns
- Consider read replicas for high-traffic scenarios
- Monitor database performance metrics

## Security

- Use environment variables for sensitive configuration
- Enable SSL for production databases
- Implement proper access controls
- Regular security updates

## Contributing

When adding new features:

1. Update database models if needed
2. Add corresponding service methods
3. Update tests
4. Document new functionality

## License

Same as the main Adapt-Memory project.
