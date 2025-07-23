# FoodRecommender
git clone git@github.com:manhnguyen41/FoodRecommender.git

cd FoodRecommender

docker build -t food-recommendation-app .

docker run -p 8501:8501 food-recommendation-app

http://localhost:8501
