#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xóa cache files khi cần thiết
"""

import os

def clear_cache():
    """Xóa tất cả cache files"""
    cache_files = [
        "similarity_matrix.pkl",
        "feature_matrix.pkl",
        "ingredient_similarity_matrix.pkl",
        "tag_similarity_matrix.pkl"
    ]
    
    print("Đang xóa cache files...")
    
    for file_name in cache_files:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"Đã xóa: {file_name}")
            except Exception as e:
                print(f"Lỗi khi xóa {file_name}: {e}")
        else:
            print(f"File không tồn tại: {file_name}")
    
    print("Hoàn thành xóa cache!")

if __name__ == "__main__":
    clear_cache()
