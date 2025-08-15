import psycopg2
import json
import decimal
from collections import defaultdict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
# Kết nối database
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()
# ====== 1. Lấy thông tin món ăn ======
cur.execute("""
    SELECT 
        fr.id, 
        fr.name, 
        fr.description, 
        fr.images, 
        fr.video_urls, 
        fr.cost, 
        fr.cooking_time, 
        fr.difficulty, 
        fr.average_rating, 
        fr.total_reviews, 
        fr.view_count,
        fr.preping_time
    FROM public.food_recipe fr
""")
recipes_raw = cur.fetchall()
recipe_cols = [desc[0] for desc in cur.description]
# ====== 2. Lấy nguyên liệu ======
cur.execute("""
    SELECT 
        fri.recipe_id,
        fi.id AS ingredient_id,
        fi.name
    FROM public.food_recipe_ingredient fri
    JOIN public.food_ingredient fi ON fri.ingredient_id::uuid = fi.id
""")
ingredients_raw = cur.fetchall()
ingredient_cols = [desc[0] for desc in cur.description]
# ====== 3. Lấy tag ======
cur.execute("""
    SELECT 
        frt.recipe_id,
        ft.id AS tag_id,
        ft.name,
        ft.group
    FROM public.food_recipe_tag frt
    JOIN public.food_tag ft ON frt.tag_id::uuid = ft.id
    WHERE frt.tag_id IS NOT NULL AND frt.tag_id <> ''
""")
tags_raw = cur.fetchall()
tag_cols = [desc[0] for desc in cur.description]
# ====== Xử lý dữ liệu ======
# Cấu trúc dữ liệu mới:
# - method: Danh sách cách chế biến (từ tag group 7)
# - recipe_type: Danh sách loại món ăn (từ tag group 9)  
# - meal_type: Danh sách loại bữa (từ tag group 10)
# Tổ chức nguyên liệu theo recipe_id
ingredient_map = defaultdict(list)
for row in ingredients_raw:
    row_dict = dict(zip(ingredient_cols, row))
    recipe_id = row_dict.pop("recipe_id")
    ingredient_map[recipe_id].append(row_dict)
# Tổ chức tags theo recipe_id
tag_map = defaultdict(list)
for row in tags_raw:
    row_dict = dict(zip(tag_cols, row))
    recipe_id = row_dict.pop("recipe_id")
    tag_map[recipe_id].append(row_dict)
# Gộp vào từng món ăn
recipes = []
for row in recipes_raw:
    recipe = dict(zip(recipe_cols, row))
    recipe_id = recipe["id"]
    recipe["ingredients"] = ingredient_map.get(recipe_id, [])
    recipe["tags"] = tag_map.get(recipe_id, [])
    
    # Thêm thông tin từ tag groups
    # Group 7: Cách chế biến (method) - VD: rán, luộc, nướng
    # Group 9: Loại món ăn (recipe_type) - VD: món chính, món phụ
    # Group 10: Loại bữa (meal_type) - VD: bữa sáng, bữa trưa, bữa tối
    recipe["method"] = []
    recipe["recipe_type"] = []
    recipe["meal_type"] = []
    
    # Kiểm tra và thêm thông tin từ tags
    for tag in recipe["tags"]:
        group = tag.get("group")
        if 7 in group:  # Method
            recipe["method"].append(tag["name"])
        elif 9 in group:  # Recipe type
            recipe["recipe_type"].append(tag["name"])
        elif 10 in group:  # Meal type
            recipe["meal_type"].append(tag["name"])
    
    recipes.append(recipe)
# ====== Xuất JSON ======
with open("data/recipes.json", "w", encoding="utf-8") as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2, default=decimal_default)

# ====== 4. Lấy nguyên liệu ======
cur.execute("""
    SELECT 
        fi.id AS ingredient_id,
        fi.name,
        fi.cost,
        fi.allergen_flag,
        fi.category
    FROM public.food_ingredient fi
""")
ingredients_raw = cur.fetchall()
ingredient_cols = [desc[0] for desc in cur.description]

# Lưu danh sách nguyên liệu vào file JSON
ingredients = []
for row in ingredients_raw:
    ingredient = dict(zip(ingredient_cols, row))
    ingredients.append(ingredient)

with open("data/ingredients.json", "w", encoding="utf-8") as f:
    json.dump(ingredients, f, ensure_ascii=False, indent=2, default=decimal_default)

# ====== 5. Lấy tag ======
cur.execute("""
    SELECT 
        ft.id AS tag_id,
        ft.name,
        ft.description,
        ft.type,
        ft.group
    FROM public.food_tag ft
""")
tags_raw = cur.fetchall()
tag_cols = [desc[0] for desc in cur.description]

# Lưu danh sách tag vào file JSON
tags = []
for row in tags_raw:
    tag = dict(zip(tag_cols, row))
    tags.append(tag)

with open("data/tags.json", "w", encoding="utf-8") as f:
    json.dump(tags, f, ensure_ascii=False, indent=2, default=decimal_default)

cur.close()
conn.close()