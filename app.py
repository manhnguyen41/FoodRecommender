from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
import os
from datetime import datetime, timedelta

# Import các module cần thiết
from daily_meal_planner import (
    suggest_daily_meals, 
    get_default_user_profile, 
    get_default_user_requirements,
    replace_recipe_in_daily_plan
)
from weekly_meal_planner import generate_weekly_meal_plan
from embeddings import load_phobert_model
from utils import load_data
from similarity import (
    create_recipe_similarity_matrix,
    create_ingredient_similarity_matrix,
    create_tag_similarity_matrix
)

app = Flask(__name__)
CORS(app)

# Global variables để lưu trữ model và data
model = None
tokenizer = None
recipes = []
ingredients = []
tags = []
recipe_sim_matrix = None
ingredient_sim_matrix = None
tag_sim_matrix = None
ingredient_name_to_id = None
tag_name_to_id = None
all_ingredient_names = None
all_tag_names = None
all_ingredient_ids = None
all_tag_ids = None

def initialize_system():
    """Khởi tạo hệ thống - load model và data"""
    global model, tokenizer, recipes, ingredients, tags
    global recipe_sim_matrix, ingredient_sim_matrix, tag_sim_matrix
    global ingredient_name_to_id, tag_name_to_id
    global all_ingredient_names, all_tag_names, all_ingredient_ids, all_tag_ids
    
    try:
        print("🚀 Đang khởi tạo hệ thống...")
        
        # Load PhoBERT model
        print("📚 Đang load PhoBERT model...")
        model, tokenizer = load_phobert_model()
        print("✅ Đã load xong PhoBERT model!")
        
        # Load data
        print("📊 Đang load data...")
        df, recipes = load_data("data/recipes.json")
        _, ingredients = load_data("data/ingredients.json") 
        _, tags = load_data("data/tags.json")
        print(f"✅ Đã load {len(recipes)} món ăn, {len(ingredients)} nguyên liệu, {len(tags)} tags")
        
        # Tạo similarity matrices
        print("🔍 Đang tạo similarity matrices...")
        recipe_sim_matrix, rec_name_to_rec_id = create_recipe_similarity_matrix(df, recipes, model, tokenizer)
        ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids = create_ingredient_similarity_matrix(ingredients, model, tokenizer)
        tag_sim_matrix, tag_name_to_id, all_tag_names, all_tag_ids = create_tag_similarity_matrix(tags, model, tokenizer)
        print("✅ Đã tạo xong similarity matrices!")
        
        print("🎉 Hệ thống đã sẵn sàng!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo hệ thống: {str(e)}")
        return False


def convert_daily_plan_to_meals_format(daily_plan, date_timestamp):
    """Chuyển đổi daily_plan sang format meals mong muốn"""
    # Nếu daily_plan đã có cấu trúc mới (với "meals"), chỉ cần thêm date
    if "meals" in daily_plan:
        return {
            "date": date_timestamp,
            "meals": daily_plan["meals"]
        }
    
    # Xử lý cấu trúc cũ (fallback)
    meals = []
    
    # Xử lý bữa sáng
    breakfast_meals = {
        "mealTypeId": "bữa sáng",
        "mapRecipe": {
            "món chính": [],
            "món phụ": [],
            "món canh": [],
            "món tráng miệng": []
        }
    }
    breakpoint()
    if daily_plan.get("breakfast") and daily_plan["breakfast"].get("recipes"):
        for recipe in daily_plan["breakfast"]["recipes"]:
            recipe_types = recipe.get("recipe_type", [])
            for recipe_type in recipe_types:
                if recipe_type in breakfast_meals["mapRecipe"]:
                    breakfast_meals["mapRecipe"][recipe_type].append(recipe.get("id"))
    
    meals.append(breakfast_meals)
    
    # Xử lý bữa trưa
    lunch_meals = {
        "mealTypeId": "bữa trưa",
        "mapRecipe": {
            "món chính": [],
            "món phụ": [],
            "món canh": [],
            "món tráng miệng": []
        }
    }
    
    if daily_plan.get("lunch") and daily_plan["lunch"].get("recipes"):
        for recipe in daily_plan["lunch"]["recipes"]:
            recipe_types = recipe.get("recipe_type", [])
            for recipe_type in recipe_types:
                if recipe_type in lunch_meals["mapRecipe"]:
                    lunch_meals["mapRecipe"][recipe_type].append(recipe.get("id"))
    
    meals.append(lunch_meals)
    
    # Xử lý bữa tối
    dinner_meals = {
        "mealTypeId": "bữa tối",
        "mapRecipe": {
            "món chính": [],
            "món phụ": [],
            "món canh": [],
            "món tráng miệng": []
        }
    }
    
    if daily_plan.get("dinner") and daily_plan["dinner"].get("recipes"):
        for recipe in daily_plan["dinner"]["recipes"]:
            recipe_types = recipe.get("recipe_type", [])
            for recipe_type in recipe_types:
                if recipe_type in dinner_meals["mapRecipe"]:
                    dinner_meals["mapRecipe"][recipe_type].append(recipe.get("id"))
    
    meals.append(dinner_meals)
    
    return {
        "date": date_timestamp,
        "meals": meals
    }

def convert_weekly_plan_to_meals_format(weekly_plan, start_date):
    """Chuyển đổi weekly_plan sang format meals cho từng ngày"""
    weekly_meals = []
    
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    for i, day in enumerate(weekdays):
        if day in weekly_plan:
            daily_plan = weekly_plan[day]
            # Tính timestamp cho ngày tương ứng
            current_date = start_date + timedelta(days=i)
            date_timestamp = int(current_date.timestamp() * 1000)  # Convert to milliseconds
            
            daily_meals = convert_daily_plan_to_meals_format(daily_plan, date_timestamp)
            weekly_meals.append(daily_meals)
    
    return weekly_meals

@app.route('/api/daily-meal', methods=['POST'])
def create_daily_meal():
    """Tạo thực đơn cho 1 ngày"""
    try:
        if model is None or tokenizer is None or recipes is None or recipe_sim_matrix is None:
            return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 503
        
        data = request.get_json()
        
        favorite_ingredients = data.get('favorite_ingredients', [])
        not_favorite_ingredients = data.get('not_favorite_ingredients', [])
        allergy_ingredients = data.get('allergy_ingredients', [])
        favorite_recipes = data.get('favorite_recipes', [])
        not_favorite_recipes = data.get('not_favorite_recipes', [])
        diet_mode = data.get('diet_mode', 'normal')
        serving_size = data.get('serving_size', 2)
        date_str = data.get('date')
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                target_date = datetime.now()
        else:
            target_date = datetime.now()
        
        date_timestamp = int(target_date.timestamp() * 1000)  # Convert to milliseconds
        
        user_profile = get_default_user_profile()
        if favorite_ingredients:
            user_profile["favoriteIngredientIds"] = favorite_ingredients
        if not_favorite_ingredients:
            user_profile["notFavoriteIngredientIds"] = not_favorite_ingredients
        if allergy_ingredients:
            user_profile["allergyIngredientIds"] = allergy_ingredients
        if favorite_recipes:
            user_profile["favoriteRecipeIds"] = favorite_recipes
        if not_favorite_recipes:
            user_profile["notFavoriteRecipeIds"] = not_favorite_recipes
        
        user_requirements = get_default_user_requirements()
        user_requirements["difficulty"] = "1"
        user_requirements["excludeMethod"] = []
        
        daily_plan = suggest_daily_meals(
            recipes=recipes,
            similarity_matrix=recipe_sim_matrix,
            user_profile=user_profile,
            user_requirements=user_requirements,
            ingredient_name_to_id=ingredient_name_to_id,
            tag_name_to_id=tag_name_to_id,
            ingredient_sim_matrix=ingredient_sim_matrix,
            tag_sim_matrix=tag_sim_matrix,
            all_ingredient_names=all_ingredient_names,
            all_tag_names=all_tag_names,
            all_ingredient_ids=all_ingredient_ids,
            all_tag_ids=all_tag_ids,
            serving_size=serving_size
        )
        meals_format = convert_daily_plan_to_meals_format(daily_plan, date_timestamp)
        
        response = {
            "success": True,
            "data": meals_format,
            "user_profile": {
                "cookedRecipeIds": user_profile.get("cookedRecipeIds", []),
                "favoriteIngredientIds": user_profile.get("favoriteIngredientIds", []),
                "notFavoriteIngredientIds": user_profile.get("notFavoriteIngredientIds", [])
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weekly-meal', methods=['POST'])
def create_weekly_meal():
    """Tạo thực đơn cho 1 tuần"""
    try:
        if model is None or tokenizer is None or recipes is None or recipe_sim_matrix is None:
            return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 503
        
        data = request.get_json()
        
        favorite_ingredients = data.get('favorite_ingredients', [])
        not_favorite_ingredients = data.get('not_favorite_ingredients', [])
        allergy_ingredients = data.get('allergy_ingredients', [])
        favorite_recipes = data.get('favorite_recipes', [])
        not_favorite_recipes = data.get('not_favorite_recipes', [])
        diet_mode = data.get('diet_mode', 'normal')
        serving_size = data.get('serving_size', 2)
        start_date_str = data.get('start_date')
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                start_date = datetime.now()
        else:
            start_date = datetime.now()
        
        user_profile = get_default_user_profile()
        if favorite_ingredients:
            user_profile["favoriteIngredientIds"] = favorite_ingredients
        if not_favorite_ingredients:
            user_profile["notFavoriteIngredientIds"] = not_favorite_ingredients
        if allergy_ingredients:
            user_profile["allergyIngredientIds"] = allergy_ingredients
        if favorite_recipes:
            user_profile["favoriteRecipeIds"] = favorite_recipes
        if not_favorite_recipes:
            user_profile["notFavoriteRecipeIds"] = not_favorite_recipes
            
        user_requirements = get_default_user_requirements()
        user_requirements["difficulty"] = "1"
        user_requirements["excludeMethod"] = []
        
        weekly_plan = generate_weekly_meal_plan(
            recipes=recipes,
            similarity_matrix=recipe_sim_matrix,
            user_profile=user_profile,
            user_requirements=user_requirements,
            ingredient_name_to_id=ingredient_name_to_id,
            tag_name_to_id=tag_name_to_id,
            ingredient_sim_matrix=ingredient_sim_matrix,
            tag_sim_matrix=tag_sim_matrix,
            all_ingredient_names=all_ingredient_names,
            all_tag_names=all_tag_names,
            all_ingredient_ids=all_ingredient_ids,
            all_tag_ids=all_tag_ids,
            serving_size=serving_size
        )
        
        weekly_meals = convert_weekly_plan_to_meals_format(weekly_plan, start_date)
        
        response = {
            "success": True,
            "data": weekly_meals,
            "user_profile": {
                "cookedRecipeIds": user_profile.get("cookedRecipeIds", []),
                "favoriteIngredientIds": user_profile.get("favoriteIngredientIds", []),
                "notFavoriteIngredientIds": user_profile.get("notFavoriteIngredientIds", [])
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/replace-recipe', methods=['POST'])
def replace_recipe():
    """Thay thế món ăn trong daily plan"""
    try:
        if model is None or tokenizer is None or recipes is None or recipe_sim_matrix is None:
            return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 503
        
        data = request.get_json()
        
        daily_plan = data.get('daily_plan')
        meal_type = data.get('meal_type')
        recipe_id = data.get('recipe_id')
        replacement_reason = data.get('replacement_reason')
        
        if daily_plan is None or meal_type is None or recipe_id is None or replacement_reason is None:
            return jsonify({
                "success": False,
                "error": "Thiếu thông tin bắt buộc: daily_plan, meal_type, recipe_id, replacement_reason"
            }), 400
        
        favorite_ingredients = data.get('favorite_ingredients', [])
        not_favorite_ingredients = data.get('not_favorite_ingredients', [])
        allergy_ingredients = data.get('allergy_ingredients', [])
        favorite_recipes = data.get('favorite_recipes', [])
        not_favorite_recipes = data.get('not_favorite_recipes', [])
        diet_mode = data.get('diet_mode', 'normal')
        serving_size = data.get('serving_size', 2)
        
        recipe_name = None
        meal_type_str = str(meal_type) if meal_type is not None else ""
        recipe_id_str = str(recipe_id) if recipe_id is not None else ""
        
        for meal in daily_plan.get("meals", []):
            if str(meal.get("mealTypeId", "")) == meal_type_str:
                for recipe_type, recipe_ids in meal.get("mapRecipe", {}).items():
                    if recipe_id_str in [str(rid) for rid in recipe_ids]:
                        for recipe in recipes:
                            if str(recipe.get("id", "")) == recipe_id_str:
                                recipe_name = recipe.get("name")
                                break
                        break
                if recipe_name:
                    break
        
        if not recipe_name:
            return jsonify({
                "success": False,
                "error": f"Không tìm thấy recipe với ID: {recipe_id}"
            }), 400
        
        user_profile = get_default_user_profile()
        if favorite_ingredients:
            user_profile["favoriteIngredientIds"] = favorite_ingredients
        if not_favorite_ingredients:
            user_profile["notFavoriteIngredientIds"] = not_favorite_ingredients
        if allergy_ingredients:
            user_profile["allergyIngredientIds"] = allergy_ingredients
        if favorite_recipes:
            user_profile["favoriteRecipeIds"] = favorite_recipes
        if not_favorite_recipes:
            user_profile["notFavoriteRecipeIds"] = not_favorite_recipes
        
        user_requirements = get_default_user_requirements()
        user_requirements["difficulty"] = "1"
        user_requirements["excludeMethod"] = []
        
        updated_plan = replace_recipe_in_daily_plan(
            recipes=recipes,
            similarity_matrix=recipe_sim_matrix,
            user_profile=user_profile,
            user_requirements=user_requirements,
            ingredient_name_to_id=ingredient_name_to_id,
            tag_name_to_id=tag_name_to_id,
            ingredient_sim_matrix=ingredient_sim_matrix,
            tag_sim_matrix=tag_sim_matrix,
            all_ingredient_names=all_ingredient_names,
            all_tag_names=all_tag_names,
            all_ingredient_ids=all_ingredient_ids,
            all_tag_ids=all_tag_ids,
            daily_plan=daily_plan,
            meal_type=meal_type,
            recipe_id_to_replace=recipe_id,
            replacement_reason=replacement_reason
        )
        
        if updated_plan:
            date_timestamp = daily_plan.get("date", int(datetime.now().timestamp() * 1000))
            meals_format = convert_daily_plan_to_meals_format(updated_plan, date_timestamp)
            
            response = {
                "success": True,
                "data": meals_format,
                "user_profile": {
                    "cookedRecipeIds": user_profile.get("cookedRecipeIds", []),
                    "favoriteIngredientIds": user_profile.get("favoriteIngredientIds", []),
                    "notFavoriteIngredientIds": user_profile.get("notFavoriteIngredientIds", [])
                }
            }
            return jsonify(response), 200
        else:
            return jsonify({
                "success": False,
                "error": "Không thể thay thế món ăn"
            }), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    if initialize_system():
        print("🌐 Khởi động Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Không thể khởi động server do lỗi khởi tạo hệ thống")
