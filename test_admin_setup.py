"""
Test script to verify admin panel setup is correct.
Run this before starting the server to catch any issues.
"""

import sys

def test_imports():
    """Test all admin-related imports."""
    print("Testing imports...")
    try:
        from app.core.security import get_admin_user
        from app.schemas.admin import (
            AdminUserOut, AdminUserList, UserDeactivate,
            AdminRecipeCreate, AdminRecipeUpdate, AdminRecipeOut,
            AdminFeedbackOut, AdminFeedbackList, FeedbackRemoveReason,
            CookingHistoryItem, CookingHistoryList, CookingAnalytics,
            AIKnowledgeRefreshResponse, RecipeDataUpdate
        )
        from app.routers.admin import router
        from app.deps import AdminUser
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def test_router_setup():
    """Test that admin router is properly configured."""
    print("\nTesting router setup...")
    try:
        from app.routers.admin import router
        
        # Check router has routes
        if not router.routes:
            print("✗ Router has no routes")
            return False
        
        print(f"✓ Router has {len(router.routes)} routes")
        
        # List all routes
        print("\nAdmin endpoints:")
        for route in router.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  {methods:8} {route.path}")
        
        return True
    except Exception as e:
        print(f"✗ Router setup error: {e}")
        return False


def test_database_models():
    """Test that all required database models exist."""
    print("\nTesting database models...")
    try:
        from app.models import User, Recipe, UserFeedback, UserCookingSession, Role
        from app.models.recipe import CookingStep
        
        required_models = [User, Recipe, UserFeedback, UserCookingSession, Role, CookingStep]
        model_names = [m.__name__ for m in required_models]
        
        print(f"✓ All required models exist: {', '.join(model_names)}")
        return True
    except Exception as e:
        print(f"✗ Model error: {e}")
        return False


def test_main_app():
    """Test that admin router is registered in main app."""
    print("\nTesting main app registration...")
    try:
        from app.main import app
        
        # Check if admin router is registered
        admin_routes = [r for r in app.routes if '/admin' in str(r.path)]
        
        if not admin_routes:
            print("✗ Admin router not registered in main app")
            return False
        
        print(f"✓ Admin router registered with {len(admin_routes)} endpoints")
        return True
    except Exception as e:
        print(f"✗ Main app error: {e}")
        return False


def test_security_functions():
    """Test security functions exist and are callable."""
    print("\nTesting security functions...")
    try:
        from app.core.security import (
            get_password_hash,
            verify_password,
            create_access_token,
            get_current_user,
            get_admin_user
        )
        
        # Test password hashing
        test_password = "test_password_123"
        hashed = get_password_hash(test_password)
        
        if not verify_password(test_password, hashed):
            print("✗ Password verification failed")
            return False
        
        print("✓ All security functions working")
        return True
    except Exception as e:
        print(f"✗ Security function error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Admin Panel Setup Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_router_setup,
        test_database_models,
        test_main_app,
        test_security_functions
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All tests passed! Admin panel is ready to use.")
        print("\nNext steps:")
        print("1. Run: python seed_admin.py")
        print("2. Start server: uvicorn app.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
