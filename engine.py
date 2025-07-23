import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity

def load_recipes(file_path):
    """
    Load recipes from a JSON file and return as a DataFrame and list.
    
    Args:
        file_path (str): Path to the JSON file.
    
    Returns:
        tuple: (DataFrame of recipes, list of recipes)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    df = pd.DataFrame(recipes)
    return df, recipes

def extract_features(df, recipes):
    """
    Extract all non-numeric features (categorical, season, month, tag, ingredient).
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        recipes (list): List of recipe dictionaries.
    
    Returns:
        tuple: (feature matrix, meal_type MLB, season MLB, month MLB, ingredient name to index, tag name to index, ingredient name to id)
    """
    # Categorical features
    multi_label_col = "meal_type"
    single_label_cols = ["region", "difficulty", "diet_type"]
    
    mlb_meal = MultiLabelBinarizer()
    meal_type_features = mlb_meal.fit_transform(df[multi_label_col].apply(lambda x: x if isinstance(x, list) else [x]))
    
    onehot = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    df_single_label = df[single_label_cols].fillna("unknown")
    single_label_features = onehot.fit_transform(df_single_label)
    
    categorical_features = np.hstack([meal_type_features, single_label_features])
    
    # Season features
    mlb_season = MultiLabelBinarizer(classes=range(0, 4))
    season_features = mlb_season.fit_transform(df["preferred_season"].apply(lambda x: x or []))
    
    # Month features
    mlb_month = MultiLabelBinarizer(classes=range(1, 13))
    month_features = mlb_month.fit_transform(df["preferred_months"].apply(lambda x: x or []))
    
    # Tag features
    all_tags = [tag["name"] for recipe in recipes for tag in recipe.get("tags", [])]
    unique_tags = sorted(list(set(all_tags)))
    tag_name_to_idx = {tag: i for i, tag in enumerate(unique_tags)}
    
    def extract_tag_vector(recipe):
        vec = np.zeros(len(unique_tags))
        for tag in recipe.get("tags", []):
            tag_name = tag["name"]
            if tag_name in tag_name_to_idx:
                vec[tag_name_to_idx[tag_name]] = 1
        return vec
    
    tag_features = np.array([extract_tag_vector(r) for r in recipes])
    
    # Ingredient features
    all_ingredients = [ing["name"] for recipe in recipes for ing in recipe.get("ingredients", [])]
    unique_ingredients = sorted(list(set(all_ingredients)))
    ing_name_to_idx = {ing: i for i, ing in enumerate(unique_ingredients)}
    
    ing_name_to_ing_id = {}
    for recipe in recipes:
        for ing in recipe.get("ingredients", []):
            ing_name = ing["name"]
            ing_id = ing["ingredient_id"]
            if ing_name not in ing_name_to_ing_id:
                ing_name_to_ing_id[ing_name] = ing_id

    def extract_ingredient_vector(recipe):
        vec = np.zeros(len(unique_ingredients))
        for ing in recipe.get("ingredients", []):
            name = ing["name"]
            if name in ing_name_to_idx:
                vec[ing_name_to_idx[name]] = 1
        return vec
    
    ingredient_features = np.array([extract_ingredient_vector(r) for r in recipes])
    
    # Combine all features
    X = np.concatenate([
        categorical_features,
        month_features,
        tag_features,
        ingredient_features
    ], axis=1)
    
    return X, mlb_meal, mlb_season, mlb_month, ing_name_to_idx, tag_name_to_idx, ing_name_to_ing_id

def calculate_similarity_matrix(X):
    """
    Calculate cosine similarity matrix for the feature matrix.
    
    Args:
        X (np.ndarray): Feature matrix.
    
    Returns:
        np.ndarray: Cosine similarity matrix.
    """
    return cosine_similarity(X)

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
    Check if a recipe meets user profile and requirements, excluding meal type.
    
    Args:
        recipe (dict): Recipe dictionary.
        user_profile (dict): User profile data.
        user_requirements (dict): User requirements.
    
    Returns:
        bool: True if recipe meets all requirements, False otherwise.
    """
    cooking_time_limit = user_requirements.get("cookingTime")
    if cooking_time_limit is not None and recipe.get("cooking_time", 9999) > cooking_time_limit:
        return False
    budget_limit = min(user_profile.get("budget", float("inf")),
                       user_requirements.get("budget", float("inf")))
    if recipe.get("cost", float("inf")) > budget_limit:
        return False
    if recipe.get("id") in user_profile.get("notFavoriteRecipeIds", []):
        return False
    if recipe.get("id") in user_profile.get("cookedRecipeIds", []):
        return False
    if recipe.get("id") in user_profile.get("feedbackRecipeIds", {}).keys():
        return False
    recipe_ingredients = [ing["ingredient_id"] for ing in recipe.get("ingredients", [])]
    for bad_ing in (
        user_profile.get("allergyIngredientIds", []) +
        user_profile.get("notSuggestedPathologyIngredientIds", []) +
        user_profile.get("notSuggestedDietModeIngredientIds", [])
    ):
        if bad_ing in recipe_ingredients:
            return False
    return True

def recommend_top_k_from_profile_and_requirements(
    recipes,
    similarity_matrix,
    user_profile,
    user_requirements,
    ingredient_name_to_id,
    tag_name_to_id,
    k=5,
    prefer_available_ingredients=True
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
        k (int): Number of recommendations to return.
    
    Returns:
        tuple: (list of recommended recipes, list of corresponding scores)
    """
    scored_recipes = []
    for i, recipe in enumerate(recipes):
        if not recipe_matches_requirements(recipe, user_profile, user_requirements):
            continue
        score = 0
        recipe_ingredients = [ing["ingredient_id"] for ing in recipe.get("ingredients", [])]
        recipe_tags = [tag["tag_id"] for tag in recipe.get("tags", [])]
        for ing in user_profile.get("favoriteIngredientIds", []):
            if ing in recipe_ingredients:
                score += 1
        if prefer_available_ingredients:
            for ing in user_requirements.get("availableIngredientIds", []):
                if ing in recipe_ingredients:
                    score += 2
        for ing in user_profile.get("notFavoriteIngredientIds", []):
            if ing in recipe_ingredients:
                score -= 1
        for ing in user_profile.get("suggestedDietModeIngredientIds", []):
            if ing in recipe_ingredients:
                score += 1
        for ing in user_profile.get("suggestedPathologyIngredientIds", []):
            if ing in recipe_ingredients:
                score += 1
        for tag in user_profile.get("tags", []):
            if tag in recipe_tags:
                score += 0.5
        if similarity_matrix is not None:
            max_sim = 0
            for fav_id in user_profile.get("favoriteRecipeIds", []):
                fav_indices = [j for j, r in enumerate(recipes) if r.get("id") == fav_id]
                if fav_indices:
                    fav_idx = fav_indices[0]
                    max_sim = max(max_sim, similarity_matrix[fav_idx][i])
            score += max_sim * 2
            max_sim = 0
            for not_fav_id in user_profile.get("notFavoriteRecipeIds", []):
                not_fav_indices = [j for j, r in enumerate(recipes) if r.get("id") == not_fav_id]
                if not_fav_indices:
                    not_fav_idx = not_fav_indices[0]
                    max_sim = max(max_sim, similarity_matrix[not_fav_idx][i])
            score -= max_sim * 2
        scored_recipes.append((recipe, score))
    top_k = sorted(scored_recipes, key=lambda x: -x[1])[:k]
    return [r[0] for r in top_k], [r[1] for r in top_k]

def main():
    # Step 1: Load data
    file_path = "recipes_with_ingredients_and_tags.json"
    df, recipes = load_recipes(file_path)
    
    # Step 2: Extract all features
    X, mlb_meal, mlb_season, mlb_month, ing_name_to_idx, tag_name_to_idx = extract_features(df, recipes)
    
    print("Tổng số chiều của vector:", X.shape[1])
    print("Vector của món ăn đầu tiên:", X[0])
    
    # Step 3: Calculate similarity matrix
    similarity_matrix = calculate_similarity_matrix(X)
    
    print("Shape:", similarity_matrix.shape)
    print("Tương đồng giữa món 0 và món 1:", similarity_matrix[0, 8])
    print(recipes[0]["name"])
    
    # Step 4: Get top k similar recipes
    top_similar = get_top_k_similar(similarity_matrix, 0, k=5)
    for idx, score in top_similar:
        print(f"Món {idx} (score: {score:.3f}) - {recipes[idx]['name']}")
    
    # Step 5: Define user profile and requirements
    user_profile = {
        "familyId": "ef9e28ec-dfee-4833-a7dc-3c266d1eaba7",
        "favoriteIngredientIds": [],
        "notFavoriteIngredientIds": [
            "626872c1-78b1-4812-8425-8b3c7eb4e9c1",
            "b335783f-ff51-454f-9c9f-a4e364c5e36d"
        ],
        "allergyIngredientIds": [],
        "suggestedDietModeIngredientIds": [],
        "suggestedPathologyIngredientIds": [],
        "notSuggestedDietModeIngredientIds": [],
        "notSuggestedPathologyIngredientIds": [],
        "budget": 80000,
        "includeTags": [],
        "excludeTags": [],
        "favoriteRecipeIds": [
            "46fcd56f-c006-496f-a5a0-640632790f36",
            "e2513792-53d7-448c-84ee-a226bc5239e4",
            "32ad1d1e-948e-4535-8605-07d902686049"
        ],
        "notFavoriteRecipeIds": [
            "8eaa175f-9ed4-424f-803b-6f7caab4db9a",
            "7ccb3ec0-c188-4c28-9003-a3a87f716e88"
        ],
        "cookedRecipeIds": [
            "5854195e-4160-4b88-a0b5-cf4da208d906",
            "acaa90b3-27d5-4424-9f2a-c994765e7779"
        ],
        "feedbackRecipeIds": {
            "eab7559d-e97b-4e85-847c-d32322558641": 1,
            "a866d36a-2a9a-44eb-a2f6-5292158c2594": 3,
            "34a7d194-d00d-4af8-b4f3-28df492e471e": 0
        }
    }
    
    user_requirements = {
        "mealType": "dinner",
        "cookingTime": 15,
        "budget": 80000,
        "availableIngredientIds": ["228e29a9-3d66-4f2d-8372-1d07043d62f2"]
    }
    
    # Step 6: Recommend top k recipes
    top5, top5_scores = recommend_top_k_from_profile_and_requirements(
        recipes=recipes,
        similarity_matrix=similarity_matrix,
        user_profile=user_profile,
        user_requirements=user_requirements,
        ingredient_name_to_id=ing_name_to_idx,
        tag_name_to_id=tag_name_to_idx,
        k=5,
        prefer_available_ingredients=True
    )
    
    # Print results
    for r, score in zip(top5, top5_scores):
        print(f"{r['name']} - {r.get('id')} with score {score}")

if __name__ == "__main__":
    main()