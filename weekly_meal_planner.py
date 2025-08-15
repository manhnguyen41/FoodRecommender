import numpy as np
from daily_meal_planner import suggest_daily_meals, get_default_user_profile, get_default_user_requirements
from recommendation import recommend_top_k_from_profile_and_requirements


def generate_weekly_meal_plan(
    recipes,
    similarity_matrix,
    user_profile,
    user_requirements,
    ingredient_name_to_id,
    tag_name_to_id,
    ingredient_sim_matrix,
    tag_sim_matrix,
    all_ingredient_names,
    all_tag_names,
    all_ingredient_ids,
    all_tag_ids,
    serving_size=2
):
    """
    Generate thực đơn cho 1 tuần (7 ngày)
    
    Args:
        recipes (list): Danh sách tất cả recipes
        similarity_matrix (np.ndarray): Recipe similarity matrix
        user_profile (dict): User profile (sẽ được cập nhật cookedRecipeIds)
        user_requirements (dict): User requirements
        ingredient_name_to_id (dict): Mapping ingredient name to id
        tag_name_to_id (dict): Mapping tag name to id
        ingredient_sim_matrix (np.ndarray): Ingredient similarity matrix
        tag_sim_matrix (np.ndarray): Tag similarity matrix
        all_ingredient_names (list): Danh sách tất cả ingredient names
        all_tag_names (list): Danh sách tất cả tag names
        all_ingredient_ids (list): Danh sách tất cả ingredient IDs
        all_tag_ids (list): Danh sách tất cả tag IDs
        serving_size (int): Số lượng người ăn
    
    Returns:
        dict: Dictionary chứa thực đơn cho 7 ngày
    """
    
    weekly_plan = {}
    previous_main_dishes = []  # Lưu trữ các món chính của ngày trước
    
    # Tên các ngày trong tuần
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
    for i, day in enumerate(weekdays):
        
        # Nếu có món chính của ngày trước, thêm vào danh sách không thích
        if previous_main_dishes:
            for dish in previous_main_dishes:
                dish_id = dish.get("id")
                if dish_id and dish_id not in user_profile.get("notFavoriteRecipeIds", []):
                    user_profile["notFavoriteRecipeIds"].append(dish_id)
        
        # Generate thực đơn cho ngày hiện tại
        daily_plan = suggest_daily_meals(
            recipes=recipes,
            similarity_matrix=similarity_matrix,
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
            serving_size=serving_size
        )
        
        # Lưu thực đơn của ngày
        weekly_plan[day] = daily_plan
        
        # Thu thập các món chính của ngày hiện tại để tránh lặp lại ngày mai
        current_main_dishes = []
        
        # Lấy món chính từ bữa trưa và tối
        for meal in daily_plan.get("meals", []):
            meal_type_id = meal.get("mealTypeId", "")
            if meal_type_id in ["bữa trưa", "bữa tối"]:
                meal_recipes = meal.get("recipes", [])
                for recipe in meal_recipes:
                    recipe_types = recipe.get("recipe_type", [])
                    # Kiểm tra xem có phải món chính không
                    if any("món chính" in str(rt).lower() for rt in recipe_types):
                        current_main_dishes.append(recipe)
        
        # Cập nhật danh sách món chính của ngày trước
        previous_main_dishes = current_main_dishes
        
        # Xóa các món chính của ngày trước khỏi danh sách không thích ngay sau khi generate xong ngày hiện tại
        if i > 0:  # Không xóa gì cho ngày đầu tiên (i=0)
            removed_count = 0
            # Lấy danh sách món chính của ngày trước (đã được lưu trước đó)
            previous_day_main_dishes = []
            i_int = int(i) if hasattr(i, 'item') else i  # Chuyển đổi numpy array thành int nếu cần
            if i_int == 1:  # Ngày 2, xóa món chính của ngày 1
                previous_day_main_dishes = weekly_plan[weekdays[0]]["previous_main_dishes"]
            elif i_int == 2:  # Ngày 3, xóa món chính của ngày 2
                previous_day_main_dishes = weekly_plan[weekdays[1]]["previous_main_dishes"]
            elif i_int == 3:  # Ngày 4, xóa món chính của ngày 3
                previous_day_main_dishes = weekly_plan[weekdays[2]]["previous_main_dishes"]
            elif i_int == 4:  # Ngày 5, xóa món chính của ngày 4
                previous_day_main_dishes = weekly_plan[weekdays[3]]["previous_main_dishes"]
            elif i_int == 5:  # Ngày 6, xóa món chính của ngày 5
                previous_day_main_dishes = weekly_plan[weekdays[4]]["previous_main_dishes"]
            elif i_int == 6:  # Ngày 7, xóa món chính của ngày 6
                previous_day_main_dishes = weekly_plan[weekdays[5]]["previous_main_dishes"]
            
            for dish in previous_day_main_dishes:
                dish_id = dish.get("id")
                if dish_id and dish_id in user_profile.get("notFavoriteRecipeIds", []):
                    user_profile["notFavoriteRecipeIds"].remove(dish_id)
                    removed_count += 1
        
        # Lưu danh sách món chính của ngày hiện tại để sử dụng cho ngày tiếp theo
        daily_plan["previous_main_dishes"] = current_main_dishes.copy()
    
    # Tạo summary cho cả tuần
    weekly_summary = {
        "total_days": 7,
        "serving_size": serving_size,
        "total_recipes_week": sum(
            daily_plan.get("daily_summary", {}).get("total_recipes", 0)
            for daily_plan in weekly_plan.values()
        ),
        "daily_breakdown": {
            day: {
                "total_recipes": daily_plan.get("daily_summary", {}).get("total_recipes", 0),
                "breakfast_count": daily_plan.get("daily_summary", {}).get("breakfast_count", 0),
                "lunch_count": daily_plan.get("daily_summary", {}).get("lunch_count", 0),
                "dinner_count": daily_plan.get("daily_summary", {}).get("dinner_count", 0)
            }
            for day, daily_plan in weekly_plan.items()
        }
    }
    
    weekly_plan["weekly_summary"] = weekly_summary
    

    
    return weekly_plan


def display_weekly_plan(weekly_plan):
    """
    Hiển thị thực đơn tuần một cách đẹp mắt
    
    Args:
        weekly_plan (dict): Thực đơn tuần
    """
    print("\n" + "="*80)
    print("📅 THỰC ĐƠN TUẦN - WEEKLY MEAL PLAN")
    print("="*80)
    
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    weekday_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    
    for i, (day, weekday_name) in enumerate(zip(weekdays, weekday_names)):
        if day in weekly_plan:
            daily_plan = weekly_plan[day]
            print(f"\n🌅 {weekday_name.upper()} ({day.upper()}) - Ngày {i+1}")
            print("-" * 60)
            
            # Hiển thị từng bữa
            for meal in daily_plan.get("meals", []):
                meal_type_id = meal.get("mealTypeId", "")
                meal_display_names = {
                    "bữa sáng": "🌅 BỮA SÁNG",
                    "bữa trưa": "🌞 BỮA TRƯA", 
                    "bữa tối": "🌙 BỮA TỐI"
                }
                
                display_name = meal_display_names.get(meal_type_id, meal_type_id.upper())
                print(f"\n{display_name}:")
                
                # Hiển thị mapRecipe
                map_recipe = meal.get("mapRecipe", {})
                for recipe_type, recipe_ids in map_recipe.items():
                    if recipe_ids:
                        print(f"  {recipe_type}: {len(recipe_ids)} món")
                        for recipe_id in recipe_ids:
                            print(f"    - Recipe ID: {recipe_id}")
    
    # Hiển thị summary
    if "weekly_summary" in weekly_plan:
        summary = weekly_plan["weekly_summary"]
        print(f"\n" + "="*80)
        print("📊 TỔNG KẾT TUẦN - WEEKLY SUMMARY")
        print("="*80)
        print(f"🍽️ Tổng số món trong tuần: {summary['total_recipes_week']}")
        print(f"👥 Số người ăn: {summary['serving_size']}")
        print(f"📅 Số ngày: {summary['total_days']}")
        
        print(f"\n📋 Chi tiết từng ngày:")
        for day, day_info in summary["daily_breakdown"].items():
            print(f"  {day.title()}: {day_info['total_recipes']} món "
                  f"(Sáng: {day_info['breakfast_count']}, "
                  f"Trưa: {day_info['lunch_count']}, "
                  f"Tối: {day_info['dinner_count']})")

def main():
    """
    Hàm main để test chức năng generate thực đơn tuần
    """
    from embeddings import load_phobert_model
    from utils import load_data
    from similarity import (
        create_recipe_similarity_matrix,
        create_ingredient_similarity_matrix, 
        create_tag_similarity_matrix
    )
    
    print("🚀 Đang khởi tạo hệ thống generate thực đơn tuần...")
    
    try:
        # Load model và data
        print("📚 Đang load PhoBERT model...")
        model, tokenizer = load_phobert_model()
        print("✅ Đã load xong PhoBERT model!")
        
        print("📊 Đang load data...")
        df, recipes = load_data("data/recipes.json")
        _, ingredients = load_data("data/ingredients.json") 
        _, tags = load_data("data/tags.json")
        print(f"✅ Đã load {len(recipes)} món ăn, {len(ingredients)} nguyên liệu, {len(tags)} tags")
        
        # Tạo similarity matrices
        print("🔍 Đang tạo similarity matrices...")
        recipe_sim_matrix, rec_name_to_rec_id = create_recipe_similarity_matrix(df, recipes, model, tokenizer)
        ingredient_sim_matrix, ingredient_name_to_id, all_ingredient_names, all_ingredient_ids = create_ingredient_similarity_matrix(ingredients, model, tokenizer)
        tag_sim_matrix, tag_name_to_id, all_tag_names, all_tag_ids = create_tag_similarity_matrix(tags, model, tokenizer)
        print("✅ Đã tạo xong similarity matrices!")

        
        # Reset user profile để test
        user_profile = get_default_user_profile()
        user_requirements = get_default_user_requirements()
        user_requirements["difficulty"] = "1"
        user_requirements["excludeMethod"] = []
        
        weekly_plan_2 = generate_weekly_meal_plan(
            recipes=recipes,
            similarity_matrix=recipe_sim_matrix,
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
            serving_size=2  # 3 người ăn
        )
        
        display_weekly_plan(weekly_plan_2)
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
