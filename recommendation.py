from scoring import calculate_recipe_score_with_matrices, calculate_recipe_score_fallback
import random

def get_top_k_similar(similarity_matrix, recipe_idx, k=20):
    """
    Get the top k most similar recipes to a given recipe index.
    
    Args:
        similarity_matrix (np.ndarray): Cosine similarity matrix.
        recipe_idx (int): Index of the target recipe.
        k (int): Number of similar recipes to return.
    
    Returns:
        list: List of tuples (index, similarity_score) for top k similar recipes.
    """
    sim_scores = similarity_matrix[recipe_idx]
    similar_indices = sim_scores.argsort()[::-1][1:k+1]
    return [(i, sim_scores[i]) for i in similar_indices]

def recipe_matches_requirements(recipe, user_profile, user_requirements):
    """
    Check if a recipe meets user profile and requirements, including meal type filtering.
    
    Args:
        recipe (dict): Recipe dictionary.
        user_profile (dict): User profile data.
        user_requirements (dict): User requirements.
    
    Returns:
        bool: True if recipe meets all requirements, False otherwise.
    """
    # Kiểm tra món đã nấu
    if recipe.get("id") in user_profile.get("cookedRecipeIds", []):
        return False
    
    # Kiểm tra nguyên liệu dị ứng
    recipe_ingredients = [ing["ingredient_id"] for ing in recipe.get("ingredients", [])]
    for bad_ing in (
        user_profile.get("allergyIngredientIds", []) +
        user_profile.get("notSuggestedPathologyIngredientIds", []) +
        user_profile.get("notSuggestedDietModeIngredientIds", [])
    ):
        if bad_ing in recipe_ingredients:
            return False
    # Kiểm tra meal_type của recipe nếu có yêu cầu cụ thể
    meal_type = user_requirements.get("mealType")
    if meal_type and meal_type != "all":
        recipe_meal_types = recipe.get("meal_type", [])
        if not recipe_meal_types:
            return False
        
        # Kiểm tra xem recipe có meal_type phù hợp không
        recipe_has_meal_type = False
        for recipe_meal in recipe_meal_types:
            if recipe_meal.lower() == meal_type.lower():
                recipe_has_meal_type = True
                break
        
        # Nếu không có meal_type phù hợp, loại bỏ recipe
        if not recipe_has_meal_type:
            return False

        # Kiểm tra recipe_type của recipe nếu có yêu cầu cụ thể
    recipe_type_req = user_requirements.get("recipeType")
    if recipe_type_req:
        recipe_types = recipe.get("recipe_type", [])
        if recipe_type_req and not recipe_types:
            return False
        
        # Đồng bộ chữ thường để so khớp linh hoạt
        recipe_types_lower = [str(t).lower() for t in recipe_types]
        
        flag = False
        for r in recipe_types_lower:
            if r in recipe_type_req:
                flag = True
                break
        if not flag:
            return False
    
    # Kiểm tra độ khó của recipe nếu có yêu cầu cụ thể
    difficulty_req = user_requirements.get("difficulty")
    if difficulty_req is not None:
        recipe_difficulty = recipe.get("difficulty", "1")  # Mặc định là 1 nếu không có
        # Chuyển đổi sang int để so sánh
        try:
            recipe_diff_int = int(recipe_difficulty)
            difficulty_req_int = int(difficulty_req)
            if recipe_diff_int > difficulty_req_int:
                return False
        except (ValueError, TypeError):
            # Nếu không thể chuyển đổi, bỏ qua kiểm tra này
            pass
    
    # Kiểm tra cách chế biến của recipe nếu có yêu cầu loại trừ
    exclude_methods = user_requirements.get("excludeMethod")
    if exclude_methods:
        recipe_methods = recipe.get("method", [])
        if recipe_methods:
            # Nếu recipe có bất kỳ cách chế biến nào trong danh sách loại trừ thì bỏ qua
            for method in recipe_methods:
                if method in exclude_methods:
                    return False
    
    return True

def recommend_top_k_from_profile_and_requirements(
    recipes,
    similarity_matrix,
    user_profile,
    user_requirements,
    ingredient_name_to_id,
    tag_name_to_id,
    ingredient_sim_matrix=None,
    tag_sim_matrix=None,
    all_ingredient_names=None,
    all_tag_names=None,
    all_ingredient_ids=None,
    all_tag_ids=None,
    k=5
):
    """
    Recommend top k recipes based on user profile and requirements.
    
    Args:
        recipes (list): List of recipe dictionaries.
        similarity_matrix (np.ndarray): Cosine similarity matrix.
        user_profile (dict): User profile data.
        user_requirements (dict): User requirements.
        ingredient_name_to_id (dict): Mapping of ingredient names to indices.
        tag_name_to_id (dict): Mapping of tag names to indices.
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix.
        tag_sim_matrix (np.ndarray): Tag similarity matrix.
        all_ingredient_names (list): List of all ingredient names.
        all_tag_names (list): List of all tag names.
        k (int): Number of recommendations to return.
    
    Returns:
        tuple: (list of recommended recipes, list of corresponding scores)
    """
    scored_recipes = []
    
    for recipe in recipes:
        if not recipe_matches_requirements(recipe, user_profile, user_requirements):
            continue
        
        if (ingredient_sim_matrix is not None and tag_sim_matrix is not None and 
            all_ingredient_names is not None and all_tag_names is not None):
            score = calculate_recipe_score_with_matrices(
                recipe, user_profile, user_requirements,
                ingredient_sim_matrix, tag_sim_matrix,
                ingredient_name_to_id, tag_name_to_id,
                all_ingredient_names, all_tag_names,
                all_ingredient_ids, all_tag_ids,
                similarity_matrix, recipes
            )
        else:
            score = calculate_recipe_score_fallback(
                recipe, user_profile, user_requirements,
                similarity_matrix, recipes
            )
        
        scored_recipes.append((recipe, score))
    
    # Sắp xếp theo điểm và lấy top k
    # Nếu tất cả điểm bằng nhau, random để tạo đa dạng
    if len(scored_recipes) > 0:
        all_scores = [score for _, score in scored_recipes]
        if len(set(all_scores)) == 1:  # Tất cả điểm bằng nhau
            random.shuffle(scored_recipes)
    
    top_k = sorted(scored_recipes, key=lambda x: -x[1])[:k]
    return [r[0] for r in top_k], [r[1] for r in top_k]
