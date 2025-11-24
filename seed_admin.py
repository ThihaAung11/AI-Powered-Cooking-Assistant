"""
Database seed script for admin panel functionality.
Run this script to create necessary roles and an initial admin user.

Usage:
    python seed_admin.py
"""

from app.database import get_db, SessionLocal
from app.models import Role, User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session


def seed_roles(db: Session):
    """Create default roles if they don't exist."""
    roles = [
        {"name": "user", "description": "Regular user with standard permissions"},
        {"name": "admin", "description": "Administrator with full system access"},
        {"name": "moderator", "description": "Moderator with content management permissions"}
    ]
    
    for role_data in roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ Created role: {role_data['name']}")
        else:
            print(f"- Role already exists: {role_data['name']}")
    
    db.commit()
    print("\n✓ Roles seeded successfully")


def create_admin_user(db: Session, username: str, email: str, password: str, name: str = "Admin"):
    """Create an admin user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        print(f"\n✗ User already exists with username '{username}' or email '{email}'")
        return False
    
    # Get admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        print("\n✗ Admin role not found. Please run seed_roles first.")
        return False
    
    # Create admin user
    hashed_password = get_password_hash(password)
    admin_user = User(
        username=username,
        name=name,
        email=email,
        password=hashed_password,
        role_id=admin_role.id,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"\n✓ Admin user created successfully!")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Role: admin")
    return True


def main():
    """Main function to seed database."""
    print("=" * 60)
    print("Admin Panel Database Seed Script")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Seed roles
        print("Seeding roles...")
        seed_roles(db)
        
        # Create admin user
        print("\n" + "=" * 60)
        print("Create Admin User")
        print("=" * 60)
        
        import getpass
        
        username = input("\nEnter admin username (default: admin): ").strip() or "admin"
        email = input("Enter admin email (default: admin@example.com): ").strip() or "admin@example.com"
        name = input("Enter admin name (default: Admin): ").strip() or "Admin"
        
        # Get password securely
        while True:
            password = getpass.getpass("Enter admin password: ")
            confirm_password = getpass.getpass("Confirm admin password: ")
            
            if password != confirm_password:
                print("\n✗ Passwords don't match. Please try again.\n")
                continue
            
            if len(password) < 8:
                print("\n✗ Password must be at least 8 characters long. Please try again.\n")
                continue
            
            break
        
        create_admin_user(db, username, email, password, name)
        
        print("\n" + "=" * 60)
        print("Database seeded successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Login as admin at: http://localhost:8000/docs")
        print("3. Access admin endpoints under: /admin/*")
        print("\nAdmin endpoints:")
        print("  - GET  /admin/users - View all users")
        print("  - GET  /admin/recipes - View all recipes")
        print("  - GET  /admin/feedbacks - View all feedbacks")
        print("  - GET  /admin/cooking-sessions - View cooking history")
        print("  - GET  /admin/analytics/cooking - View analytics")
        print("  - POST /admin/ai/refresh-embeddings - Refresh AI knowledge")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
