"""
Service layer for database operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import User, UserPreference, UserInteraction, TaskHistory, PreferenceTemplate
from database.config import get_db

class PreferenceService:
    """Service class for managing user preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User management
    def create_user(self, persona_id: str, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(persona_id=persona_id, name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user(self, persona_id: str) -> Optional[User]:
        """Get user by persona_id"""
        return self.db.query(User).filter(User.persona_id == persona_id).first()
    
    def get_or_create_user(self, persona_id: str, name: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        user = self.get_user(persona_id)
        if not user:
            user = self.create_user(persona_id, name)
        return user
    
    # Preference management
    def add_preference(
        self, 
        user_id: int, 
        preference_type: str, 
        preference_key: str, 
        preference_value: str,
        confidence_score: float = 1.0,
        source: str = "user_feedback"
    ) -> UserPreference:
        """Add or update a user preference"""
        # Check if preference already exists
        existing = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == preference_type,
                UserPreference.preference_key == preference_key,
                UserPreference.is_active == True
            )
        ).first()
        
        if existing:
            # Update existing preference
            existing.preference_value = preference_value
            existing.confidence_score = confidence_score
            existing.source = source
            self.db.commit()
            return existing
        else:
            # Create new preference
            preference = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_key=preference_key,
                preference_value=preference_value,
                confidence_score=confidence_score,
                source=source
            )
            self.db.add(preference)
            self.db.commit()
            self.db.refresh(preference)
            return preference
    
    def get_user_preferences(self, user_id: int, preference_type: Optional[str] = None) -> List[UserPreference]:
        """Get all preferences for a user"""
        query = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.is_active == True
            )
        )
        
        if preference_type:
            query = query.filter(UserPreference.preference_type == preference_type)
        
        return query.all()
    
    def get_preference_summary(self, user_id: int) -> str:
        """Get a formatted summary of user preferences"""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return "No preferences recorded yet."
        
        # Group by preference type
        grouped = {}
        for pref in preferences:
            if pref.preference_type not in grouped:
                grouped[pref.preference_type] = []
            grouped[pref.preference_type].append(f"{pref.preference_key}: {pref.preference_value}")
        
        summary_parts = []
        for pref_type, prefs in grouped.items():
            summary_parts.append(f"{pref_type.replace('_', ' ').title()}:")
            for pref in prefs:
                summary_parts.append(f"  - {pref}")
        
        return "\n".join(summary_parts)
    
    def update_preference_confidence(self, preference_id: int, confidence_score: float):
        """Update the confidence score of a preference"""
        preference = self.db.query(UserPreference).filter(UserPreference.id == preference_id).first()
        if preference:
            preference.confidence_score = confidence_score
            self.db.commit()
    
    def deactivate_preference(self, preference_id: int):
        """Deactivate a preference (soft delete)"""
        preference = self.db.query(UserPreference).filter(UserPreference.id == preference_id).first()
        if preference:
            preference.is_active = False
            self.db.commit()
    
    # Interaction management
    def log_interaction(
        self,
        user_id: int,
        task: str,
        interaction_type: str,
        robot_action: Optional[str] = None,
        user_response: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        reward_score: Optional[float] = None,
        preference_id: Optional[int] = None
    ) -> UserInteraction:
        """Log a user interaction"""
        interaction = UserInteraction(
            user_id=user_id,
            preference_id=preference_id,
            task=task,
            interaction_type=interaction_type,
            robot_action=robot_action,
            user_response=user_response,
            context=context,
            reward_score=reward_score
        )
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction
    
    def get_user_interactions(self, user_id: int, limit: int = 100) -> List[UserInteraction]:
        """Get recent interactions for a user"""
        return self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).order_by(UserInteraction.created_at.desc()).limit(limit).all()
    
    # Task history
    def log_task_completion(
        self,
        user_id: int,
        task_name: str,
        success: bool,
        completion_time: Optional[float] = None,
        steps_taken: int = 0,
        preferences_used: Optional[List[int]] = None,
        final_reward: Optional[float] = None,
        task_description: Optional[str] = None
    ) -> TaskHistory:
        """Log task completion"""
        task_history = TaskHistory(
            user_id=user_id,
            task_name=task_name,
            task_description=task_description,
            success=success,
            completion_time=completion_time,
            steps_taken=steps_taken,
            preferences_used=preferences_used,
            final_reward=final_reward
        )
        self.db.add(task_history)
        self.db.commit()
        self.db.refresh(task_history)
        return task_history
    
    def get_task_history(self, user_id: int, limit: int = 50) -> List[TaskHistory]:
        """Get task history for a user"""
        return self.db.query(TaskHistory).filter(
            TaskHistory.user_id == user_id
        ).order_by(TaskHistory.created_at.desc()).limit(limit).all()
    
    # Preference templates
    def create_preference_template(
        self,
        template_name: str,
        preference_type: str,
        template_text: str
    ) -> PreferenceTemplate:
        """Create a preference template"""
        template = PreferenceTemplate(
            template_name=template_name,
            preference_type=preference_type,
            template_text=template_text
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def get_preference_templates(self, preference_type: Optional[str] = None) -> List[PreferenceTemplate]:
        """Get preference templates"""
        query = self.db.query(PreferenceTemplate).filter(PreferenceTemplate.is_active == True)
        if preference_type:
            query = query.filter(PreferenceTemplate.preference_type == preference_type)
        return query.all()

class DatabaseManager:
    """High-level database manager"""
    
    def __init__(self):
        self.db = next(get_db())
        self.preference_service = PreferenceService(self.db)
    
    def get_preference_service(self) -> PreferenceService:
        """Get preference service instance"""
        return self.preference_service
    
    def close(self):
        """Close database connection"""
        self.db.close()
