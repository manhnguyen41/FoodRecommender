import numpy as np

def get_ingredient_similarity_score(recipe_ingredients, user_ingredients, ingredient_sim_matrix, 
                                   ingredient_name_to_id, all_ingredient_names, all_ingredient_ids, is_positive=True):
    """
    Tính điểm similarity cho nguyên liệu dựa trên matrix
    
    Args:
        recipe_ingredients (list): Danh sách nguyên liệu của recipe
        user_ingredients (list): Danh sách ingredient IDs của user (favorite/not favorite)
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        ingredient_name_to_id (dict): Mapping ingredient name to id
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        is_positive (bool): True nếu là favorite, False nếu là not favorite
    
    Returns:
        float: Điểm similarity cao nhất
    """
    if not user_ingredients or not recipe_ingredients:
        return 0.0
    
    # Lấy ingredient IDs từ recipe ingredients
    recipe_ing_ids = [ing["ingredient_id"] for ing in recipe_ingredients]
    max_score = -10.0
    
    for user_ing_id in user_ingredients:
        # Tìm index của user ingredient trong all_ingredient_ids
        if user_ing_id in all_ingredient_ids:
            user_ing_idx = all_ingredient_ids.index(user_ing_id)
            
            # Tính similarity với từng nguyên liệu trong recipe
            for recipe_ing_id in recipe_ing_ids:
                if recipe_ing_id in all_ingredient_ids:
                    recipe_ing_idx = all_ingredient_ids.index(recipe_ing_id)
                    similarity = ingredient_sim_matrix[user_ing_idx][recipe_ing_idx]
                    
                    max_score = max(max_score, similarity)
    if is_positive:
        return max_score
    else:
        return -max_score

def get_tag_similarity_score(recipe_tags, user_tags, tag_sim_matrix, 
                            tag_name_to_id, all_tag_names, all_tag_ids, is_positive=True):
    """
    Tính điểm similarity cho tags dựa trên matrix
    
    Args:
        recipe_tags (list): Danh sách tags của recipe
        user_tags (list): Danh sách tag IDs của user
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        tag_name_to_id (dict): Mapping tag name to id
        all_tag_names (list): Danh sách tất cả tag names
        all_tag_ids (list): Danh sách tất cả tag IDs
        is_positive (bool): True nếu là include, False nếu là exclude
    
    Returns:
        float: Điểm similarity cao nhất
    """
    if not user_tags or not recipe_tags:
        return 0.0
    
    recipe_tag_ids = [tag["tag_id"] for tag in recipe_tags]
    max_score = -10.0
    
    for user_tag_id in user_tags:
        # Tìm index của user tag trong all_tag_ids
        if user_tag_id in all_tag_ids:
            user_tag_idx = all_tag_ids.index(user_tag_id)
                
            # Tính similarity với từng tag trong recipe
            for recipe_tag_id in recipe_tag_ids:
                if recipe_tag_id in all_tag_ids:
                    recipe_tag_idx = all_tag_ids.index(recipe_tag_id)
                    similarity = tag_sim_matrix[user_tag_idx][recipe_tag_idx]
                    
                    if is_positive:
                        max_score = max(max_score, similarity)
                    else:
                        max_score = max(max_score, -similarity)
    
    return max_score

def get_ingredient_availability_score(recipe_ingredients, available_ingredients, ingredient_sim_matrix,
                                     ingredient_name_to_id, all_ingredient_names, all_ingredient_ids):
    """
    Tính điểm cho nguyên liệu có sẵn dựa trên matrix similarity
    
    Args:
        recipe_ingredients (list): Danh sách nguyên liệu của recipe
        available_ingredients (list): Danh sách ingredient IDs có sẵn
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        ingredient_name_to_id (dict): Mapping ingredient name to id
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
    
    Returns:
        float: Điểm availability cao nhất
    """
    if not available_ingredients or not recipe_ingredients:
        return 0.0
    
    recipe_ing_ids = [ing["ingredient_id"] for ing in recipe_ingredients]
    max_score = -10.0
    
    for available_ing_id in available_ingredients:
        # Tìm index của available ingredient trong all_ingredient_ids
        if available_ing_id in all_ingredient_ids:
            available_ing_idx = all_ingredient_ids.index(available_ing_id)
                
            # Tính similarity với từng nguyên liệu trong recipe
            for recipe_ing_id in recipe_ing_ids:
                if recipe_ing_id in all_ingredient_ids:
                    recipe_ing_idx = all_ingredient_ids.index(recipe_ing_id)
                    similarity = ingredient_sim_matrix[available_ing_idx][recipe_ing_idx]
                    
                    # Nếu có nguyên liệu trùng khớp, cộng điểm cao
                    if similarity > 0.9:  # Threshold cho exact match
                        score = 3.0
                    else:
                        # Cộng điểm dựa trên similarity
                        score = similarity * 2.0
                    
                    max_score = max(max_score, score)
    
    return max_score

def get_diet_pathology_score(recipe_ingredients, suggested_ingredients, ingredient_sim_matrix,
                             ingredient_name_to_id, all_ingredient_names, all_ingredient_ids):
    """
    Tính điểm cho nguyên liệu được khuyến nghị dựa trên matrix similarity
    
    Args:
        recipe_ingredients (list): Danh sách nguyên liệu của recipe
        suggested_ingredients (list): Danh sách ingredient IDs được khuyến nghị
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        ingredient_name_to_id (dict): Mapping ingredient name to id
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
    
    Returns:
        float: Điểm diet/pathology cao nhất
    """
    if not suggested_ingredients or not recipe_ingredients:
        return 0.0
    
    recipe_ing_ids = [ing["ingredient_id"] for ing in recipe_ingredients]
    max_score = -10.0
    
    for suggested_ing_id in suggested_ingredients:
        # Tìm index của suggested ingredient trong all_ingredient_ids
        if suggested_ing_id in all_ingredient_ids:
            suggested_ing_idx = all_ingredient_ids.index(suggested_ing_id)
                
            # Tính similarity với từng nguyên liệu trong recipe
            for recipe_ing_id in recipe_ing_ids:
                if recipe_ing_id in all_ingredient_ids:
                    recipe_ing_idx = all_ingredient_ids.index(recipe_ing_id)
                    similarity = ingredient_sim_matrix[suggested_ing_idx][recipe_ing_idx]
                    
                    # Cộng điểm dựa trên similarity
                    max_score = max(max_score, similarity)
    
    return max_score

def get_meal_type_bonus_score(recipe_meal_types, meal_type):
    """
    Tính điểm bonus cho meal_type phù hợp
    
    Args:
        recipe_meal_types (list): Danh sách meal_type của recipe
        meal_type (str): Loại bữa cần kiểm tra (breakfast, lunch, dinner)
    
    Returns:
        float: Điểm bonus (0.0 nếu không phù hợp, 2.0 nếu phù hợp)
    """
    if not meal_type or meal_type == "all" or not recipe_meal_types:
        return 0.0
    
    meal_type_lower = meal_type.lower()
    
    # Mapping tên bữa ăn với meal_type names
    meal_mappings = {
        "breakfast": ["bữa sáng", "sáng", "breakfast", "morning"],
        "lunch": ["bữa trưa", "trưa", "lunch", "noon"],
        "dinner": ["bữa tối", "tối", "dinner", "evening"]
    }
    
    if meal_type_lower in meal_mappings:
        for recipe_meal in recipe_meal_types:
            recipe_meal_lower = recipe_meal.lower()
            if any(mapping in recipe_meal_lower for mapping in meal_mappings[meal_type_lower]):
                return 5.0  # Bonus điểm cho món ăn phù hợp bữa
    
    return 0.0

def calculate_recipe_score_with_matrices(recipe, user_profile, user_requirements, 
                                       ingredient_sim_matrix, tag_sim_matrix,
                                       ingredient_name_to_id, tag_name_to_id,
                                       all_ingredient_names, all_tag_names,
                                       all_ingredient_ids, all_tag_ids,
                                       similarity_matrix, recipes):
    """
    Tính điểm cho một recipe sử dụng similarity matrices
    
    Args:
        recipe (dict): Recipe cần tính điểm
        user_profile (dict): User profile
        user_requirements (dict): User requirements
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        similarity_matrix (np.ndarray): Recipe similarity matrix
        recipes (list): Danh sách tất cả recipes
    
    Returns:
        float: Điểm của recipe
    """
    score = 0.0
    recipe_ingredients = [ing["ingredient_id"] for ing in recipe.get("ingredients", [])]
    recipe_tags = [tag["tag_id"] for tag in recipe.get("tags", [])]
    
    # 1. Tính điểm similarity cho nguyên liệu
    if ingredient_sim_matrix is not None and all_ingredient_names is not None:
        # Điểm cho nguyên liệu yêu thích
        ing_score = get_ingredient_similarity_score(
            recipe.get("ingredients", []), 
            user_profile.get("favoriteIngredientIds", []), 
            ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids
        )
        
        # Điểm cho nguyên liệu không thích (trừ điểm)
        ing_score += get_ingredient_similarity_score(
            recipe.get("ingredients", []), 
            user_profile.get("notFavoriteIngredientIds", []), 
            ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids, 
            is_positive=False
        )
        
        score += ing_score
    
    # 2. Tính điểm similarity cho tags
    if tag_sim_matrix is not None and all_tag_names is not None:
        tag_score = get_tag_similarity_score(
            recipe.get("tags", []), 
            user_profile.get("includeTags", []), 
            tag_sim_matrix, tag_name_to_id, all_tag_names, all_tag_ids
        )
        tag_score += get_tag_similarity_score(
            recipe.get("tags", []), 
            user_profile.get("excludeTags", []), 
            tag_sim_matrix, tag_name_to_id, all_tag_names, all_tag_ids, 
            is_positive=False
        )
        score += tag_score
    
    # 3. Tính điểm cho nguyên liệu có sẵn
    if ingredient_sim_matrix is not None and all_ingredient_names is not None:
        available_ing_score = get_ingredient_availability_score(
            recipe.get("ingredients", []), 
            user_requirements.get("availableIngredientIds", []),
            ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids
        )
        score += available_ing_score
    
    # 4. Tính điểm cho nguyên liệu được khuyến nghị
    if ingredient_sim_matrix is not None and all_ingredient_names is not None:
        diet_pathology_score = get_diet_pathology_score(
            recipe.get("ingredients", []), 
            user_profile.get("suggestedDietModeIngredientIds", []),
            ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids
        )
        diet_pathology_score += get_diet_pathology_score(
            recipe.get("ingredients", []), 
            user_profile.get("suggestedPathologyIngredientIds", []),
            ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids
        )
        score += diet_pathology_score
    
    # 5. Điểm bonus cho meal_type phù hợp
    meal_type = user_requirements.get("mealType")
    meal_bonus = get_meal_type_bonus_score(recipe.get("meal_type", []), meal_type)
    score += meal_bonus
    
    
    # 6. Điểm tương tự với các món yêu thích/không thích
    recipe_idx = None
    for i, r in enumerate(recipes):
        if str(r.get("id", "")) == str(recipe.get("id", "")):
            recipe_idx = i
            break
    
    if recipe_idx is not None:
        # Điểm cho món yêu thích
        for fav_id in user_profile.get("favoriteRecipeIds", []):
            fav_indices = [j for j, r in enumerate(recipes) if str(r.get("id", "")) == str(fav_id)]
            if fav_indices:
                fav_idx = fav_indices[0]
                sim_score = similarity_matrix[fav_idx][recipe_idx]
                score += sim_score
        
        # Điểm cho món không thích (trừ điểm)
        for not_fav_id in user_profile.get("notFavoriteRecipeIds", []):
            not_fav_indices = [j for j, r in enumerate(recipes) if str(r.get("id", "")) == str(not_fav_id)]
            if not_fav_indices:
                not_fav_idx = not_fav_indices[0]
                sim_score = similarity_matrix[not_fav_idx][recipe_idx]
                score -= sim_score
                
    
    return score

def calculate_recipe_score_fallback(recipe, user_profile, user_requirements, similarity_matrix, recipes):
    """
    Tính điểm fallback sử dụng phương pháp cũ (điểm cố định)
    
    Args:
        recipe (dict): Recipe cần tính điểm
        user_profile (dict): User profile
        user_requirements (dict): User requirements
        similarity_matrix (np.ndarray): Recipe similarity matrix
        recipes (list): Danh sách tất cả recipes
    
    Returns:
        float: Điểm của recipe
    """
    score = 0.0
    recipe_ingredients = [ing["ingredient_id"] for ing in recipe.get("ingredients", [])]
    recipe_tags = [tag["tag_id"] for tag in recipe.get("tags", [])]
    
    # Điểm cho nguyên liệu yêu thích/không thích
    for ing in user_profile.get("favoriteIngredientIds", []):
        if ing in recipe_ingredients:
            score += 1.0
    for ing in user_profile.get("notFavoriteIngredientIds", []):
        if ing in recipe_ingredients:
            score -= 1.0
    
    # Điểm cho tags
    for tag in user_profile.get("includeTags", []):
        if tag in recipe_tags:
            score += 0.5
    for tag in user_profile.get("excludeTags", []):
        if tag in recipe_tags:
            score -= 0.5
    
    # Điểm cho nguyên liệu có sẵn
    for ing in user_requirements.get("availableIngredientIds", []):
        if ing in recipe_ingredients:
            score += 2.0
    
    # Điểm cho nguyên liệu được khuyến nghị
    for ing in user_profile.get("suggestedDietModeIngredientIds", []):
        if ing in recipe_ingredients:
            score += 1.0
    for ing in user_profile.get("suggestedPathologyIngredientIds", []):
        if ing in recipe_ingredients:
            score += 1.0
    
    # Điểm bonus cho meal_type phù hợp
    meal_type = user_requirements.get("mealType")
    if meal_type and meal_type != "all":
        recipe_meal_types = recipe.get("meal_type", [])
        if recipe_meal_types:
            meal_type_lower = meal_type.lower()
            
            # Mapping tên bữa ăn với meal_type names
            meal_mappings = {
                "breakfast": ["bữa sáng", "sáng", "breakfast", "morning"],
                "lunch": ["bữa trưa", "trưa", "lunch", "noon"],
                "dinner": ["bữa tối", "tối", "dinner", "evening"]
            }
            
            if meal_type_lower in meal_mappings:
                for recipe_meal in recipe_meal_types:
                    recipe_meal_lower = recipe_meal.lower()
                    if any(mapping in recipe_meal_lower for mapping in meal_mappings[meal_type_lower]):
                        score += 2.0  # Bonus điểm cho món ăn phù hợp bữa
                        break
    
    # Điểm tương tự với các món yêu thích/không thích
    recipe_idx = None
    for i, r in enumerate(recipes):
        if str(r.get("id", "")) == str(recipe.get("id", "")):
            recipe_idx = i
            break
    
    if recipe_idx is not None:
        for fav_id in user_profile.get("favoriteRecipeIds", []):
            fav_indices = [j for j, r in enumerate(recipes) if r.get("id") == fav_id]
            if fav_indices:
                fav_idx = fav_indices[0]
                sim_score = similarity_matrix[fav_idx][recipe_idx]
                score += sim_score * 2.0
        
        for not_fav_id in user_profile.get("notFavoriteRecipeIds", []):
            not_fav_indices = [j for j, r in enumerate(recipes) if r.get("id") == not_fav_id]
            if not_fav_indices:
                not_fav_idx = not_fav_indices[0]
                sim_score = similarity_matrix[not_fav_idx][recipe_idx]
                score -= sim_score * 2.0
    
    return score
