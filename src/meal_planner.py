from typing import Dict, List, Any

# Target ratios (Carbs, Protein, Fat) as proportion of total energy intake
GOAL_MACRO_RATIOS = {
    "weight_loss": {"carbs": 0.40, "protein": 0.35, "fat": 0.25},
    "maintenance": {"carbs": 0.50, "protein": 0.20, "fat": 0.30},
    "weight_gain": {"carbs": 0.55, "protein": 0.25, "fat": 0.20}
}

# Realistic Indian meal plans with specific local dishes
MEAL_TEMPLATES = {
    "vegetarian": {
        "low": { # < 1600 kcal
            "breakfast": "Moong Dal Chilla (2 pieces) filled with grated paneer, served with mint-coriander chutney.",
            "lunch": "Yellow Dal Tadka (1 cup), Mixed Vegetable Sabzi (1 cup), Brown Rice (1/2 cup), and Cucumber Tomato Salad.",
            "snack": "Roasted Chickpeas / Chana (30g) with a cup of buttermilk or green tea.",
            "dinner": "Tofu Stir-fry with broccoli and bell peppers, 1 Whole Wheat Roti, and a small bowl of vegetable soup."
        },
        "medium": { # 1600 - 2200 kcal
            "breakfast": "Oats Idli (3 pieces) with Sambar and coconut chutney, plus a handful of soaked almonds.",
            "lunch": "Paneer Tikka (150g cooked), Dal Makhani (light version, 1 cup), 2 Chapattis (Rotis), and Beetroot Raita.",
            "snack": "Apple slices with 1.5 tablespoons of peanut butter and a cup of warm cardamom tea.",
            "dinner": "Palak Paneer (1 cup), Jeera Rice (1/2 cup), 1 Chapatti, and a mixed green salad."
        },
        "high": { # > 2200 kcal
            "breakfast": "Stuffed Paneer Parathas (2 parathas cooked with minimal ghee), served with Greek yogurt (1 cup) and a banana.",
            "lunch": "Chickpea/Chole Curry (1.5 cups), Vegetable Pulao (1.5 cups), Boondi Raita (1 cup), and stir-fried green beans.",
            "snack": "Handful of walnuts, cashews, pumpkin seeds, and a protein shake mixed with soy/dairy milk.",
            "dinner": "Paneer Butter Masala (light version, 1.5 cups), Dal Tadka (1 cup), 2 Bajra Rotis, and steamed asparagus."
        }
    },
    "non-vegetarian": {
        "low": { # < 1600 kcal
            "breakfast": "Masala Egg White Omelet (3 egg whites, 1 whole egg) with spinach and onions, and 1 slice of multi-grain toast.",
            "lunch": "Grilled Chicken Breast (120g), Dal Tadka (1/2 cup), Brown Rice (1/2 cup), and a green salad.",
            "snack": "Sprouts Salad with lemon juice and a hard-boiled egg white.",
            "dinner": "Baked Fish Curry (Salmon or Pomfret, 120g) cooked in tomato-onion gravy, served with steamed broccoli."
        },
        "medium": { # 1600 - 2200 kcal
            "breakfast": "Egg Bhurji (3 eggs scrambled with vegetables) with 2 slices of whole wheat toast and fresh orange juice.",
            "lunch": "Chicken Tikka (150g), Yellow Dal (1 cup), 2 Whole Wheat Rotis, and onion-cucumber salad.",
            "snack": "Whey protein shake with water and 1 banana.",
            "dinner": "Fish Curry (Rohu/Surmai, 150g), Brown Rice (1 cup), Stir-fried cabbage and carrots, and beetroot salad."
        },
        "high": { # > 2200 kcal
            "breakfast": "Egg Bhurji (4 eggs) cooked with bell peppers and cheese, served with 2 multigrain parathas and a bowl of fresh papaya.",
            "lunch": "Chicken Biryani (made with lean chicken breast, 1.5 cups), Dal Makhani (1 cup), Cucumber Raita (1 cup), and salad.",
            "snack": "Hard-boiled eggs (3 whole eggs), a handful of almonds, and a protein bar.",
            "dinner": "Mutton/Chicken Curry (gravy, 180g), 2 Bajra Rotis, Brown Rice (1 cup), and sautéed vegetables."
        }
    }
}

def calculate_adjusted_calories(tdee: float, goal: str) -> float:
    """
    Adjust TDEE based on weight goals:
    - weight_loss: Deficit of 500 kcal (capped at min 1200 kcal)
    - weight_gain: Surplus of 500 kcal
    - maintenance: Same as TDEE
    """
    if goal == "weight_loss":
        adjusted = max(1200.0, tdee - 500.0)
    elif goal == "weight_gain":
        adjusted = tdee + 500.0
    else:
        adjusted = tdee
    return round(adjusted, 2)

def calculate_macros(calories: float, goal: str) -> Dict[str, float]:
    """
    Calculate macronutrient split in grams based on calorie target.
    Carbohydrates: 4 kcal/gram
    Protein: 4 kcal/gram
    Fat: 9 kcal/gram
    """
    ratios = GOAL_MACRO_RATIOS.get(goal, GOAL_MACRO_RATIOS["maintenance"])
    
    carb_kcal = calories * ratios["carbs"]
    protein_kcal = calories * ratios["protein"]
    fat_kcal = calories * ratios["fat"]
    
    return {
        "carbs_g": round(carb_kcal / 4.0, 1),
        "protein_g": round(protein_kcal / 4.0, 1),
        "fat_g": round(fat_kcal / 9.0, 1),
        "carbs_pct": int(ratios["carbs"] * 100),
        "protein_pct": int(ratios["protein"] * 100),
        "fat_pct": int(ratios["fat"] * 100)
    }

def generate_meal_plan(tdee: float, goal: str, diet_type: str) -> Dict[str, Any]:
    """
    Generate complete meal plan: calories, macros, and diet-specific recommendations with per-meal targets.
    """
    target_calories = calculate_adjusted_calories(tdee, goal)
    macros = calculate_macros(target_calories, goal)
    
    # Determine calorie range bracket for templates
    if target_calories < 1600:
        bracket = "low"
    elif 1600 <= target_calories <= 2200:
        bracket = "medium"
    else:
        bracket = "high"
        
    diet_key = diet_type.lower()
    if diet_key not in ["vegetarian", "non-vegetarian"]:
        diet_key = "vegetarian" # Safe default
        
    raw_meals = MEAL_TEMPLATES[diet_key][bracket]
    total_protein = macros["protein_g"]
    
    # Programmatic split of calorie and protein limits for each meal
    # Breakfast: 25% cal, 25% protein
    # Lunch: 35% cal, 35% protein
    # Snack: 15% cal, 10% protein
    # Dinner: 25% cal, 30% protein
    meals_detailed = {
        "breakfast": {
            "menu": raw_meals["breakfast"],
            "calories": int(target_calories * 0.25),
            "protein": int(total_protein * 0.25)
        },
        "lunch": {
            "menu": raw_meals["lunch"],
            "calories": int(target_calories * 0.35),
            "protein": int(total_protein * 0.35)
        },
        "snack": {
            "menu": raw_meals["snack"],
            "calories": int(target_calories * 0.15),
            "protein": int(total_protein * 0.10)
        },
        "dinner": {
            "menu": raw_meals["dinner"],
            "calories": int(target_calories * 0.25),
            "protein": int(total_protein * 0.30)
        }
    }
    
    return {
        "target_calories": target_calories,
        "macros": macros,
        "meals": meals_detailed,
        "bracket": bracket,
        "diet_type": diet_type
    }
