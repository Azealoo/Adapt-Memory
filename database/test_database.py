"""
Test script for database functionality
"""
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from database.preference_manager import get_preference_manager, close_preference_manager
from database.config import engine, Base
from sqlalchemy import text

def test_database_connection():
    """Test database connection"""
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_create_tables():
    """Test table creation"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False

def test_preference_operations():
    """Test preference operations"""
    try:
        manager = get_preference_manager()
        
        # Test user creation
        user = manager.preference_service.get_or_create_user("test_persona", "Test User")
        print(f"✓ User created: {user.persona_id}")
        
        # Test preference addition
        preference = manager.preference_service.add_preference(
            user_id=user.id,
            preference_type="breakfast",
            preference_key="coffee_preference",
            preference_value="I prefer strong black coffee",
            confidence_score=1.0
        )
        print(f"✓ Preference added: {preference.preference_value}")
        
        # Test preference retrieval
        preferences = manager.preference_service.get_user_preferences(user.id)
        print(f"✓ Retrieved {len(preferences)} preferences")
        
        # Test interaction logging
        interaction = manager.preference_service.log_interaction(
            user_id=user.id,
            task="Make coffee",
            interaction_type="question",
            robot_action="Ask about coffee preference",
            user_response="I like it strong and black"
        )
        print(f"✓ Interaction logged: {interaction.id}")
        
        # Test task completion logging
        task_history = manager.preference_service.log_task_completion(
            user_id=user.id,
            task_name="Make coffee",
            success=True,
            completion_time=120.5,
            steps_taken=5,
            final_reward=45.0
        )
        print(f"✓ Task completion logged: {task_history.id}")
        
        # Test preference list (compatible with existing system)
        preference_list = manager.get_preference_list("test_persona")
        print(f"✓ Preference list: {len(preference_list)} items")
        
        # Test privileged summary
        summary = manager.get_privileged_summary("test_persona")
        print(f"✓ Privileged summary generated: {len(summary)} characters")
        
        # Test user stats
        stats = manager.get_user_stats("test_persona")
        print(f"✓ User stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Preference operations failed: {e}")
        return False
    finally:
        close_preference_manager()

def main():
    """Run all tests"""
    print("Testing Adapt-Memory Database Setup")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Creation", test_create_tables),
        ("Preference Operations", test_preference_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n{'=' * 40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Database setup is working correctly.")
    else:
        print("❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
