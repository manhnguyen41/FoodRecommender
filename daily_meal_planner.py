import numpy as np
from recommendation import recommend_top_k_from_profile_and_requirements

def suggest_daily_meals(recipes, similarity_matrix, user_profile, user_requirements,
                        ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
                        tag_sim_matrix, all_ingredient_names, all_tag_names,
                        all_ingredient_ids, all_tag_ids, serving_size=2):
    """
    Gợi ý món ăn cho 1 ngày với 3 bữa (sáng, trưa, tối)
    
    Logic gợi ý:
    - Bữa sáng: 1 món chính
    - Bữa trưa và tối: 
      * 1 món canh (cho bất kỳ số người)
      * 2 món chính (cho mỗi 2 người)
      * 1 món phụ (cho mỗi 2 người)
      * 1 món tráng miệng (cho bất kỳ số người)
    
    Args:
        recipes (list): Danh sách tất cả recipes
        similarity_matrix (np.ndarray): Recipe similarity matrix
        user_profile (dict): User profile (sẽ được cập nhật cookedRecipeIds)
        user_requirements (dict): User requirements
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        serving_size (int): Số lượng người ăn
    
    Returns:
        dict: Dictionary chứa 3 bữa với recipes và thông tin chi tiết
    """
    
    def get_meal_suggestions(meal_type, serving_size=2):
        """Lấy suggestions cho một bữa cụ thể"""
        # Tạo requirements cho bữa cụ thể
        meal_requirements = user_requirements.copy()
        meal_requirements["mealType"] = meal_type
        meal_requirements["difficulty"] = user_requirements.get("difficulty", "1")  # Mặc định độ khó = 1
        
        if str(meal_type) == "bữa sáng":
            # Bữa sáng: chỉ lấy 1 món
            meal_requirements["recipeType"] = []
            suggested_recipes, scores = recommend_top_k_from_profile_and_requirements(
            recipes, similarity_matrix, user_profile, meal_requirements,
            ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
            tag_sim_matrix, all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids, k=1
            )
            
            # Thêm món bữa sáng vào danh sách đã nấu
            for recipe in suggested_recipes:
                recipe["recipe_type"] = ["món chính"]
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in user_profile.get("cookedRecipeIds", []):
                    user_profile["cookedRecipeIds"].append(recipe_id)
        else:
            # Bữa trưa và tối: lấy theo cấu trúc món ăn
            # 1 món canh (cho bất kỳ số người)
            soup_requirements = meal_requirements.copy()
            soup_requirements["recipeType"] = ["món canh"]
            soup_recipes, soup_scores = recommend_top_k_from_profile_and_requirements(
                recipes, similarity_matrix, user_profile, soup_requirements,
                ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
                tag_sim_matrix, all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids, k=1
            )
            
            # Thêm món canh vào danh sách đã nấu
            for recipe in soup_recipes:
                recipe["recipe_type"] = ["món canh"]
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in user_profile.get("cookedRecipeIds", []):
                    user_profile["cookedRecipeIds"].append(recipe_id)
            
            # 2 món chính (cho mỗi 2 người)
            main_dish_count = max(1, serving_size // 2 * 2)
            main_requirements = meal_requirements.copy()
            main_requirements["recipeType"] = ["món chính"]
            main_recipes, main_scores = recommend_top_k_from_profile_and_requirements(
                recipes, similarity_matrix, user_profile, main_requirements,
                ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
                tag_sim_matrix, all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids, k=main_dish_count
            )
            
            # Thêm món chính vào danh sách đã nấu
            for recipe in main_recipes:
                recipe["recipe_type"] = ["món chính"]
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in user_profile.get("cookedRecipeIds", []):
                    user_profile["cookedRecipeIds"].append(recipe_id)
            
            # 1 món phụ (cho mỗi 2 người)
            side_dish_count = max(1, serving_size // 2)
            side_requirements = meal_requirements.copy()
            side_requirements["recipeType"] = ["món phụ"]
            side_recipes, side_scores = recommend_top_k_from_profile_and_requirements(
                recipes, similarity_matrix, user_profile, side_requirements,
                ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
                tag_sim_matrix, all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids, k=side_dish_count
            )
            
            # Thêm món phụ vào danh sách đã nấu
            for recipe in side_recipes:
                recipe["recipe_type"] = ["món phụ"]
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in user_profile.get("cookedRecipeIds", []):
                    user_profile["cookedRecipeIds"].append(recipe_id)
            
            # 1 món tráng miệng (cho bất kỳ số người)
            dessert_requirements = meal_requirements.copy()
            dessert_requirements["recipeType"] = ["món tráng miệng"]
            dessert_recipes, dessert_scores = recommend_top_k_from_profile_and_requirements(
                recipes, similarity_matrix, user_profile, dessert_requirements,
                ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
                tag_sim_matrix, all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids, k=1
            )
            
            # Thêm món tráng miệng vào danh sách đã nấu
            for recipe in dessert_recipes:
                recipe["recipe_type"] = ["món tráng miệng"]
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in user_profile.get("cookedRecipeIds", []):
                    user_profile["cookedRecipeIds"].append(recipe_id)
            
            # Gộp tất cả món ăn
            suggested_recipes = soup_recipes + main_recipes + side_recipes + dessert_recipes
            scores = soup_scores + main_scores + side_scores + dessert_scores
            
        return suggested_recipes, scores
    
    # Lấy suggestions cho từng bữa
    breakfast_recipes, breakfast_scores = get_meal_suggestions("bữa sáng", serving_size)
    lunch_recipes, lunch_scores = get_meal_suggestions("bữa trưa", serving_size)
    dinner_recipes, dinner_scores = get_meal_suggestions("bữa tối", serving_size)
    
   
    daily_plan = {
        "meals": [
            {
                "mealTypeId": "bữa sáng",
                "mapRecipe": {
                    "món chính": [recipe.get("id") for recipe in breakfast_recipes],
                    "món phụ": [],
                    "món canh": [],
                    "món tráng miệng": []
                }
            },
            {
                "mealTypeId": "bữa trưa",
                "mapRecipe": {
                    "món chính": [recipe.get("id") for recipe in lunch_recipes if recipe.get("recipe_type") and "món chính" in recipe.get("recipe_type", [])],
                    "món phụ": [recipe.get("id") for recipe in lunch_recipes if recipe.get("recipe_type") and "món phụ" in recipe.get("recipe_type", [])],
                    "món canh": [recipe.get("id") for recipe in lunch_recipes if recipe.get("recipe_type") and "món canh" in recipe.get("recipe_type", [])],
                    "món tráng miệng": [recipe.get("id") for recipe in lunch_recipes if recipe.get("recipe_type") and "món tráng miệng" in recipe.get("recipe_type", [])]
                }
            },
            {
                "mealTypeId": "bữa tối",
                "mapRecipe": {
                    "món chính": [recipe.get("id") for recipe in dinner_recipes if recipe.get("recipe_type") and "món chính" in recipe.get("recipe_type", [])],
                    "món phụ": [recipe.get("id") for recipe in dinner_recipes if recipe.get("recipe_type") and "món phụ" in recipe.get("recipe_type", [])],
                    "món canh": [recipe.get("id") for recipe in dinner_recipes if recipe.get("recipe_type") and "món canh" in recipe.get("recipe_type", [])],
                    "món tráng miệng": [recipe.get("id") for recipe in dinner_recipes if recipe.get("recipe_type") and "món tráng miệng" in recipe.get("recipe_type", [])]
                }
            }
        ]
    }
    
    # Tính tổng cho cả ngày
    all_recipes = breakfast_recipes + lunch_recipes + dinner_recipes
    daily_plan["daily_summary"] = {
        "serving_size": serving_size,
        "total_recipes": len(all_recipes),
        "breakfast_count": len(breakfast_recipes),
        "lunch_count": len(lunch_recipes),
        "dinner_count": len(dinner_recipes)
    }
    
    return daily_plan

def get_default_user_profile():
    """
    Trả về user profile mặc định nếu không có thông tin
    
    Returns:
        dict: Default user profile
    """
    return {
        "familyId": "default",
        "favoriteIngredientIds": [],
        "notFavoriteIngredientIds": [],
        "allergyIngredientIds": [],
        "suggestedDietModeIngredientIds": [],
        "suggestedPathologyIngredientIds": [],
        "notSuggestedDietModeIngredientIds": [],
        "notSuggestedPathologyIngredientIds": [],
        "includeTags": [],
        "excludeTags": [],
        "favoriteRecipeIds": [],
        "notFavoriteRecipeIds": [],
        "cookedRecipeIds": [],
        "feedbackRecipeIds": {}
    }

def get_default_user_requirements():
    """
    Trả về user requirements mặc định
    
    Returns:
        dict: Default user requirements
    """
    return {
        "mealType": "all",
        "availableIngredientIds": [],
        "difficulty": "1",  # Mặc định độ khó = 1 (dễ nhất)
        "excludeMethod": []  # Mặc định không loại trừ cách chế biến nào
    }

def create_user_profile_from_inputs(
    favorite_ingredients=None,
    not_favorite_ingredients=None,
    allergy_ingredients=None,
    favorite_recipes=None,
    not_favorite_recipes=None
):
    """
    Tạo user profile từ các input đơn giản
    
    Args:
        favorite_ingredients (list): Danh sách tên nguyên liệu yêu thích
        not_favorite_ingredients (list): Danh sách tên nguyên liệu không thích
        allergy_ingredients (list): Danh sách tên nguyên liệu dị ứng
        favorite_recipes (list): Danh sách tên món ăn yêu thích
        not_favorite_recipes (list): Danh sách tên món ăn không thích
    
    Returns:
        dict: User profile
    """
    # Sử dụng default nếu không có input
    if favorite_ingredients is None:
        favorite_ingredients = []
    if not_favorite_ingredients is None:
        not_favorite_ingredients = []
    if allergy_ingredients is None:
        allergy_ingredients = []
    if favorite_recipes is None:
        favorite_recipes = []
    if not_favorite_recipes is None:
        not_favorite_recipes = []
    
    return {
        "familyId": "user_input",
        "favoriteIngredientIds": favorite_ingredients,
        "notFavoriteIngredientIds": not_favorite_ingredients,
        "allergyIngredientIds": allergy_ingredients,
        "suggestedDietModeIngredientIds": [],
        "suggestedPathologyIngredientIds": [],
        "notSuggestedDietModeIngredientIds": [],
        "notSuggestedPathologyIngredientIds": [],
        "includeTags": [],
        "excludeTags": [],
        "favoriteRecipeIds": favorite_recipes,
        "notFavoriteRecipeIds": not_favorite_recipes,
        "cookedRecipeIds": [],
        "feedbackRecipeIds": {}
    }

def create_user_requirements_from_inputs(
    serving_size=2,
    available_ingredients=None,
    difficulty=1,
    exclude_methods=None
):
    """
    Tạo user requirements từ các input đơn giản
    
    Args:
        serving_size (int): Số lượng người ăn
        available_ingredients (list): Danh sách nguyên liệu có sẵn
        difficulty (int): Độ khó của món ăn
        exclude_methods (list): Danh sách cách chế biến muốn loại trừ
    
    Returns:
        dict: User requirements
    """
    if available_ingredients is None:
        available_ingredients = []
    if exclude_methods is None:
        exclude_methods = []
    
    return {
        "mealType": "all",
        "availableIngredientIds": available_ingredients, 
        "serving_size": serving_size,
        "difficulty": difficulty,
        "excludeMethod": exclude_methods
    }

def replace_recipe_in_meal(
    recipes,
    similarity_matrix,
    user_profile,
    user_requirements,
    ingredient_name_to_id,
    tag_name_to_id,
    ingredient_sim_matrix,
    tag_sim_matrix,
    all_ingredient_names,
    all_tag_names,
    all_ingredient_ids,
    all_tag_ids,
    meal_type,
    recipe_to_replace,
    replacement_reason,
):
    """
    Thay thế 1 món ăn trong bữa ăn dựa trên lý do cụ thể.
    
    Args:
        recipes (list): Danh sách tất cả recipes
        similarity_matrix (np.ndarray): Recipe similarity matrix
        user_profile (dict): User profile
        user_requirements (dict): User requirements
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        meal_type (str): Loại bữa ăn ("breakfast", "lunch", "dinner")
        recipe_to_replace (dict): Recipe cần thay thế
        replacement_reason (str): Lý do thay thế ("ingredients", "difficulty", "method")
    
    Returns:
        tuple: (new_recipe, new_score) hoặc (None, None) nếu không tìm được
    """
    
    # Tạo requirements cho bữa ăn
    meal_requirements = user_requirements.copy()
    meal_requirements["mealType"] = meal_type
    meal_requirements["difficulty"] = user_requirements.get("difficulty", "1")
    
    # Chuyển đổi sang string để so sánh an toàn
    replacement_reason_str = str(replacement_reason) if replacement_reason is not None else ""
    
    if replacement_reason_str == "ingredients":
        # Tìm món có độ tương đồng thấp nhất với món muốn thay
        return _find_least_similar_recipe(
            recipes, similarity_matrix, user_profile, meal_requirements,
            ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
            tag_sim_matrix, all_ingredient_names, all_tag_names,
            all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
        )
    
    elif replacement_reason_str == "difficulty":
        # Tìm món có độ khó thấp hơn hoặc bằng nhưng khác món
        return _find_lower_difficulty_recipe(
            recipes, similarity_matrix, user_profile, meal_requirements,
            ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
            tag_sim_matrix, all_ingredient_names, all_tag_names,
            all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
        )
    
    elif replacement_reason_str == "method":
        # Tìm món có cách chế biến khác
        return _find_different_method_recipe(
            recipes, similarity_matrix, user_profile, meal_requirements,
            ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
            tag_sim_matrix, all_ingredient_names, all_tag_names,
            all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
        )
    
    else:
        return None, None


def _find_least_similar_recipe(
    recipes, similarity_matrix, user_profile, meal_requirements,
    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
    tag_sim_matrix, all_ingredient_names, all_tag_names,
    all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
):
    """Tìm món có độ tương đồng thấp nhất với món muốn thay"""
    
    # Tạo user_profile tạm thời từ profile cũ
    temp_user_profile = user_profile.copy()
    old_recipe_id = recipe_to_replace.get("id")
    if old_recipe_id and old_recipe_id not in temp_user_profile.get("notFavoriteRecipeIds", []):
        temp_user_profile["notFavoriteRecipeIds"].append(old_recipe_id)
    temp_user_requirements = meal_requirements.copy()
    temp_user_requirements["recipeType"] = [recipe_to_replace.get("recipe_type", [])[0]]
    # Xác định recipe_type cần tìm dựa trên meal_type
    if str(meal_type) == "breakfast":
        meal_requirements["recipeType"] = []
        k = 1
    else:
        # Xác định loại món của recipe cần thay
        recipe_type = recipe_to_replace.get("recipe_type", [])
        if recipe_type:
            meal_requirements["recipeType"] = recipe_type
        k = 1
    
    # Lấy danh sách món phù hợp với profile tạm thời
    candidates, scores = recommend_top_k_from_profile_and_requirements(
        recipes, similarity_matrix, temp_user_profile, temp_user_requirements,
        ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
        tag_sim_matrix, all_ingredient_names, all_tag_names,
        all_ingredient_ids, all_tag_ids, k=1  # Chỉ cần 1 món thay thế
    )
    
    if not candidates:
        return None, None
    
    # Lấy món đầu tiên (đã được recommend_top_k_from_profile_and_requirements sắp xếp theo score)
    best_candidate = candidates[0]
    best_score = scores[0]
    
    if best_candidate:
        # Thêm món mới vào cookedRecipeIds của profile gốc
        new_recipe_id = best_candidate.get("id")
        if new_recipe_id and new_recipe_id not in user_profile.get("cookedRecipeIds", []):
            user_profile["cookedRecipeIds"].append(new_recipe_id)
        
        return best_candidate, best_score
    
    return None, None


def _find_lower_difficulty_recipe(
    recipes, similarity_matrix, user_profile, meal_requirements,
    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
    tag_sim_matrix, all_ingredient_names, all_tag_names,
    all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
):
    """Tìm món có độ khó thấp hơn hoặc bằng nhưng khác món"""
    
    # Tạo user_profile tạm thời từ profile cũ
    temp_meal_requirements = meal_requirements.copy()
    temp_meal_requirements["recipeType"] = [recipe_to_replace.get("recipe_type", [])[0]]

    old_difficulty = recipe_to_replace.get("difficulty", "1")
    if str(old_difficulty) == "2":
        temp_meal_requirements["difficulty"] = "1"
    elif str(old_difficulty) == "3":
        temp_meal_requirements["difficulty"] = "2"

    # Xác định recipe_type cần tìm
    if str(meal_type) == "breakfast":
        temp_meal_requirements["recipeType"] = []
        k = 1
    else:
        recipe_type = recipe_to_replace.get("recipe_type", [])
        if recipe_type:
            temp_meal_requirements["recipeType"] = recipe_type
        k = 1
    
    # Lấy danh sách món phù hợp với profile tạm thời
    candidates, scores = recommend_top_k_from_profile_and_requirements(
        recipes, similarity_matrix, user_profile, temp_meal_requirements,
        ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
        tag_sim_matrix, all_ingredient_names, all_tag_names,
        all_ingredient_ids, all_tag_ids, k=1  # Chỉ cần 1 món thay thế
    )
    
    if not candidates:
        return None, None
    
    # Lấy món đầu tiên (đã được recommend_top_k_from_profile_and_requirements sắp xếp theo score)
    best_candidate = candidates[0]
    best_score = scores[0]
    
    if best_candidate:
        # Thêm món mới vào cookedRecipeIds của profile gốc
        new_recipe_id = best_candidate.get("id")
        if new_recipe_id and new_recipe_id not in user_profile.get("cookedRecipeIds", []):
            user_profile["cookedRecipeIds"].append(new_recipe_id)
        
        old_difficulty = recipe_to_replace.get("difficulty", "1")
        print(f"🔄 Đã thay món '{recipe_to_replace['name']}' (độ khó: {old_difficulty}) bằng '{best_candidate['name']}' (độ khó: {best_candidate.get('difficulty', '1')}) (score: {best_score:.3f})")
        return best_candidate, best_score
    
    return None, None


def _find_different_method_recipe(
    recipes, similarity_matrix, user_profile, meal_requirements,
    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
    tag_sim_matrix, all_ingredient_names, all_tag_names,
    all_ingredient_ids, all_tag_ids, recipe_to_replace, meal_type
):
    """Tìm món có cách chế biến khác"""

    # Tạo user_profile tạm thời từ profile cũ
    temp_meal_requirements = meal_requirements.copy()
    temp_meal_requirements["recipeType"] = [recipe_to_replace.get("recipe_type", [])[0]]
    # Thêm món cũ vào notFavoriteRecipeIds để tránh gợi ý lại
    old_methods = recipe_to_replace.get("method", [])
    if old_methods:
        temp_meal_requirements["excludeMethod"] = old_methods
    
    # Xác định recipe_type cần tìm
    if str(meal_type) == "bữa sáng":
        temp_meal_requirements["recipeType"] = []
        k = 1
    else:
        recipe_type = recipe_to_replace.get("recipe_type", [])
        if recipe_type:
            temp_meal_requirements["recipeType"] = recipe_type
        k = 1
    
    # Lấy danh sách món phù hợp với profile tạm thời
    candidates, scores = recommend_top_k_from_profile_and_requirements(
        recipes, similarity_matrix, user_profile, temp_meal_requirements,
        ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
        tag_sim_matrix, all_ingredient_names, all_tag_names,
        all_ingredient_ids, all_tag_ids, k=1  # Chỉ cần 1 món thay thế
    )
    if not candidates:
        return None, None
    
    # Lấy món đầu tiên (đã được recommend_top_k_from_profile_and_requirements sắp xếp theo score)
    best_candidate = candidates[0]
    best_score = scores[0]
    
    if best_candidate:
        # Thêm món mới vào cookedRecipeIds của profile gốc
        new_recipe_id = best_candidate.get("id")
        if new_recipe_id and new_recipe_id not in user_profile.get("cookedRecipeIds", []):
            user_profile["cookedRecipeIds"].append(new_recipe_id)
        
        return best_candidate, best_score
    
    return None, None


def update_daily_plan_after_replacement(
    daily_plan,
    meal_type,
    old_recipe_id,
    new_recipe,
    new_score
):
    """
    Cập nhật daily plan sau khi thay thế món ăn.
    
    Args:
        daily_plan (dict): Daily plan hiện tại theo định dạng API mới
        meal_type (str): Loại bữa ăn ("breakfast", "lunch", "dinner")
        old_recipe_id (str): ID của recipe cũ
        new_recipe (dict): Recipe mới
        new_score (float): Score của recipe mới
    
    Returns:
        dict: Daily plan đã được cập nhật
    """
    
    # Tìm meal entry trong daily_plan
    meal_entry = None
    for meal in daily_plan.get("meals", []):
        if str(meal.get("mealTypeId", "")) == str(meal_type):
            meal_entry = meal
            break
    
    if not meal_entry:
        return daily_plan
    
    # Cập nhật mapRecipe - thay thế old_recipe_id bằng new_recipe["id"]
    map_recipe = meal_entry.get("mapRecipe", {})
    
    # Tìm và thay thế trong tất cả các loại món
    for recipe_type, recipe_ids in map_recipe.items():
        if isinstance(recipe_ids, list):
            for i, recipe_id in enumerate(recipe_ids):
                if str(recipe_id) == str(old_recipe_id):
                    # Thay thế ID cũ bằng ID mới
                    map_recipe[recipe_type][i] = new_recipe["id"]
                    break
    
    return daily_plan


def suggest_daily_meals_simple(
    recipes,
    similarity_matrix,
    ingredient_name_to_id,
    tag_name_to_id,
    ingredient_sim_matrix,
    tag_sim_matrix,
    all_ingredient_names,
    all_tag_names,
    all_ingredient_ids,
    all_tag_ids,
    favorite_ingredients=None,
    not_favorite_ingredients=None,
    allergy_ingredients=None,
    favorite_recipes=None,
    not_favorite_recipes=None,
    serving_size=2,
    available_ingredients=None,
    difficulty=1,
    exclude_methods=None,
    use_default=False
):
    """
    Hàm gợi ý món ăn cho 1 ngày với interface đơn giản
    
    Args:
        recipes (list): Danh sách recipes
        similarity_matrix (np.ndarray): Recipe similarity matrix
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        favorite_ingredients (list): Danh sách tên nguyên liệu yêu thích
        not_favorite_ingredients (list): Danh sách tên nguyên liệu không thích
        allergy_ingredients (list): Danh sách tên nguyên liệu dị ứng
        favorite_recipes (list): Danh sách tên món ăn yêu thích
        not_favorite_recipes (list): Danh sách tên món ăn không thích
        serving_size (int): Số lượng người ăn
        available_ingredients (list): Danh sách nguyên liệu có sẵn
        difficulty (int): Độ khó của món ăn
        use_default (bool): Sử dụng profile mặc định nếu True
    
    Returns:
        dict: Daily meal plan
    """
    
    if use_default:
        # Sử dụng profile mặc định
        user_profile = get_default_user_profile()
        user_requirements = get_default_user_requirements()
    else:
        # Tạo profile từ inputs
        user_profile = create_user_profile_from_inputs(
            favorite_ingredients=favorite_ingredients,
            not_favorite_ingredients=not_favorite_ingredients,
            allergy_ingredients=allergy_ingredients,
            favorite_recipes=favorite_recipes,
            not_favorite_recipes=not_favorite_recipes
        )
        
        user_requirements = create_user_requirements_from_inputs(
            serving_size=serving_size,
            available_ingredients=available_ingredients,
            difficulty=difficulty,
            exclude_methods=exclude_methods
        )
    
    # Gọi hàm gợi ý chính
    daily_plan = suggest_daily_meals(
        recipes=recipes,
        similarity_matrix=similarity_matrix,
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
    
    return daily_plan


def replace_recipe_in_daily_plan(
    recipes, similarity_matrix, user_profile, user_requirements,
    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
    tag_sim_matrix, all_ingredient_names, all_tag_names,
    all_ingredient_ids, all_tag_ids, daily_plan, meal_type, 
    recipe_id_to_replace, replacement_reason
):
    """
    Thay thế một món ăn trong daily plan dựa trên lý do cụ thể
    
    Args:
        recipes (list): Danh sách recipes
        similarity_matrix (np.ndarray): Recipe similarity matrix
        user_profile (dict): User profile
        user_requirements (dict): User requirements
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        daily_plan (dict): Daily plan theo định dạng API mới
        meal_type (str): Loại bữa ăn ("breakfast", "lunch", "dinner")
        recipe_id_to_replace (str): ID của món ăn cần thay thế
        replacement_reason (str): Lý do thay thế ("ingredients", "difficulty", "method")
    
    Returns:
        dict: Daily plan đã được cập nhật hoặc None nếu không tìm được
    """
    # Tìm meal entry trong daily_plan
    
    meal_entry = None
    for meal in daily_plan.get("meals", []):
        if str(meal.get("mealTypeId", "")) == str(meal_type):
            meal_entry = meal
            break
    
    if not meal_entry:
        return None
    
    # Tìm recipe cần thay thế trong global recipes list
    recipe_to_replace = None
    for recipe in recipes:
        if str(recipe.get("id", "")) == str(recipe_id_to_replace):
            recipe_to_replace = recipe
            break
    
    if not recipe_to_replace:
        return None
    
    # Thực hiện thay thế
    new_recipe, new_score = replace_recipe_in_meal(
        recipes, similarity_matrix, user_profile, user_requirements,
        ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix,
        tag_sim_matrix, all_ingredient_names, all_tag_names,
        all_ingredient_ids, all_tag_ids, meal_type, recipe_to_replace,
        replacement_reason
    )
    
    if new_recipe:
        # Cập nhật daily plan
        updated_plan = update_daily_plan_after_replacement(
            daily_plan, meal_type, recipe_id_to_replace, new_recipe, new_score
        )
        return updated_plan
    else:
        return None


def main():
    """
    Hàm main để test chức năng gợi ý món ăn
    """
    from embeddings import load_phobert_model
    from utils import load_data
    from similarity import (
        create_recipe_similarity_matrix,
        create_ingredient_similarity_matrix, 
        create_tag_similarity_matrix
    )
    
    print("🚀 Đang khởi tạo hệ thống gợi ý món ăn...")
    
    try:
        # Load model và data
        print("📚 Đang load PhoBERT model...")
        model, tokenizer = load_phobert_model()
        print("✅ Đã load xong PhoBERT model!")
        
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

        # Test với profile mặc định và độ khó = 1 (dễ nhất)
        print("\n🍽️ Test gợi ý với profile mặc định (độ khó = 1):")
        
        # Tạo user profile và requirements để sử dụng xuyên suốt
        user_profile = get_default_user_profile()
        user_requirements = get_default_user_requirements()
        user_requirements["excludeMethod"] = []  # Không loại trừ cách chế biến nào
        
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
            serving_size=2
        )

        # In kết quả
        print("\n📋 Kết quả gợi ý món ăn cho 1 ngày:")
        for meal in daily_plan.get("meals", []):
            meal_type = meal["mealTypeId"]
            print(f"\n🕐 {meal_type.upper()}:")
            map_recipe = meal.get("mapRecipe", {})
            for recipe_type, recipe_ids in map_recipe.items():
                if recipe_ids:
                    print(f"  {recipe_type}: {len(recipe_ids)} món")
                    for recipe_id in recipe_ids:
                        # Tìm tên recipe từ ID
                        recipe_name = "Unknown"
                        for recipe in recipes:
                            if str(recipe.get("id", "")) == str(recipe_id):
                                recipe_name = recipe.get("name", "Unknown")
                                break
                        print(f"    - {recipe_name} (ID: {recipe_id})")
        
        # Demo chức năng thay thế món ăn
        print("\n" + "="*50)
        print("🧪 DEMO CHỨC NĂNG THAY THẾ MÓN ĂN")
        print("="*50)
        
        # Sử dụng cùng user profile và requirements đã được cập nhật từ việc gợi ý ban đầu
        demo_user_profile = user_profile  # Sử dụng profile đã có cookedRecipeIds
        demo_user_requirements = user_requirements  # Sử dụng requirements đã có excludeMethod
        
        # Demo 1: Thay thế món vì nguyên liệu (tìm món ít tương đồng nhất)
        print("\n🔍 Demo 1: Thay thế món vì nguyên liệu")
        lunch_meal = next((meal for meal in daily_plan.get("meals", []) if meal["mealTypeId"] == "bữa trưa"), None)
        if lunch_meal:
            # Lấy recipe ID đầu tiên từ món chính
            main_dish_ids = lunch_meal.get("mapRecipe", {}).get("món chính", [])
            if main_dish_ids:
                recipe_id_to_replace = main_dish_ids[0]
                # Tìm tên recipe từ ID
                recipe_name = "Unknown"
                for recipe in recipes:
                    if str(recipe.get("id", "")) == str(recipe_id_to_replace):
                        recipe_name = recipe.get("name", "Unknown")
                        break
                print(f"   Món cần thay: {recipe_name} (ID: {recipe_id_to_replace})")
                
                updated_plan = replace_recipe_in_daily_plan(
                    recipes, recipe_sim_matrix, demo_user_profile, demo_user_requirements,
                    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix, tag_sim_matrix,
                    all_ingredient_names, all_tag_names, all_ingredient_ids, all_tag_ids,
                    daily_plan, "lunch", recipe_id_to_replace, "ingredients"
                )
                
                if updated_plan:
                    print("   ✅ Thay thế thành công!")
        
        # Demo 2: Thay thế món vì độ khó
        print("\n🔍 Demo 2: Thay thế món vì độ khó")
        dinner_meal = next((meal for meal in daily_plan.get("meals", []) if meal["mealTypeId"] == "bữa tối"), None)
        if dinner_meal:
            # Lấy recipe ID đầu tiên từ món chính
            main_dish_ids = dinner_meal.get("mapRecipe", {}).get("món chính", [])
            if main_dish_ids:
                recipe_id_to_replace = main_dish_ids[0]
                # Tìm tên recipe từ ID
                recipe_name = "Unknown"
                for recipe in recipes:
                    if str(recipe.get("id", "")) == str(recipe_id_to_replace):
                        recipe_name = recipe.get("name", "Unknown")
                        break
                print(f"   Món cần thay: {recipe_name} (ID: {recipe_id_to_replace})")
                
                updated_plan = replace_recipe_in_daily_plan(
                    recipes, recipe_sim_matrix, demo_user_profile, demo_user_requirements,
                    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix, tag_sim_matrix,
                    all_ingredient_names, all_tag_names, all_ingredient_ids, all_tag_ids,
                    daily_plan, "dinner", recipe_id_to_replace, "difficulty"
                )
                
                if updated_plan:
                    print("   ✅ Thay thế thành công!")
        
        # Demo 3: Thay thế món vì cách chế biến
        print("\n🔍 Demo 3: Thay thế món vì cách chế biến")
        lunch_meal = next((meal for meal in daily_plan.get("meals", []) if meal["mealTypeId"] == "bữa trưa"), None)
        if lunch_meal:
            # Lấy recipe ID thứ hai từ món chính (nếu có)
            main_dish_ids = lunch_meal.get("mapRecipe", {}).get("món chính", [])
            if len(main_dish_ids) > 1:
                recipe_id_to_replace = main_dish_ids[1]
                # Tìm tên recipe từ ID
                recipe_name = "Unknown"
                for recipe in recipes:
                    if str(recipe.get("id", "")) == str(recipe_id_to_replace):
                        recipe_name = recipe.get("name", "Unknown")
                        break
                print(f"   Món cần thay: {recipe_name} (ID: {recipe_id_to_replace})")
                
                updated_plan = replace_recipe_in_daily_plan(
                    recipes, recipe_sim_matrix, demo_user_profile, demo_user_requirements,
                    ingredient_name_to_id, tag_name_to_id, ingredient_sim_matrix, tag_sim_matrix,
                    all_ingredient_names, all_tag_names, all_ingredient_ids, all_tag_ids,
                    daily_plan, "lunch", recipe_id_to_replace, "method"
                )
                
                if updated_plan:
                    print("   ✅ Thay thế thành công!")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    main()
