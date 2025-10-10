"""
Setup script for Adapt-Memory database
"""
import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install database requirements"""
    print("Installing database requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_db.txt"])
        print("✓ Database requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not env_example.exists():
        print("✗ env_example.txt not found")
        return False
    
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created from template")
        print("⚠️  Please edit .env file with your database configuration")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        from database.test_database import main as test_main
        test_main()
        return True
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False

def run_migration():
    """Run database migration"""
    print("Running database migration...")
    try:
        from database.migrate_existing_preferences import main as migrate_main
        migrate_main()
        print("✓ Database migration completed")
        return True
    except Exception as e:
        print(f"✗ Database migration failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Adapt-Memory Database Setup")
    print("=" * 40)
    
    steps = [
        ("Installing requirements", install_requirements),
        ("Creating .env file", create_env_file),
        ("Testing database connection", test_database_connection),
        ("Running migration", run_migration)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"✗ {step_name} failed")
            print("\nPlease check your database configuration and try again.")
            return False
    
    print("\n" + "=" * 40)
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your database configuration")
    print("2. Ensure PostgreSQL is running (or use Neon cloud database)")
    print("3. Run: python database/test_database.py")
    print("4. Start using the database-enabled system!")

if __name__ == "__main__":
    main()
