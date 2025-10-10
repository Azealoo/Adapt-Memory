"""
SQLAlchemy models for Adapt-Memory database
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    """User preference model for storing individual preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_type = Column(String(100), nullable=False)  # e.g., "dietary", "cooking_style", "communication"
    preference_key = Column(String(200), nullable=False)  # e.g., "breakfast_preference", "coffee_style"
    preference_value = Column(Text, nullable=False)  # The actual preference text
    confidence_score = Column(Float, default=1.0)  # Confidence in this preference (0.0 to 1.0)
    source = Column(String(100), default="user_feedback")  # How this preference was learned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    interactions = relationship("UserInteraction", back_populates="preference")

class UserInteraction(Base):
    """User interaction model for storing conversation history"""
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_id = Column(Integer, ForeignKey("user_preferences.id"), nullable=True)
    task = Column(String(500), nullable=False)  # The task being performed
    interaction_type = Column(String(50), nullable=False)  # "question", "feedback", "correction"
    robot_action = Column(Text, nullable=True)  # What the robot did
    user_response = Column(Text, nullable=True)  # User's response
    context = Column(JSON, nullable=True)  # Additional context as JSON
    reward_score = Column(Float, nullable=True)  # Reward/feedback score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    preference = relationship("UserPreference", back_populates="interactions")

class PreferenceTemplate(Base):
    """Template for common preference types"""
    __tablename__ = "preference_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(200), unique=True, nullable=False)
    preference_type = Column(String(100), nullable=False)
    template_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TaskHistory(Base):
    """Task execution history"""
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String(500), nullable=False)
    task_description = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    completion_time = Column(Float, nullable=True)  # Time in seconds
    steps_taken = Column(Integer, default=0)
    preferences_used = Column(JSON, nullable=True)  # List of preference IDs used
    final_reward = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
