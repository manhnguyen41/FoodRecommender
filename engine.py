import warnings
from embeddings import load_phobert_model
from utils import load_data
from similarity import (
    create_recipe_similarity_matrix,
    create_ingredient_similarity_matrix,
    create_tag_similarity_matrix
)
from recommendation import get_top_k_similar, recommend_top_k_from_profile_and_requirements

warnings.filterwarnings('ignore')

def main():
    # Step 1: Load PhoBERT model
    print("Đang load PhoBERT model...")
    model, tokenizer = load_phobert_model()
    print("Đã load xong PhoBERT model!")
    
    # Step 2: Load data
    df, recipes = load_data("data/recipes.json")
    print(f"Đã load {len(recipes)} món ăn")
    
    # Step 3: Create recipe similarity matrix
    recipe_similarity_matrix, rec_name_to_rec_id = create_recipe_similarity_matrix(df, recipes, model, tokenizer)
    
    print("Shape similarity matrix:", recipe_similarity_matrix.shape)
    print("Tương đồng giữa món 0 và món 8:", recipe_similarity_matrix[0, 8])
    print("Tên món 0:", recipes[0]["name"])
    print("Tên món 8:", recipes[8]["name"])
    
    # Step 4: Get top k similar recipes
    top_similar = get_top_k_similar(recipe_similarity_matrix, 0, k=10)
    print("\nTop 5 món tương tự với món đầu tiên:")
    for idx, score in top_similar:
        print(f"Món {idx} (score: {score:.3f}) - {recipes[idx]['name']}")
    
    # Step 6: Define user profile and requirements
    user_profile = {
        "familyId": "ef9e28ec-dfee-4833-a7dc-3c266d1eaba7",
        "favoriteIngredientIds": [
            "228e29a9-3d66-4f2d-8372-1d07043d62f2"
        ],
        "notFavoriteIngredientIds": [
            "c89dba74-e63b-411f-b5d5-22fea4063c9b"
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
            "84c4e617-ac8c-4a5b-977d-530e3b6e7823"
        ],
        "notFavoriteRecipeIds": [
        ],
        "cookedRecipeIds": [
        ],
        "feedbackRecipeIds": {
        }
    }
    
    user_requirements = {
        "cookingTime": 120,
        "budget": 80000,
        "availableIngredientIds": []
    }
    
    # Step 7: Recommend top k recipes
    print("\nĐang tạo gợi ý món ăn...")

    # Load ingredients và tags data
    _, ingredients = load_data("data/ingredients.json")
    _, tags = load_data("data/tags.json")
    
    ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids = create_ingredient_similarity_matrix(ingredients, model, tokenizer)
    tag_sim_matrix, tag_name_to_id, all_tag_names, all_tag_ids = create_tag_similarity_matrix(tags, model, tokenizer)

    # In thông tin về ingredient similarity matrix
    print("\n" + "="*50)
    print("INGREDIENT SIMILARITY MATRIX INFO")
    print("="*50)
    print("Shape ingredient similarity matrix:", ingredient_sim_matrix.shape)
    print("Tương đồng giữa nguyên liệu 0 và nguyên liệu 5:", ingredient_sim_matrix[0, 5])
    print("Tên nguyên liệu 0:", all_ingredient_names[741])
    print("Tên nguyên liệu 5:", all_ingredient_names[5])
    
    # In top 5 nguyên liệu tương tự với nguyên liệu đầu tiên
    print("\nTop 5 nguyên liệu tương tự với nguyên liệu đầu tiên:")
    top_similar = get_top_k_similar(ingredient_sim_matrix, 741, k=10)
    for idx, score in top_similar:
        print(f"Nguyên liệu {idx} (score: {score:.3f}) - {all_ingredient_names[idx]}")
    
    # In thông tin về tag similarity matrix
    print("\n" + "="*50)
    print("TAG SIMILARITY MATRIX INFO")
    print("="*50)
    print("Shape tag similarity matrix:", tag_sim_matrix.shape)
    print("Tương đồng giữa tag 0 và tag 3:", tag_sim_matrix[0, 3])
    print("Tên tag 0:", all_tag_names[0])
    print("Tên tag 3:", all_tag_names[3])
    
    # In top 5 tags tương tự với tag đầu tiên
    print("\nTop 5 tags tương tự với tag đầu tiên:")
    top_similar = get_top_k_similar(tag_sim_matrix, 0, k=10)
    for idx, score in top_similar:
        print(f"Tag {idx} (score: {score:.3f}) - {all_tag_names[idx]}")

    top5, top5_scores = recommend_top_k_from_profile_and_requirements(
        recipes=recipes,
        similarity_matrix=recipe_similarity_matrix,
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
        k=20
    )
    
    # Print results
    print("\nTop 5 món ăn được gợi ý:")
    for r, score in zip(top5, top5_scores):
        print(f"{r['name']} - {r.get('id')} với score {score:.4f}")

if __name__ == "__main__":
    main()