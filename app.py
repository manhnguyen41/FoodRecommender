import streamlit as st
import json
from engine import (
    load_recipes, extract_features, calculate_similarity_matrix,
    recommend_top_k_from_profile_and_requirements
)

# ------------------- Load data & pre-compute -------------------
df, recipes = load_recipes("recipes_with_ingredients_and_tags.json")
X, _, _, _, ing_name_to_idx, tag_name_to_idx, ing_name_to_ing_id = extract_features(df, recipes)
sim_matrix = calculate_similarity_matrix(X)

# Options for selects
all_ing_names = list(ing_name_to_idx.keys())
recipe_id2name = {r["id"]: r["name"] for r in recipes}
recipe_name2id = {v: k for k, v in recipe_id2name.items()}
all_recipe_names = list(recipe_id2name.values())

# ------------------- UI -------------------
st.set_page_config(page_title="Food Recommender", layout="wide")
st.title("🍽️ Food Recommender Demo")

with st.form("recommend_form"):
    st.subheader("👤 User Profile & Requirement")

    fav_ings = st.multiselect("Favorite ingredients", all_ing_names,
                              default=st.session_state.get("fav_ings", []))
    not_fav_ings = st.multiselect("Not favorite ingredients", all_ing_names,
                                  default=st.session_state.get("not_fav_ings", []))
    allergy_ings = st.multiselect("Allergy ingredients", all_ing_names,
                                  default=st.session_state.get("allergy_ings", []))

    budget = st.number_input("Budget (VND)", 0, 500000,
                             st.session_state.get("budget", 80000), 5000)

    fav_recipes = st.multiselect("Favorite recipes", all_recipe_names,
                                 default=st.session_state.get("fav_recipes", []))
    not_fav_recipes = st.multiselect("Not favorite recipes", all_recipe_names,
                                     default=st.session_state.get("not_fav_recipes", []))
    cooked_recipes = st.multiselect("Already cooked recipes", all_recipe_names,
                                    default=st.session_state.get("cooked_recipes", []))

    cooking_time = st.slider("Max cooking time (minutes)", 5, 120,
                             st.session_state.get("cooking_time", 30))

    avail_ings = st.multiselect("Available ingredients", all_ing_names,
                                default=st.session_state.get("avail_ings", []))

    top_k = st.slider("Number of recommended dishes (Top-K)", 1, 20,
                      st.session_state.get("top_k", 5))

    use_sim_matrix = st.checkbox("Use similarity matrix",
                                 value=st.session_state.get("use_sim_matrix", True))
    prefer_available_ingredients = st.checkbox("Prefer available ingredients",
                                               value=st.session_state.get("prefer_available_ingredients", True))

    submitted = st.form_submit_button("🔍 Recommend")

# ------------------- Recommend logic -------------------
if submitted:
    st.write(f"**Settings**: Using similarity matrix: {use_sim_matrix}, Prefer available ingredients: {prefer_available_ingredients}")
    # Save input state
    st.session_state["fav_ings"] = fav_ings
    st.session_state["not_fav_ings"] = not_fav_ings
    st.session_state["allergy_ings"] = allergy_ings
    st.session_state["budget"] = budget
    st.session_state["fav_recipes"] = fav_recipes
    st.session_state["not_fav_recipes"] = not_fav_recipes
    st.session_state["cooked_recipes"] = cooked_recipes
    st.session_state["avail_ings"] = avail_ings
    st.session_state["cooking_time"] = cooking_time
    st.session_state["top_k"] = top_k
    st.session_state["use_sim_matrix"] = use_sim_matrix
    st.session_state["prefer_available_ingredients"] = prefer_available_ingredients

    def name2ids(names, mapper):
        return [mapper[name] for name in names if name in mapper]

    profile = {
        "familyId": "demo",
        "favoriteIngredientIds": name2ids(fav_ings, ing_name_to_ing_id),
        "notFavoriteIngredientIds": name2ids(not_fav_ings, ing_name_to_ing_id),
        "allergyIngredientIds": name2ids(allergy_ings, ing_name_to_ing_id),
        "suggestedDietModeIngredientIds": [],
        "suggestedPathologyIngredientIds": [],
        "notSuggestedDietModeIngredientIds": [],
        "notSuggestedPathologyIngredientIds": [],
        "budget": budget,
        "includeTags": [],
        "excludeTags": [],
        "favoriteRecipeIds": [recipe_name2id[n] for n in fav_recipes],
        "notFavoriteRecipeIds": [recipe_name2id[n] for n in not_fav_recipes],
        "cookedRecipeIds": [recipe_name2id[n] for n in cooked_recipes],
        "feedbackRecipeIds": {}
    }

    requirement = {
        "mealType": "dinner",
        "cookingTime": cooking_time,
        "budget": budget,
        "availableIngredientIds": name2ids(avail_ings, ing_name_to_ing_id),
    }

    top_k_recs, scores = recommend_top_k_from_profile_and_requirements(
        recipes, sim_matrix if use_sim_matrix else None, profile, requirement,
        ing_name_to_idx, tag_name_to_idx, k=top_k, prefer_available_ingredients=prefer_available_ingredients
    )

    st.subheader("✅ Recommendations")
    if not top_k_recs:
        st.warning("No matching dish found")
    for rec, sc in zip(top_k_recs, scores):
        st.markdown(f"**{rec['name']}** — score `{sc:.2f}`")
        if rec["images"]:
            st.image(rec["images"][0], width=300)
        st.write(f"⏱ {rec['cooking_time']} min | 💰 {rec['cost']:,} ₫")
        st.write(", ".join(ing['name'] for ing in rec['ingredients']))
        st.divider()
