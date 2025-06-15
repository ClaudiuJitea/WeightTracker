#!/usr/bin/env python3
"""
Script to create a default administrator account for the Weight Tracker application.
This should be run once after setting up the database.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def create_default_admin():
    """Create a default administrator account."""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Default admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Email: {existing_admin.email}")
            print(f"Is Admin: {existing_admin.is_admin}")
            return
        
        # Create default admin user
        admin_user = User(
            username='admin',
            email='admin@weighttracker.local',
            is_admin=True,
            created_at=datetime.utcnow()
        )
        
        # Set default password (should be changed on first login)
        import secrets
        import string
        
        # Generate a random password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        default_password = ''.join(secrets.choice(alphabet) for i in range(12))
        admin_user.set_password(default_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Default administrator account created successfully!")
            print("\n" + "="*50)
            print("DEFAULT ADMIN CREDENTIALS")
            print("="*50)
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.email}")
            print(f"Password: {default_password}")
            print("="*50)
            print("\n⚠️  IMPORTANT SECURITY NOTICE:")
            print("   Please change the default password immediately after first login!")
            print("   You can change it from the admin dashboard or user profile.")
            print("\n🔗 Access the admin dashboard at: /admin/dashboard")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {str(e)}")
            return False
    
    return True

def check_admin_users():
    """Check existing admin users."""
    app = create_app()
    
    with app.app_context():
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("No admin users found in the database.")
            return []
        
        print(f"Found {len(admin_users)} admin user(s):")
        for admin in admin_users:
            print(f"  - {admin.username} ({admin.email})")
        
        return admin_users

if __name__ == '__main__':
    print("Weight Tracker - Admin User Setup")
    print("=" * 40)
    
    # Check for existing admin users first
    print("\nChecking for existing admin users...")
    existing_admins = check_admin_users()
    
    if existing_admins:
        response = input("\nAdmin users already exist. Create another admin? (y/N): ")
        if response.lower() != 'y':
            print("Exiting without creating new admin user.")
            sys.exit(0)
    
    print("\nCreating default admin user...")
    success = create_default_admin()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("You can now start the application and log in with the admin credentials.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)