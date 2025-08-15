import json
import pandas as pd
import os
import pickle

def load_data(file_path):
    """
    Load data from a JSON file and return as a DataFrame and list.
    
    Args:
        file_path (str): Path to the JSON file.
    
    Returns:
        tuple: (DataFrame of data, list of data)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    return df, data

def save_similarity_matrix(similarity_matrix, file_path):
    """
    Lưu similarity matrix vào file để tái sử dụng
    
    Args:
        similarity_matrix (np.ndarray): Matrix cần lưu
        file_path (str): Đường dẫn file để lưu
    """
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(similarity_matrix, f)
        print(f"Đã lưu similarity matrix vào {file_path}")
    except Exception as e:
        print(f"Lỗi khi lưu similarity matrix: {e}")

def load_similarity_matrix(file_path):
    """
    Tải similarity matrix từ file
    
    Args:
        file_path (str): Đường dẫn file cần tải
    
    Returns:
        np.ndarray or None: Similarity matrix nếu tải thành công, None nếu thất bại
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                similarity_matrix = pickle.load(f)
            print(f"Đã tải similarity matrix từ {file_path}")
            return similarity_matrix
        else:
            print(f"File {file_path} không tồn tại")
            return None
    except Exception as e:
        print(f"Lỗi khi tải similarity matrix: {e}")
        return None

def create_recipe_mapping(recipes):
    """
    Tạo mapping cho recipe name to id
    """
    rec_name_to_rec_id = {}
    for recipe in recipes:
        rec_name = recipe["name"]
        rec_id = recipe["id"]
        if rec_name not in rec_name_to_rec_id:
            rec_name_to_rec_id[rec_name] = rec_id
    return rec_name_to_rec_id

def create_ingredient_mapping(ingredients):
    """
    Tạo mapping cho ingredient name to id
    """
    ing_name_to_ing_id = {}
    for ingredient in ingredients:
        ing_name = ingredient["name"]
        ing_id = ingredient["ingredient_id"]
        if ing_name not in ing_name_to_ing_id:
            ing_name_to_ing_id[ing_name] = ing_id
    return ing_name_to_ing_id

def create_tag_mapping(tags):
    """
    Tạo mapping cho tag name to id
    """
    tag_name_to_tag_id = {}
    for tag in tags:
        tag_name = tag["name"]
        tag_id = tag["tag_id"]
        if tag_name not in tag_name_to_tag_id:
            tag_name_to_tag_id[tag_name] = tag_id
    return tag_name_to_tag_id
