#!/usr/bin/env python3
"""
Test script cho Food Recommendation API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   System ready: {data['system_ready']}")
            return data['system_ready']
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_daily_meal():
    """Test daily meal creation"""
    print("\n🍽️ Testing daily meal creation...")
    
    payload = {
        "favorite_ingredients": [1, 2],  # IDs của nguyên liệu yêu thích
        "not_favorite_ingredients": [3],  # IDs của nguyên liệu không thích
        "allergy_ingredients": [4],  # IDs của nguyên liệu dị ứng
        "favorite_recipes": [1],  # IDs của món ăn yêu thích
        "not_favorite_recipes": [2],  # IDs của món ăn không thích
        "diet_mode": "normal",
        "serving_size": 2,
        "date": "2024-01-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/daily-meal", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                meals_data = data['data']
                print("✅ Daily meal created successfully!")
                print(f"   Date: {meals_data['date']}")
                print(f"   Number of meals: {len(meals_data['meals'])}")
                
                for meal in meals_data['meals']:
                    meal_type = meal['mealTypeId']
                    map_recipe = meal['mapRecipe']
                    print(f"   {meal_type}:")
                    for recipe_type, recipe_ids in map_recipe.items():
                        if recipe_ids:
                            print(f"     {recipe_type}: {len(recipe_ids)} món")
                
                return meals_data
            else:
                print(f"❌ Daily meal creation failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Daily meal API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Daily meal test error: {str(e)}")
        return None

def test_weekly_meal():
    """Test weekly meal creation"""
    print("\n📅 Testing weekly meal creation...")
    
    payload = {
        "favorite_ingredients": [5, 6],  # IDs của nguyên liệu yêu thích
        "not_favorite_ingredients": [3],  # IDs của nguyên liệu không thích
        "allergy_ingredients": [4],  # IDs của nguyên liệu dị ứng
        "diet_mode": "vegetarian",
        "serving_size": 3,
        "start_date": "2024-01-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/weekly-meal", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                weekly_meals = data['data']
                print("✅ Weekly meal created successfully!")
                print(f"   Number of days: {len(weekly_meals)}")
                
                # Hiển thị thông tin ngày đầu tiên
                if weekly_meals:
                    first_day = weekly_meals[0]
                    print(f"   First day date: {first_day['date']}")
                    print(f"   First day meals: {len(first_day['meals'])}")
                
                return weekly_meals
            else:
                print(f"❌ Weekly meal creation failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Weekly meal API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Weekly meal test error: {str(e)}")
        return None

def test_replace_recipe(daily_meals):
    """Test recipe replacement"""
    if not daily_meals:
        print("❌ Cannot test recipe replacement without daily meals")
        return
    
    print("\n🔄 Testing recipe replacement...")
    
    # Tìm recipe ID đầu tiên từ bữa trưa
    recipe_id = None
    for meal in daily_meals['meals']:
        if str(meal['mealTypeId']) == 'bữa trưa':
            for recipe_type, recipe_ids in meal['mapRecipe'].items():
                if recipe_ids:
                    recipe_id = recipe_ids[0]
                    print(f"   Replacing recipe ID: {recipe_id} from {recipe_type}")
                    break
            if recipe_id:
                break
    
    if not recipe_id:
        print("❌ No recipes to replace")
        return
    
    payload = {
        "daily_plan": daily_meals,
        "meal_type": "bữa trưa",
        "recipe_id": recipe_id,
        "replacement_reason": "ingredients",
        "favorite_ingredients": [1, 2],  # IDs của nguyên liệu yêu thích
        "not_favorite_ingredients": [3],  # IDs của nguyên liệu không thích
        "allergy_ingredients": [4],  # IDs của nguyên liệu dị ứng
        "diet_mode": "normal",
        "serving_size": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/replace-recipe", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                updated_meals = data['data']
                print("✅ Recipe replacement successful!")
                print(f"   Updated date: {updated_meals['date']}")
                print(f"   Updated meals: {len(updated_meals['meals'])}")
                return updated_meals
            else:
                print(f"❌ Recipe replacement failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Recipe replacement API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Recipe replacement test error: {str(e)}")
        return None

def test_get_recipes():
    """Test getting recipes list"""
    print("\n📋 Testing get recipes...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/recipes")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                recipes = data['recipes']
                print(f"✅ Got {len(recipes)} recipes")
                if recipes:
                    first_recipe = recipes[0]
                    print(f"   First recipe: {first_recipe['name']}")
                    print(f"   Type: {first_recipe['recipe_type']}")
                    print(f"   Method: {first_recipe['method']}")
                return True
            else:
                print(f"❌ Get recipes failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get recipes API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get recipes test error: {str(e)}")
        return False

def test_get_ingredients():
    """Test getting ingredients list"""
    print("\n🥕 Testing get ingredients...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ingredients")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                ingredients = data['ingredients']
                print(f"✅ Got {len(ingredients)} ingredients")
                if ingredients:
                    first_ingredient = ingredients[0]
                    print(f"   First ingredient: {first_ingredient['name']}")
                return True
            else:
                print(f"❌ Get ingredients failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get ingredients API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get ingredients test error: {str(e)}")
        return False

def test_get_tags():
    """Test getting tags list"""
    print("\n🏷️ Testing get tags...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tags")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                tags = data['tags']
                print(f"✅ Got {len(tags)} tags")
                if tags:
                    first_tag = tags[0]
                    print(f"   First tag: {first_tag['name']} (Group: {first_tag['group']})")
                return True
            else:
                print(f"❌ Get tags failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Get tags API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get tags test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Food Recommendation API tests...")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ System not ready, skipping other tests")
        return
    
    # Wait a bit for system to be fully ready
    print("⏳ Waiting for system to be fully ready...")
    time.sleep(2)
    
    # Test daily meal creation
    daily_meals = test_daily_meal()
    
    # Test weekly meal creation
    weekly_meals = test_weekly_meal()
    
    # Test recipe replacement
    if daily_meals:
        updated_meals = test_replace_recipe(daily_meals)
    
    # Test get recipes
    test_get_recipes()
    
    # Test get ingredients
    test_get_ingredients()
    
    # Test get tags
    test_get_tags()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    
    if daily_meals:
        print("✅ Daily meal creation: PASSED")
    else:
        print("❌ Daily meal creation: FAILED")
    
    if weekly_meals:
        print("✅ Weekly meal creation: PASSED")
    else:
        print("❌ Weekly meal creation: FAILED")
    
    if daily_meals and 'updated_meals' in locals():
        print("✅ Recipe replacement: PASSED")
    else:
        print("❌ Recipe replacement: FAILED")

if __name__ == "__main__":
    main()
