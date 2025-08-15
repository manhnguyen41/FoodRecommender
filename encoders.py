import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

def create_ingredient_onehot_encoder(ingredients):
    """
    Tạo one-hot encoder cho nguyên liệu
    """
    ingredient_names = [ing["name"] for ing in ingredients]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoder.fit(np.array(ingredient_names).reshape(-1, 1))
    return encoder

def create_tag_onehot_encoder(tags):
    """
    Tạo one-hot encoder cho tags
    """
    tag_names = [tag["name"] for tag in tags]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoder.fit(np.array(tag_names).reshape(-1, 1))
    return encoder

def get_ingredients_onehot(ingredients, encoder):
    """
    Lấy one-hot vector cho nguyên liệu
    """
    if not ingredients:
        return np.zeros(len(encoder.get_feature_names_out()))
    
    ingredient_names = [ing["name"] for ing in ingredients]
    onehot = encoder.transform(np.array(ingredient_names).reshape(-1, 1))
    # Tổng hợp tất cả one-hot vectors (OR operation)
    return np.max(onehot, axis=0)

def get_tags_onehot(tags, encoder):
    """
    Lấy one-hot vector cho tags
    """
    if not tags:
        return np.zeros(len(encoder.get_feature_names_out()))
    
    tag_names = [tag["name"] for tag in tags]
    onehot = encoder.transform(np.array(tag_names).reshape(-1, 1))
    # Tổng hợp tất cả one-hot vectors (OR operation)
    return np.max(onehot, axis=0)

def create_ingredient_tfidf_matrix(recipes):
    """
    Tạo TF-IDF matrix cho nguyên liệu
    """
    # Chuyển danh sách nguyên liệu thành chuỗi (cách nhau bởi dấu phẩy)
    corpus = []
    for recipe in recipes:
        ingredients = recipe.get("ingredients", [])
        ingredient_names = [ing["name"] for ing in ingredients]
        corpus.append(" ".join(ingredient_names))  # "Salt Sugar Butter"

    # Khởi tạo TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    tfidf_matrix = vectorizer.fit_transform(corpus)  # Kết quả là sparse matrix
    
    return tfidf_matrix, vectorizer
