# Adapt-Memory Database Schema (Research-Optimized)

This document describes the research-optimized database schema for the Adapt-Memory preference learning system.

## Overview

The database is designed for research purposes to store persona preferences, interactions, and task history for the ADAPT (Actively Discovering and Adapting to Preferences for any Task) research system. This schema is optimized for research use with synthetic personas (Juan, Rachel, Ramesh, Ethan).

## Database Tables (Research-Optimized)

### 1. Users Table (Research Personas) - Simplified

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    persona_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_persona_id ON users(persona_id);
```

**Fields:**
- `id`: Primary key (auto-increment)
- `persona_id`: Unique identifier for the research persona (e.g., "Juan", "Rachel", "Ramesh", "Ethan")
- `name`: Human-readable persona name
- `created_at`: Timestamp when persona was created

**Removed for Research:**
- ~~`email`~~ - Not needed for synthetic personas
- ~~`updated_at`~~ - Research personas don't change
- ~~`is_active`~~ - Research personas are always active during experiments

### 2. User Preferences Table (Persona Preferences) - Simplified

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_type VARCHAR(100) NOT NULL,
    preference_key VARCHAR(200) NOT NULL,
    preference_value TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    source VARCHAR(100) DEFAULT 'user_feedback',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_type ON user_preferences(preference_type);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to users table
- `preference_type`: Category of preference (e.g., "breakfast", "cooking_style", "dietary")
- `preference_key`: Specific preference identifier
- `preference_value`: The actual preference text
- `confidence_score`: Confidence level (0.0 to 1.0) - **Important for research**
- `source`: How the preference was learned
- `created_at`: When preference was added

**Removed for Research:**
- ~~`updated_at`~~ - Research preferences are typically immutable
- ~~`is_active`~~ - Research preferences are always active

### 3. User Interactions Table (Persona-Robot Interactions) - Simplified

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
- `user_response`: Persona's response
- `context`: Additional context as JSON
- `reward_score`: Reward/feedback score
- `created_at`: When interaction occurred

### 4. Task History Table (Research Task Performance) - Simplified

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

### 5. Preference Templates Table - Simplified

```sql
CREATE TABLE preference_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(200) UNIQUE NOT NULL,
    preference_type VARCHAR(100) NOT NULL,
    template_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_preference_templates_type ON preference_templates(preference_type);
```

**Fields:**
- `id`: Primary key
- `template_name`: Unique template identifier
- `preference_type`: Category this template belongs to
- `template_text`: Template text with placeholders
- `created_at`: When template was created

**Removed for Research:**
- ~~`is_active`~~ - Research templates are always active

## Research-Optimized Benefits

### **Simplified Schema:**
- ✅ **Removed unnecessary fields** for research context
- ✅ **Focused on research metrics** (confidence scores, reward scores)
- ✅ **Streamlined for synthetic personas**
- ✅ **Optimized for research queries**

### **Research-Focused Features:**
- ✅ **Confidence scoring** for preference learning analysis
- ✅ **Reward tracking** for performance evaluation
- ✅ **Interaction logging** for behavior analysis
- ✅ **Task completion metrics** for research evaluation

### **Removed Complexity:**
- ❌ Email addresses (not needed for synthetic personas)
- ❌ Update timestamps (research personas are static)
- ❌ Active/inactive flags (research personas are always active)
- ❌ Complex user management (simple persona tracking)

## Sample Research Data

### Users (Research Personas)
```sql
INSERT INTO users (persona_id, name) VALUES 
('Juan', 'Juan Research Persona'),
('Rachel', 'Rachel Research Persona'),
('Ramesh', 'Ramesh Research Persona'),
('Ethan', 'Ethan Research Persona');
```

### Research Queries

```sql
-- Get preference learning progress for research
SELECT 
    persona_id,
    COUNT(*) as total_preferences,
    AVG(confidence_score) as avg_confidence,
    COUNT(DISTINCT preference_type) as preference_diversity
FROM users u
JOIN user_preferences up ON u.id = up.user_id
GROUP BY persona_id;

-- Get task performance metrics for research
SELECT 
    persona_id,
    COUNT(*) as total_tasks,
    AVG(completion_time) as avg_completion_time,
    AVG(final_reward) as avg_reward,
    COUNT(CASE WHEN success = TRUE THEN 1 END) as success_rate
FROM users u
JOIN task_history th ON u.id = th.user_id
GROUP BY persona_id;
```

This research-optimized schema removes unnecessary complexity while maintaining all the features needed for preference learning research!
