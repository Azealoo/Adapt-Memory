"""
Enhanced LLMAgent_Persona with database integration
"""
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from src.LLMAgent import LLMAgent
from database.preference_manager import get_preference_manager, close_preference_manager
from env.reward_models.persona_rewards.get_preference_list import get_preference_list

class LLMAgent_Persona_Database(LLMAgent):
    """
    Enhanced LLMAgent_Persona that integrates with the database system
    Provides backward compatibility while adding database functionality
    """
    
    def __init__(self, persona_id, model_name_base, skip_persona_syntax_failures, temperature_persona, use_database=True, **kwargs):
        super().__init__(llm_runname=model_name_base)
        self.agent_name = persona_id
        self.use_database = use_database
        
        # Initialize database manager if using database
        if self.use_database:
            try:
                self.preference_manager = get_preference_manager()
            except Exception as e:
                print(f"Warning: Database not available, falling back to file-based preferences: {e}")
                self.use_database = False
                self.preference_manager = None
        else:
            self.preference_manager = None
        
        self.system_prompt = (
            f"You are teaching a household assistive robot in performing various assistive tasks in a manner {self.agent_name} would like. The robot may not know {self.agent_name}'s preferences, so your job is to guide the robot to perform the given task for {self.agent_name}. Be sure to guide the robot to make only those dishes that the task calls for, e.g. if the task is to make a waffle do not ask the robot to make other things, such as coffee. Answer direct questions regarding your preferences, and not the avilability or location of objects. In the latter case, encourage the robot to search and explore different locations. Even if the robot makes an irreversible error, be sure to provide a correction so that the robot does not repeat it's mistakes the next time."
            + f"\n\nGiven the current state of the house and what you know about {self.agent_name} and the task at hand, you will respond to the robot's last question concisely, and in first person, as if you are {self.agent_name}."
        )
        
        self.task = None
        self.skip_persona_syntax_failures = skip_persona_syntax_failures
        self.temperature = temperature_persona
        
        # Load preferences (from database or files)
        self._load_preferences()
    
    def _load_preferences(self):
        """Load preferences from database or fallback to files"""
        if self.use_database and self.preference_manager:
            try:
                # Get preferences from database
                self.preferences_list = self.preference_manager.get_preference_list(self.agent_name)
                self.privileged_preferences = self.preference_manager.get_privileged_summary(self.agent_name)
            except Exception as e:
                print(f"Warning: Could not load preferences from database: {e}")
                # Fallback to file-based preferences
                self.preferences_list = get_preference_list(persona_id=self.agent_name)
                self.privileged_preferences = '\n'.join(self.preferences_list)
        else:
            # Use file-based preferences
            self.preferences_list = get_preference_list(persona_id=self.agent_name)
            self.privileged_preferences = '\n'.join(self.preferences_list)
    
    def reset(self):
        """Reset the persona"""
        self.task = None
        self.preferences_list = None
        print("Resetting Persona...")
    
    def get_privileged_summary(self):
        """Get privileged summary of user preferences"""
        if self.use_database and self.preference_manager:
            try:
                return self.preference_manager.get_privileged_summary(self.agent_name)
            except Exception as e:
                print(f"Warning: Could not get database summary: {e}")
                # Fallback to file-based summary
                return (
                    f"You know the following about {self.agent_name}'s preferences.\n"
                    + self.privileged_preferences
                )
        else:
            # Use file-based summary
            return (
                f"You know the following about {self.agent_name}'s preferences.\n"
                + self.privileged_preferences
            )
    
    def answer_question(self, env, rollout_steps, task):
        """Answer a question from the robot"""
        inst2 = f"Look at the following interaction and provide a short answer to the robot's last question based on {self.agent_name}'s preferences. If {self.agent_name} is flexible in their preference, make a choice arbirarily, but make sure to tell the robot that usually {self.agent_name} is flexible, and options which they would be okay with. Make sure to be consistent with your previous feedback."
        
        # Get the last question from rollout steps
        last_question = None
        for step in reversed(rollout_steps):
            if step.get('action_enum') == 'ask':
                last_question = step.get('action', '')
                break
        
        if not last_question:
            return "I don't see any question to answer."
        
        # Create prompt for the persona
        prompt = f"{inst2}\n\nTask: {task}\n\nRobot's question: {last_question}\n\n{self.privileged_preferences}"
        
        # Get response from LLM
        response = self.run_llm(prompt, temperature=self.temperature)
        
        # Log interaction if using database
        if self.use_database and self.preference_manager:
            try:
                self.preference_manager.add_preference_from_interaction(
                    persona_id=self.agent_name,
                    task=task,
                    robot_action=last_question,
                    user_response=response,
                    context={"rollout_steps": len(rollout_steps)}
                )
            except Exception as e:
                print(f"Warning: Could not log interaction to database: {e}")
        
        return response
    
    def log_task_completion(self, task, success, completion_time=None, steps_taken=0, final_reward=None):
        """Log task completion to database"""
        if self.use_database and self.preference_manager:
            try:
                self.preference_manager.log_task_completion(
                    persona_id=self.agent_name,
                    task=task,
                    success=success,
                    completion_time=completion_time,
                    steps_taken=steps_taken,
                    final_reward=final_reward
                )
            except Exception as e:
                print(f"Warning: Could not log task completion to database: {e}")
    
    def get_user_stats(self):
        """Get user statistics from database"""
        if self.use_database and self.preference_manager:
            try:
                return self.preference_manager.get_user_stats(self.agent_name)
            except Exception as e:
                print(f"Warning: Could not get user stats from database: {e}")
                return {"error": "Database not available"}
        else:
            return {"error": "Database not enabled"}
    
    def add_preference(self, preference_type, preference_key, preference_value, confidence_score=1.0):
        """Manually add a preference"""
        if self.use_database and self.preference_manager:
            try:
                user = self.preference_manager.preference_service.get_or_create_user(self.agent_name)
                self.preference_manager.preference_service.add_preference(
                    user_id=user.id,
                    preference_type=preference_type,
                    preference_key=preference_key,
                    preference_value=preference_value,
                    confidence_score=confidence_score
                )
                # Reload preferences
                self._load_preferences()
                return True
            except Exception as e:
                print(f"Error adding preference: {e}")
                return False
        else:
            print("Database not available for adding preferences")
            return False
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'preference_manager') and self.preference_manager:
            try:
                close_preference_manager()
            except:
                pass
