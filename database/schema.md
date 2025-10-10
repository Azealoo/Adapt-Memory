# Adapt-Memory Database Schema

This document describes the complete database schema for the Adapt-Memory preference learning system.

## Overview

The database is designed to store persona preferences, interactions, and task history for the ADAPT (Actively Discovering and Adapting to Preferences for any Task) research system. In this research context, "users" are actually synthetic personas (Juan, Rachel, Ramesh, Ethan) created for studying preference learning in human-robot interaction. The system supports both local PostgreSQL and Neon cloud databases.

## Database Tables

### 1. Users Table (Research Personas)

Stores information about research personas in the ADAPT system. These are synthetic personas created for studying preference learning in human-robot interaction.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    persona_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_persona_id ON users(persona_id);
```

**Fields:**
- `id`: Primary key (auto-increment)
- `persona_id`: Unique identifier for the research persona (e.g., "Juan", "Rachel", "Ramesh", "Ethan")
- `name`: Human-readable persona name
- `email`: Contact email (optional, for research purposes)
- `created_at`: Timestamp when persona was created
- `updated_at`: Timestamp when persona was last updated
- `is_active`: Whether the persona is active in research

### 2. User Preferences Table (Persona Preferences)

Stores individual preference entries for research personas, with confidence scores for preference learning analysis.

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_type VARCHAR(100) NOT NULL,
    preference_key VARCHAR(200) NOT NULL,
    preference_value TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    source VARCHAR(100) DEFAULT 'user_feedback',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_type ON user_preferences(preference_type);
CREATE INDEX idx_user_preferences_active ON user_preferences(is_active);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to users table
- `preference_type`: Category of preference (e.g., "breakfast", "cooking_style", "dietary")
- `preference_key`: Specific preference identifier (e.g., "coffee_preference", "cooking_method")
- `preference_value`: The actual preference text
- `confidence_score`: Confidence level (0.0 to 1.0)
- `source`: How the preference was learned (e.g., "user_feedback", "migrated_from_files")
- `created_at`: When preference was added
- `updated_at`: When preference was last modified
- `is_active`: Whether preference is currently active

### 3. User Interactions Table (Persona-Robot Interactions)

Logs all persona-robot interactions for preference learning research and analysis.

```sql
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_id INTEGER REFERENCES user_preferences(id),
    task VARCHAR(500) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    robot_action TEXT,
    user_response TEXT,
    context JSONB,
    reward_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_user_interactions_created_at ON user_interactions(created_at);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to users table
- `preference_id`: Optional foreign key to related preference
- `task`: The task being performed
- `interaction_type`: Type of interaction (e.g., "question", "feedback", "correction")
- `robot_action`: What the robot did
- `user_response`: User's response
- `context`: Additional context as JSON
- `reward_score`: Reward/feedback score
- `created_at`: When interaction occurred

### 4. Task History Table (Research Task Performance)

Records completed tasks and performance metrics for research analysis.

```sql
CREATE TABLE task_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_name VARCHAR(500) NOT NULL,
    task_description TEXT,
    success BOOLEAN DEFAULT TRUE,
    completion_time FLOAT,
    steps_taken INTEGER DEFAULT 0,
    preferences_used JSONB,
    final_reward FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_task_history_user_id ON task_history(user_id);
CREATE INDEX idx_task_history_success ON task_history(success);
CREATE INDEX idx_task_history_created_at ON task_history(created_at);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to users table
- `task_name`: Name of the completed task
- `task_description`: Detailed task description
- `success`: Whether task was completed successfully
- `completion_time`: Time taken in seconds
- `steps_taken`: Number of steps required
- `preferences_used`: Array of preference IDs used
- `final_reward`: Final reward score
- `created_at`: When task was completed

### 5. Preference Templates Table

Stores reusable preference templates for common patterns.

```sql
CREATE TABLE preference_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(200) UNIQUE NOT NULL,
    preference_type VARCHAR(100) NOT NULL,
    template_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_preference_templates_type ON preference_templates(preference_type);
CREATE INDEX idx_preference_templates_active ON preference_templates(is_active);
```

**Fields:**
- `id`: Primary key
- `template_name`: Unique template identifier
- `preference_type`: Category this template belongs to
- `template_text`: Template text with placeholders
- `is_active`: Whether template is active
- `created_at`: When template was created

## Relationships

### Foreign Key Relationships

```
users (1) ──→ (many) user_preferences
users (1) ──→ (many) user_interactions  
users (1) ──→ (many) task_history
user_preferences (1) ──→ (many) user_interactions
```

### Relationship Details

1. **Users → User Preferences**: One user can have many preferences
2. **Users → User Interactions**: One user can have many interactions
3. **Users → Task History**: One user can have many task completions
4. **User Preferences → User Interactions**: One preference can be referenced by many interactions

## Data Types

### Preference Types
- `breakfast`: Morning meal preferences
- `cooking_style`: How food should be prepared
- `dietary`: Dietary restrictions and preferences
- `communication`: How the user prefers to communicate
- `general`: General preferences

### Interaction Types
- `question`: Robot asking user a question
- `feedback`: User providing feedback
- `correction`: User correcting robot behavior
- `confirmation`: User confirming robot action

### Sources
- `user_feedback`: Learned from direct user input
- `migrated_from_files`: Imported from existing file system
- `extracted_from_interaction`: Learned from conversation analysis
- `manual_entry`: Manually added by administrator

## Indexes

The schema includes several indexes for optimal query performance:

- **Primary Keys**: All tables have auto-incrementing primary keys
- **Foreign Keys**: Indexed for join performance
- **Search Fields**: `persona_id`, `preference_type`, `interaction_type`
- **Time-based**: `created_at` fields for temporal queries
- **Boolean Fields**: `is_active` for filtering active records

## Constraints

### Unique Constraints
- `users.persona_id`: Each persona must be unique
- `preference_templates.template_name`: Each template name must be unique

### Check Constraints
- `confidence_score`: Must be between 0.0 and 1.0
- `completion_time`: Must be positive
- `steps_taken`: Must be non-negative

### Not Null Constraints
- All primary keys
- All foreign keys
- `persona_id`, `preference_type`, `preference_key`, `preference_value`
- `task`, `interaction_type`

## Sample Data

### Users (Research Personas)
```sql
INSERT INTO users (persona_id, name) VALUES 
('Juan', 'Juan Research Persona'),
('Rachel', 'Rachel Research Persona'),
('Ramesh', 'Ramesh Research Persona'),
('Ethan', 'Ethan Research Persona');
```

### User Preferences
```sql
INSERT INTO user_preferences (user_id, preference_type, preference_key, preference_value, confidence_score) VALUES 
(1, 'breakfast', 'coffee_preference', 'I prefer strong black coffee', 1.0),
(1, 'cooking_style', 'eggs_preference', 'I like my eggs scrambled', 0.9),
(2, 'dietary', 'allergy', 'I am allergic to nuts', 1.0);
```

### Preference Templates
```sql
INSERT INTO preference_templates (template_name, preference_type, template_text) VALUES 
('breakfast_preference', 'breakfast', 'I prefer {preference} for breakfast'),
('cooking_style', 'cooking_style', 'I like my food {preference}'),
('dietary_restriction', 'dietary', 'I have dietary restrictions: {preference}');
```

## Query Examples

### Get all preferences for a user
```sql
SELECT preference_type, preference_key, preference_value, confidence_score
FROM user_preferences 
WHERE user_id = 1 AND is_active = TRUE
ORDER BY confidence_score DESC;
```

### Get user interaction history
```sql
SELECT task, interaction_type, robot_action, user_response, created_at
FROM user_interactions 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 10;
```

### Get task completion statistics
```sql
SELECT 
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN success = TRUE THEN 1 END) as successful_tasks,
    AVG(completion_time) as avg_completion_time,
    AVG(final_reward) as avg_reward
FROM task_history 
WHERE user_id = 1;
```

## Migration Notes

When migrating from the file-based system:

1. **Existing personas** are imported as users
2. **Preference files** are parsed and stored as user_preferences
3. **Confidence scores** start at 1.0 for migrated preferences
4. **Source field** is set to "migrated_from_files"
5. **Templates** are created for common preference patterns

## Performance Considerations

- **Connection Pooling**: Configured for production use
- **Indexes**: Optimized for common query patterns
- **JSON Fields**: Used for flexible context storage
- **Soft Deletes**: `is_active` flags instead of hard deletes
- **Timestamps**: All tables include creation timestamps

This schema provides a robust foundation for learning and storing user preferences while maintaining compatibility with the existing ADAPT system.
