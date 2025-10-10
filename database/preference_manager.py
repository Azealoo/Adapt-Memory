"""
Preference manager that integrates with the existing ADAPT system
"""
from typing import List, Optional, Dict, Any
from database.services import PreferenceService, DatabaseManager
from database.config import SessionLocal

class AdaptPreferenceManager:
    """
    Preference manager that integrates with the existing ADAPT system
    Provides backward compatibility with the existing preference system
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.preference_service = self.db_manager.get_preference_service()
    
    def get_preference_list(self, persona_id: str) -> List[str]:
        """
        Get preference list for a persona (compatible with existing system)
        Returns list of preference strings as expected by the existing code
        """
        user = self.preference_service.get_user(persona_id)
        if not user:
            return []
        
        preferences = self.preference_service.get_user_preferences(user.id)
        return [pref.preference_value for pref in preferences if pref.is_active]
    
    def add_preference_from_interaction(
        self,
        persona_id: str,
        task: str,
        robot_action: str,
        user_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add preference learned from user interaction
        """
        user = self.preference_service.get_or_create_user(persona_id)
        
        # Log the interaction
        interaction = self.preference_service.log_interaction(
            user_id=user.id,
            task=task,
            interaction_type="feedback",
            robot_action=robot_action,
            user_response=user_response,
            context=context
        )
        
        # Try to extract preference from user response
        self._extract_and_store_preference(user.id, user_response, interaction.id)
    
    def _extract_and_store_preference(
        self,
        user_id: int,
        user_response: str,
        interaction_id: int
    ) -> None:
        """
        Extract preference from user response and store it
        This is a simple implementation - could be enhanced with NLP
        """
        # Simple keyword-based preference extraction
        response_lower = user_response.lower()
        
        # Extract preference type and key based on keywords
        if any(word in response_lower for word in ["breakfast", "morning", "cereal", "toast"]):
            preference_type = "breakfast"
            preference_key = "breakfast_preference"
        elif any(word in response_lower for word in ["cooking", "cook", "prepare", "make"]):
            preference_type = "cooking_style"
            preference_key = "cooking_preference"
        elif any(word in response_lower for word in ["dietary", "allergy", "vegetarian", "vegan"]):
            preference_type = "dietary"
            preference_key = "dietary_restriction"
        elif any(word in response_lower for word in ["communication", "ask", "tell", "inform"]):
            preference_type = "communication"
            preference_key = "communication_style"
        else:
            preference_type = "general"
            preference_key = "general_preference"
        
        # Store the preference
        self.preference_service.add_preference(
            user_id=user_id,
            preference_type=preference_type,
            preference_key=preference_key,
            preference_value=user_response,
            confidence_score=0.8,  # Medium confidence for extracted preferences
            source="extracted_from_interaction"
        )
    
    def get_privileged_summary(self, persona_id: str) -> str:
        """
        Get privileged summary for a persona (compatible with existing system)
        Returns formatted string as expected by the existing code
        """
        user = self.preference_service.get_user(persona_id)
        if not user:
            return f"You have no prior information about {persona_id}."
        
        preferences_summary = self.preference_service.get_preference_summary(user.id)
        return f"You know the following about {persona_id}'s preferences.\n{preferences_summary}"
    
    def log_task_completion(
        self,
        persona_id: str,
        task: str,
        success: bool,
        completion_time: Optional[float] = None,
        steps_taken: int = 0,
        final_reward: Optional[float] = None,
        task_description: Optional[str] = None
    ) -> None:
        """
        Log task completion for analysis
        """
        user = self.preference_service.get_or_create_user(persona_id)
        
        self.preference_service.log_task_completion(
            user_id=user.id,
            task_name=task,
            success=success,
            completion_time=completion_time,
            steps_taken=steps_taken,
            final_reward=final_reward,
            task_description=task_description
        )
    
    def get_user_stats(self, persona_id: str) -> Dict[str, Any]:
        """
        Get user statistics
        """
        user = self.preference_service.get_user(persona_id)
        if not user:
            return {"error": "User not found"}
        
        preferences = self.preference_service.get_user_preferences(user.id)
        interactions = self.preference_service.get_user_interactions(user.id, limit=100)
        task_history = self.preference_service.get_task_history(user.id, limit=50)
        
        return {
            "persona_id": persona_id,
            "total_preferences": len(preferences),
            "total_interactions": len(interactions),
            "total_tasks": len(task_history),
            "successful_tasks": len([t for t in task_history if t.success]),
            "preference_types": list(set([p.preference_type for p in preferences])),
            "last_interaction": interactions[0].created_at if interactions else None,
            "last_task": task_history[0].created_at if task_history else None
        }
    
    def close(self):
        """Close database connections"""
        self.db_manager.close()

# Global instance for easy access
_preference_manager = None

def get_preference_manager() -> AdaptPreferenceManager:
    """Get global preference manager instance"""
    global _preference_manager
    if _preference_manager is None:
        _preference_manager = AdaptPreferenceManager()
    return _preference_manager

def close_preference_manager():
    """Close global preference manager"""
    global _preference_manager
    if _preference_manager:
        _preference_manager.close()
        _preference_manager = None
