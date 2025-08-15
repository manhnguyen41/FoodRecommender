import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embeddings import get_text_embedding
from encoders import create_ingredient_onehot_encoder, create_tag_onehot_encoder, get_ingredients_onehot, get_tags_onehot, create_ingredient_tfidf_matrix
from utils import load_data, save_similarity_matrix, load_similarity_matrix, create_recipe_mapping, create_ingredient_mapping, create_tag_mapping

def create_recipe_similarity_matrix(df, recipes, model, tokenizer, use_cache=True):
    """
    Extract features sử dụng one-hot encoding cho nguyên liệu và tags, PhoBERT cho tên món ăn.
    Hỗ trợ cache để tái sử dụng similarity matrix.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        recipes (list): List of recipe dictionaries.
        model: PhoBERT model.
        tokenizer: PhoBERT tokenizer.
        use_cache (bool): Có sử dụng cache hay không.
    
    Returns:
        tuple: (feature matrix, ingredient name to id)
    """
    # Kiểm tra cache trước
    if use_cache:
        cached_X = load_similarity_matrix("matrices/similarity_matrix.pkl")
        if cached_X is not None:
            print("Đã tải similarity matrix từ cache!")
            return cached_X, create_recipe_mapping(recipes)
    
    print("Đang tạo feature vectors với one-hot encoding cho nguyên liệu và tags...")
    
    # Tạo one-hot encoders cho nguyên liệu và tags
    # Cần load dữ liệu nguyên liệu và tags riêng biệt
    _, ingredients = load_data("data/ingredients.json")
    _, tags = load_data("data/tags.json")
    
    ingredient_encoder = create_ingredient_onehot_encoder(ingredients)
    tag_encoder = create_tag_onehot_encoder(tags)
    
    # Khởi tạo list để lưu feature vectors
    feature_vectors = []
    
    for i, recipe in enumerate(recipes):
        if i % 100 == 0:
            print(f"Đang xử lý món ăn {i}/{len(recipes)}")
        
        try:
            # 2. One-hot vector cho nguyên liệu
            tfidf_matrix, vectorizer = create_ingredient_tfidf_matrix(recipes)
            ingredient_embedding = tfidf_matrix[i].toarray().flatten()
            
            # 3. One-hot vector cho tags
            tag_embedding = get_tags_onehot(recipe.get("tags", []), tag_encoder)
            
            # 4. Các features số học
            numerical_features = np.array([
                recipe.get("cost", 0.0),
                recipe.get("cooking_time", 0),
                float(recipe.get("difficulty", "1")),
            ])

            ingredient_embedding = ingredient_embedding / np.linalg.norm(ingredient_embedding) if np.linalg.norm(ingredient_embedding) else ingredient_embedding
            ingredient_embedding = ingredient_embedding * 2
            tag_embedding = tag_embedding / np.linalg.norm(tag_embedding) if np.linalg.norm(tag_embedding) else tag_embedding
            tag_embedding = tag_embedding / 2
            numerical_features = numerical_features / np.linalg.norm(numerical_features) if np.linalg.norm(numerical_features) else numerical_features
            numerical_features = numerical_features / 2

            # 5. Kết hợp tất cả features
            recipe_vector = np.concatenate([
                ingredient_embedding,  # one-hot vector
                tag_embedding,         # one-hot vector
                numerical_features     # 3 chiều
            ])
            
            feature_vectors.append(recipe_vector)
            
        except Exception as e:
            print(f"Lỗi khi xử lý món ăn {i} '{recipe.get('name', 'Unknown')}': {e}")
            # Sử dụng vector 0 nếu có lỗi
            zero_vector = np.zeros(len(ingredient_embedding) + len(tag_embedding) + 3)
            feature_vectors.append(zero_vector)
    
    # Chuyển thành numpy array
    X = np.array(feature_vectors)

    X = cosine_similarity(X)
    
    # Lưu feature matrix vào cache nếu được yêu cầu
    if use_cache:
        save_similarity_matrix(X, "matrices/similarity_matrix.pkl")
    
    # Tạo mapping cho ingredient name to id (để sử dụng trong recommendation)
    rec_name_to_rec_id = create_recipe_mapping(recipes)
    
    print(f"Hoàn thành! Similarity matrix có shape: {X.shape}")
    
    return X, rec_name_to_rec_id

def create_ingredient_similarity_matrix(ingredients, model, tokenizer, use_cache=True):
    """
    Tạo similarity matrix cho nguyên liệu dựa trên PhoBERT embedding
    
    Args:
        ingredients (list): Danh sách ingredients
        model: PhoBERT model
        tokenizer: PhoBERT tokenizer
        use_cache (bool): Có sử dụng cache hay không
    
    Returns:
        tuple: (ingredient similarity matrix, ingredient name to id mapping, all_ingredient_names, all_ingredient_ids)
    """
    cache_file = "matrices/ingredient_similarity_matrix.pkl"
    
    # Kiểm tra cache trước
    if use_cache:
        cached_matrix = load_similarity_matrix(cache_file)
        if cached_matrix is not None:
            print("Đã tải ingredient similarity matrix từ cache!")
            ing_name_to_id = create_ingredient_mapping(ingredients)
            all_ingredients = [ingredient["name"] for ingredient in ingredients]
            all_ingredients_id = [ingredient["ingredient_id"] for ingredient in ingredients]
            return cached_matrix, ing_name_to_id, all_ingredients, all_ingredients_id
    
    print("Đang tạo ingredient similarity matrix...")
    
    # Sử dụng tất cả ingredients, không cần unique
    all_ingredients = [ingredient["name"] for ingredient in ingredients]
    all_ingredients_id = [ingredient["ingredient_id"] for ingredient in ingredients]

    print(f"Tổng số nguyên liệu: {len(all_ingredients)}")
    
    # Tạo embedding cho mỗi ingredient
    ingredient_embeddings = []
    for ing_name in all_ingredients:
        embedding = get_text_embedding(ing_name, model, tokenizer, max_length=64)
        ingredient_embeddings.append(embedding)
    
    # Chuyển thành matrix
    ingredient_matrix = np.array(ingredient_embeddings)
    
    # Tính similarity matrix
    ingredient_sim_matrix = cosine_similarity(ingredient_matrix)
    
    # Lưu vào cache
    if use_cache:
        save_similarity_matrix(ingredient_sim_matrix, cache_file)
        print("Đã lưu ingredient similarity matrix vào cache!")
    
    ing_name_to_id = create_ingredient_mapping(ingredients)
    return ingredient_sim_matrix, ing_name_to_id, all_ingredients, all_ingredients_id

def create_tag_similarity_matrix(tags, model, tokenizer, use_cache=True):
    """
    Tạo similarity matrix cho tags dựa trên PhoBERT embedding
    
    Args:
        tags (list): Danh sách tags
        model: PhoBERT model
        tokenizer: PhoBERT tokenizer
        use_cache (bool): Có sử dụng cache hay không
    
    Returns:
        tuple: (tag similarity matrix, tag name to id mapping, all_tag_names, all_tag_ids)
    """
    cache_file = "matrices/tag_similarity_matrix.pkl"
    
    # Kiểm tra cache trước
    if use_cache:
        cached_matrix = load_similarity_matrix(cache_file)
        if cached_matrix is not None:
            print("Đã tải tag similarity matrix từ cache!")
            # Tạo lại mapping và names để đảm bảo consistency
            tag_name_to_id = create_tag_mapping(tags)
            all_tags = [tag["name"] for tag in tags]
            all_tags_id = [tag["tag_id"] for tag in tags]
            return cached_matrix, tag_name_to_id, all_tags, all_tags_id
    
    print("Đang tạo tag similarity matrix...")
    
    # Sử dụng tất cả tags, không cần unique
    all_tags = [tag["name"] for tag in tags]
    all_tags_id = [tag["tag_id"] for tag in tags]
    print(f"Tổng số tags: {len(all_tags)}")
    
    # Tạo embedding cho mỗi tag
    tag_embeddings = []
    for tag_name in all_tags:
        embedding = get_text_embedding(tag_name, model, tokenizer, max_length=64)
        tag_embeddings.append(embedding)
    
    # Chuyển thành matrix
    tag_matrix = np.array(tag_embeddings)
    
    # Tính similarity matrix
    tag_sim_matrix = cosine_similarity(tag_matrix)
    
    # Lưu vào cache
    if use_cache:
        save_similarity_matrix(tag_sim_matrix, cache_file)
        print("Đã lưu tag similarity matrix vào cache!")
    
    tag_name_to_id = create_tag_mapping(tags)
    return tag_sim_matrix, tag_name_to_id, all_tags, all_tags_id

def get_recipe_similarity_matrix(model, tokenizer):
    df, recipes = load_data("data/recipes.json")
    X, rec_name_to_rec_id = create_recipe_similarity_matrix(df, recipes, model, tokenizer, use_cache=True)
    return X, rec_name_to_rec_id

def get_ingredient_similarity_matrix(model, tokenizer):
    df, ingredients = load_data("data/ingredients.json")
    X, ing_name_to_ing_id, all_ingredients = create_ingredient_similarity_matrix(ingredients, model, tokenizer, use_cache=True)
    return X, ing_name_to_ing_id, all_ingredients, all_ingredients_id

def get_tag_similarity_matrix(model, tokenizer):
    df, tags = load_data("data/tags.json")
    X, tag_name_to_tag_id, all_tags = create_tag_similarity_matrix(tags, model, tokenizer, use_cache=True)
    return X, tag_name_to_tag_id, all_tags, all_tags_id
