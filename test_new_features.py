"""
Quick test script for new features
Run: uv run python test_new_features.py
"""
import requests

BASE_URL = "http://localhost:8000"

# Test credentials (create a test user first)
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
}

def get_auth_token():
    """Login and get token"""
    # Try to login first
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, register
    print("Registering new user...")
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if response.status_code == 201:
        # Now login
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": TEST_USER["username"], "password": TEST_USER["password"]}
        )
        return response.json()["access_token"]
    
    raise Exception("Failed to authenticate")


def test_collections(token):
    """Test recipe collections"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 Testing Recipe Collections...")
    
    # 1. Create collection
    collection_data = {
        "name": "Weekly Meal Plan",
        "description": "Test meal plan",
        "collection_type": "meal_plan",
        "is_public": False
    }
    
    response = requests.post(f"{BASE_URL}/collections/", json=collection_data, headers=headers)
    print(f"✅ Create collection: {response.status_code}")
    if response.status_code == 201:
        collection = response.json()
        collection_id = collection["id"]
        print(f"   Collection ID: {collection_id}")
        
        # 2. Get collections
        response = requests.get(f"{BASE_URL}/collections/", headers=headers)
        print(f"✅ Get collections: {response.status_code} - Found {len(response.json())} collection(s)")
        
        # 3. Get single collection
        response = requests.get(f"{BASE_URL}/collections/{collection_id}", headers=headers)
        print(f"✅ Get collection detail: {response.status_code}")
        
        return collection_id
    
    return None


def test_shopping_lists(token, recipe_ids=None):
    """Test shopping lists"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🛒 Testing Shopping Lists...")
    
    # 1. Create manual shopping list
    list_data = {
        "name": "Test Shopping List",
        "description": "Manual test",
        "is_completed": False,
        "items": [
            {
                "ingredient": "milk",
                "quantity": "1 gallon",
                "category": "Dairy"
            },
            {
                "ingredient": "tomatoes",
                "quantity": "4",
                "category": "Produce"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/shopping-lists/", json=list_data, headers=headers)
    print(f"✅ Create manual shopping list: {response.status_code}")
    
    if response.status_code == 201:
        shopping_list = response.json()
        list_id = shopping_list["id"]
        print(f"   Shopping List ID: {list_id}")
        print(f"   Items: {len(shopping_list['items'])}")
        
        # 2. Get shopping lists
        response = requests.get(f"{BASE_URL}/shopping-lists/", headers=headers)
        print(f"✅ Get shopping lists: {response.status_code} - Found {len(response.json())} list(s)")
        
        # 3. Toggle item
        if shopping_list["items"]:
            item_id = shopping_list["items"][0]["id"]
            response = requests.patch(
                f"{BASE_URL}/shopping-lists/items/{item_id}?is_checked=true",
                headers=headers
            )
            print(f"✅ Toggle item checked: {response.status_code}")
        
        return list_id
    
    return None


def test_integration(token):
    """Test integration features"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔗 Testing Integration Features...")
    
    # Get recipes
    response = requests.get(f"{BASE_URL}/recipes/", headers=headers)
    if response.status_code == 200:
        recipes = response.json().get("items", [])
        if recipes:
            recipe_id = recipes[0]["id"]
            print(f"✅ Found recipe: {recipe_id}")
            
            # Create collection and add recipe
            collection_data = {
                "name": "Integration Test Collection",
                "collection_type": "custom"
            }
            response = requests.post(f"{BASE_URL}/collections/", json=collection_data, headers=headers)
            
            if response.status_code == 201:
                collection_id = response.json()["id"]
                
                # Add recipe to collection
                item_data = {
                    "recipe_id": recipe_id,
                    "order": 1,
                    "day_of_week": "Monday",
                    "meal_type": "dinner"
                }
                response = requests.post(
                    f"{BASE_URL}/collections/{collection_id}/recipes",
                    json=item_data,
                    headers=headers
                )
                print(f"✅ Add recipe to collection: {response.status_code}")
                
                # Generate shopping list from collection
                generate_data = {
                    "collection_id": collection_id,
                    "list_name": "Generated from Collection"
                }
                response = requests.post(
                    f"{BASE_URL}/shopping-lists/generate",
                    json=generate_data,
                    headers=headers
                )
                print(f"✅ Generate shopping list from collection: {response.status_code}")
                
                if response.status_code == 201:
                    shopping_list = response.json()
                    print(f"   Generated {len(shopping_list['items'])} items")
                    for item in shopping_list['items'][:3]:  # Show first 3
                        print(f"   - {item['ingredient']} ({item['category']})")
        else:
            print("⚠️ No recipes found. Create some recipes first!")
    else:
        print(f"⚠️ Failed to get recipes: {response.status_code}")


def main():
    print("=" * 50)
    print("Testing New Features: Collections & Shopping Lists")
    print("=" * 50)
    
    try:
        # Get authentication token
        print("\n🔐 Authenticating...")
        token = get_auth_token()
        print("✅ Authentication successful")
        
        # Test collections
        collection_id = test_collections(token)
        
        # Test shopping lists
        list_id = test_shopping_lists(token)
        
        # Test integration
        test_integration(token)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)
        print("\n📚 Next Steps:")
        print("1. Open http://localhost:8000/docs to see API docs")
        print("2. Check NEW_FEATURES_GUIDE.md for detailed usage")
        print("3. Test manually in Swagger UI")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Server is running: uv run uvicorn app.main:app --reload")
        print("2. Database is accessible")


if __name__ == "__main__":
    main()
