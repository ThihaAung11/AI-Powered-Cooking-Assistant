# Recipe Display with Saved Status Guide

This guide shows how to display recipe data with saved/unsaved status in your frontend application.

## Backend API Changes ✅

The following endpoints now include `is_saved` and `save_count` fields:

- `GET /recipes/` - List all recipes with saved status
- `GET /recipes/search` - Search recipes with saved status  
- `GET /recipes/{id}` - Get single recipe with saved status
- `GET /recipes/recommend` - AI recommendations with saved status

## API Response Format

```json
{
  "items": [
    {
      "id": 1,
      "title": "Spicy Thai Curry",
      "description": "A delicious and spicy curry",
      "cuisine": "Thai",
      "difficulty": "Medium", 
      "total_time": 45,
      "ingredients": "coconut milk, curry paste, vegetables",
      "image_url": "https://example.com/curry.jpg",
      "is_public": true,
      "is_saved": true,        // null if user not authenticated
      "save_count": 23,        // total number of saves
      "created_at": "2024-11-25T04:08:00Z",
      "creator": {
        "id": 5,
        "username": "chef_tom",
        "name": "Tom Chef"
      }
    }
  ]
}
```

## Field Meanings

- **`is_saved`**: 
  - `true` - Recipe is saved by current user
  - `false` - Recipe is not saved by current user  
  - `null` - User not authenticated/not provided
- **`save_count`**: Total number of users who saved this recipe

## Frontend Display Examples

### 1. Recipe Card with Save Status

```tsx
const RecipeCard = ({ recipe, onSaveToggle, currentUser }) => {
  return (
    <div className="recipe-card">
      <img src={recipe.image_url} alt={recipe.title} />
      
      {/* Save Button */}
      {currentUser && (
        <button 
          onClick={() => onSaveToggle(recipe.id, recipe.is_saved)}
          className={recipe.is_saved ? 'saved' : 'not-saved'}
        >
          <HeartIcon filled={recipe.is_saved} />
        </button>
      )}
      
      <h3>{recipe.title}</h3>
      <p>{recipe.description}</p>
      
      {/* Save Count */}
      <div className="stats">
        <span>{recipe.save_count} saves</span>
        <span>{recipe.total_time}m</span>
        <span>{recipe.difficulty}</span>
      </div>
      
      {/* Current User Save Status */}
      {currentUser && recipe.is_saved !== null && (
        <div className="save-status">
          {recipe.is_saved ? 'Saved ❤️' : 'Not saved'}
        </div>
      )}
    </div>
  );
};
```

### 2. Save/Unsave Functionality

```javascript
const handleSaveToggle = async (recipeId, currentlySaved) => {
  try {
    if (currentlySaved) {
      // Unsave recipe
      await fetch(`/api/saved-recipes/recipe/${recipeId}`, {
        method: 'DELETE',
        headers: { 'Authorization': 'Bearer your-token' }
      });
    } else {
      // Save recipe  
      await fetch('/api/saved-recipes/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Bearer your-token' 
        },
        body: JSON.stringify({ recipe_id: recipeId })
      });
    }

    // Update local state
    setRecipes(prev => prev.map(recipe => 
      recipe.id === recipeId 
        ? { 
            ...recipe, 
            is_saved: !currentlySaved,
            save_count: recipe.save_count + (currentlySaved ? -1 : 1)
          }
        : recipe
    ));
  } catch (error) {
    console.error('Failed to toggle save status:', error);
  }
};
```

### 3. Recipe List with Filtering

```javascript
// Show all recipes
const allRecipes = await fetch('/api/recipes/').then(r => r.json());

// Show only saved recipes by current user
const savedRecipes = await fetch('/api/saved-recipes/my-saved-recipes')
  .then(r => r.json());

// Search with saved status
const searchResults = await fetch('/api/recipes/search?search=curry')
  .then(r => r.json());
```

## Display States

### For Authenticated Users
- Show heart icon (filled if saved, outline if not)
- Display save count
- Show personal save status
- Enable save/unsave functionality

### For Non-Authenticated Users  
- Show save count only
- Hide save button
- `is_saved` will be `null`
- Show login prompt when trying to save

### Popular Recipe Indicators
Use `save_count` to show popularity:
- 0-5 saves: New recipe
- 6-20 saves: Popular
- 21+ saves: Very popular

## CSS Classes Example

```css
.recipe-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.save-button {
  position: absolute;
  top: 12px;
  right: 12px;
  background: white;
  border-radius: 50%;
  padding: 8px;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.save-button.saved {
  background: #ef4444;
  color: white;
}

.save-button:hover {
  transform: scale(1.05);
}

.save-count {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6b7280;
  font-size: 14px;
}

.save-status.saved {
  color: #ef4444;
  font-weight: 500;
}
```

## Implementation Checklist

- [ ] Update API calls to use new enriched endpoints
- [ ] Add save/unsave button functionality  
- [ ] Display save count in recipe cards
- [ ] Show personal save status for authenticated users
- [ ] Handle unauthenticated state gracefully
- [ ] Add loading states for save/unsave actions
- [ ] Update local state after save/unsave operations
- [ ] Add error handling for failed save operations

## Notes

- The backend efficiently batches save status checks to minimize database queries
- Save counts are real-time and cached for performance  
- All existing saved recipe endpoints remain unchanged
- The enhancement is backward compatible with existing frontend code
