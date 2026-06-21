from typing import Dict, Any

def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """
    Calculate Body Mass Index (BMI) and determine classification and health risk.
    Formula: BMI = weight (kg) / (height (m) ^ 2)
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {"value": 0.0, "status": "Invalid Input", "feedback": "Please enter valid height and weight values."}
        
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 2)
    
    if bmi < 18.5:
        status = "Underweight"
        feedback = "Your BMI indicates you are underweight. Consider discussing with a healthcare professional to establish balanced nutritional intake."
        color = "#EF4444"
    elif 18.5 <= bmi < 25.0:
        status = "Normal Weight"
        feedback = "Congratulations! Your BMI is within the healthy weight range. Maintain your current active lifestyle and balanced diet."
        color = "#10B981"
    elif 25.0 <= bmi < 30.0:
        status = "Overweight"
        feedback = "Your BMI indicates you are slightly overweight. Incorporating regular physical activity and a calorie-conscious diet can help."
        color = "#F59E0B"
    else:
        status = "Obese"
        feedback = "Your BMI falls in the obese range. We recommend speaking to a certified dietitian or physician for personalized guidance."
        color = "#EF4444"
        
    return {
        "value": bmi,
        "status": status,
        "feedback": feedback,
        "color": color
    }

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation.
    Men: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (y) + 5
    Women: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (y) - 161
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return 0.0
        
    if gender.lower() in ["male", "m"]:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
    return round(bmr, 2)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on activity level.
    """
    multipliers = {
        "Sedentary (little/no exercise)": 1.2,
        "Lightly Active (exercise 1-3 days/week)": 1.375,
        "Moderately Active (exercise 3-5 days/week)": 1.55,
        "Very Active (exercise 6-7 days/week)": 1.725,
        "Extra Active (hard physical job or 2x training)": 1.9
    }
    
    multiplier = multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)

def calculate_ideal_weight(height_cm: float, gender: str) -> float:
    """
    Calculate Ideal Body Weight (IBW) using the Devine Formula:
    Male: 50.0 kg + 2.3 kg per inch over 5 feet
    Female: 45.5 kg + 2.3 kg per inch over 5 feet
    Applicable for heights > 152.4 cm (5 feet).
    """
    if height_cm <= 0:
        return 0.0
        
    # Convert height to inches
    height_in = height_cm / 2.54
    inches_over_5ft = max(0.0, height_in - 60.0)
    
    if gender.lower() in ["male", "m"]:
        ibw = 50.0 + (2.3 * inches_over_5ft)
    else:
        ibw = 45.5 + (2.3 * inches_over_5ft)
        
    return round(ibw, 1)

def generate_health_summary(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str) -> Dict[str, Any]:
    """
    Convenience function to run all health calculators and compile reports.
    """
    bmi_info = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    ibw = calculate_ideal_weight(height_cm, gender)
    
    return {
        "bmi": bmi_info["value"],
        "bmi_status": bmi_info["status"],
        "bmi_feedback": bmi_info["feedback"],
        "bmi_color": bmi_info["color"],
        "bmr": bmr,
        "tdee": tdee,
        "ideal_weight_kg": ibw
    }
