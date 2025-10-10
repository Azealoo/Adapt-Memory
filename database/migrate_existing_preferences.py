"""
Migration script to move existing preferences from files to database
"""
import os
import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from database.config import engine, Base
from database.services import PreferenceService
from database.config import SessionLocal
from env.reward_models.persona_rewards.get_preference_list import get_preference_list

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def migrate_persona_preferences():
    """Migrate existing persona preferences to database"""
    db = SessionLocal()
    preference_service = PreferenceService(db)
    
    # List of known personas from the existing system
    personas = ["Juan", "Rachel", "Ramesh", "Ethan"]
    
    for persona in personas:
        print(f"Migrating preferences for {persona}...")
        
        try:
            # Get or create user
            user = preference_service.get_or_create_user(persona, f"{persona} Persona")
            
            # Get existing preferences from the old system
            try:
                preferences_list = get_preference_list(persona_id=persona)
                
                for i, preference_text in enumerate(preferences_list):
                    # Parse preference text to extract type and key
                    preference_type = "general"
                    preference_key = f"preference_{i+1}"
                    
                    # Try to categorize preferences based on content
                    if any(word in preference_text.lower() for word in ["breakfast", "morning", "cereal", "toast", "coffee"]):
                        preference_type = "breakfast"
                        preference_key = "breakfast_preference"
                    elif any(word in preference_text.lower() for word in ["cooking", "cook", "prepare", "make"]):
                        preference_type = "cooking_style"
                        preference_key = "cooking_preference"
                    elif any(word in preference_text.lower() for word in ["dietary", "allergy", "vegetarian", "vegan"]):
                        preference_type = "dietary"
                        preference_key = "dietary_restriction"
                    elif any(word in preference_text.lower() for word in ["communication", "ask", "tell", "inform"]):
                        preference_type = "communication"
                        preference_key = "communication_style"
                    
                    # Add preference to database
                    preference_service.add_preference(
                        user_id=user.id,
                        preference_type=preference_type,
                        preference_key=preference_key,
                        preference_value=preference_text,
                        confidence_score=1.0,
                        source="migrated_from_files"
                    )
                
                print(f"Successfully migrated {len(preferences_list)} preferences for {persona}")
                
            except Exception as e:
                print(f"Error getting preferences for {persona}: {e}")
                continue
                
        except Exception as e:
            print(f"Error migrating {persona}: {e}")
            continue
    
    db.close()
    print("Migration completed!")

def create_preference_templates():
    """Create common preference templates"""
    db = SessionLocal()
    preference_service = PreferenceService(db)
    
    templates = [
        {
            "template_name": "breakfast_preference",
            "preference_type": "breakfast",
            "template_text": "I prefer {preference} for breakfast"
        },
        {
            "template_name": "cooking_style",
            "preference_type": "cooking_style", 
            "template_text": "I like my food {preference}"
        },
        {
            "template_name": "dietary_restriction",
            "preference_type": "dietary",
            "template_text": "I have dietary restrictions: {preference}"
        },
        {
            "template_name": "communication_style",
            "preference_type": "communication",
            "template_text": "I prefer {preference} communication"
        }
    ]
    
    for template_data in templates:
        try:
            preference_service.create_preference_template(**template_data)
            print(f"Created template: {template_data['template_name']}")
        except Exception as e:
            print(f"Error creating template {template_data['template_name']}: {e}")
    
    db.close()

def main():
    """Main migration function"""
    print("Starting migration of existing preferences...")
    
    # Create database tables
    create_tables()
    
    # Migrate existing preferences
    migrate_persona_preferences()
    
    # Create preference templates
    create_preference_templates()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    main()
