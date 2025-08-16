# 🍽️ Food Recommendation API

API gợi ý thực đơn hàng ngày và hàng tuần dựa trên sở thích người dùng.

## 🐳 Chạy với Docker

### 1. Build và chạy
```bash
docker-compose up --build
```

### 2. Dừng
```bash
docker-compose down
```

API sẽ chạy tại: **http://localhost:5000**

## 🧪 Test API

### 🚀 **Cách 1: Test bằng Postman (Khuyến nghị)**

#### 1. Import Postman Collection
- Mở Postman
- Click **Import** → Chọn file `Food_Recommendation_API.postman_collection.json`
- Collection sẽ được import với tên "Food Recommendation API"

#### 2. Thiết lập Environment Variables
- Tạo Environment mới trong Postman
- Thêm variable: `base_url` = `http://localhost:5000`
- Chọn Environment này để sử dụng

#### 3. Test các API endpoints

**Health Check:**
- Method: `GET`
- URL: `{{base_url}}/health`

**Daily Meal Plan:**
- Method: `POST`
- URL: `{{base_url}}/api/daily-meal`
- Body: JSON với các tham số cần thiết

**Weekly Meal Plan:**
- Method: `POST`
- URL: `{{base_url}}/api/weekly-meal`
- Body: JSON với các tham số cần thiết

**Replace Recipe:**
- Method: `POST`
- URL: `{{base_url}}/api/replace-recipe`
- Body: JSON với daily_plan và thông tin thay thế

**Get Data:**
- Method: `GET`
- URLs: 
  - `{{base_url}}/api/recipes`
  - `{{base_url}}/api/ingredients`
  - `{{base_url}}/api/tags`

## 📋 Các endpoint

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/reinit` | Khởi tạo lại hệ thống (dữ liệu + ma trận tương đồng) |
| POST | `/api/daily-meal` | Tạo thực đơn cho 1 ngày |
| POST | `/api/weekly-meal` | Tạo thực đơn cho 1 tuần |
| POST | `/api/replace-recipe` | Thay thế món ăn |

## 🎯 **Chi tiết Postman Collection**

### **Daily Meal Plan**
- **Method**: POST
- **URL**: `{{base_url}}/api/daily-meal`
- **Body**: 
  ```json
  {
    "favorite_ingredients": [],
    "not_favorite_ingredients": [],
    "allergy_ingredients": [],
    "favorite_recipes": [],
    "not_favorite_recipes": [],
    "diet_mode": "normal",
    "serving_size": 2,
    "date": ""
  }
  ```

### **Weekly Meal Plan**
- **Method**: POST
- **URL**: `{{base_url}}/api/weekly-meal`
- **Body**: 
  ```json
  {
    "favorite_ingredients": [],
    "not_favorite_ingredients": [],
    "allergy_ingredients": [],
    "favorite_recipes": [],
    "not_favorite_recipes": [],
    "diet_mode": "normal",
    "serving_size": 2,
    "start_date": ""
  }
  ```

### **Replace Recipe**
- **Method**: POST
- **URL**: `{{base_url}}/api/replace-recipe`
- **Body**: 
  ```json
  {
    "daily_plan": {
      "date": 0,
      "meals": [
        {
          "mealTypeId": "",
          "mapRecipe": {
            "món chính": [],
            "món phụ": [],
            "món canh": [],
            "món tráng miệng": []
          }
        }
      ]
    },
    "meal_type": "",
    "recipe_id": "",
    "replacement_reason": "",
    "favorite_ingredients": [],
    "not_favorite_ingredients": [],
    "allergy_ingredients": [],
    "favorite_recipes": [],
    "not_favorite_recipes": [],
    "diet_mode": "normal"
  }
  ```

## 🔧 Tham số đầu vào

### Daily/Weekly Meal
```json
{
  "favorite_ingredients": ["ingredient_id1", "ingredient_id2"],
  "not_favorite_ingredients": ["ingredient_id3"],
  "allergy_ingredients": ["ingredient_id4"],
  "favorite_recipes": ["recipe_id1"],
  "not_favorite_recipes": ["recipe_id2"],
  "diet_mode": "normal",
  "serving_size": 2,
  "difficulty": 1,
  "exclude_methods": ["rán", "nướng"]
}
```

### Replace Recipe
```json
{
  "daily_plan": {...},
  "meal_type": "bữa trưa",
  "recipe_id_to_replace": "recipe_id",
  "replacement_reason": "ingredients|difficulty|method"
}
```

## 📊 Định dạng đầu ra

### Daily/Weekly Meal
```json
{
  "date": 1755104400000,
  "meals": [
    {
      "mealTypeId": "bữa sáng",
      "mapRecipe": {
        "món chính": ["recipe_id1"],
        "món phụ": [],
        "món canh": [],
        "món tráng miệng": []
      }
    }
  ]
}
```