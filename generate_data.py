
import pandas as pd
import numpy as np

def generate_synthetic_data(num_rows):
    np.random.seed(42)

    genders = np.random.choice(['Male', 'Female'], size=num_rows)
    
    # Realistic height and weight ranges
    heights_male = np.random.normal(175, 10, num_rows) # cm
    weights_male = np.random.normal(75, 15, num_rows) # kg
    heights_female = np.random.normal(162, 8, num_rows) # cm
    weights_female = np.random.normal(60, 12, num_rows) # kg

    heights = np.where(genders == 'Male', heights_male, heights_female)
    weights = np.where(genders == 'Male', weights_male, weights_female)

    # Ensure positive values
    heights = np.maximum(100, heights) 
    weights = np.maximum(30, weights)

    bmis = weights / ((heights / 100)**2)

    # Simplified diet recommendations based on BMI categories
    def get_diet_recommendation(bmi):
        if bmi < 18.5:
            return 'Gain Weight Diet'
        elif 18.5 <= bmi < 24.9:
            return 'Balanced Diet'
        elif 24.9 <= bmi < 29.9:
            return 'Weight Loss Diet'
        else:
            return 'Obesity Management Diet'

    diet_recommendations = np.array([get_diet_recommendation(bmi) for bmi in bmis])

    data = pd.DataFrame({
        'Gender': genders,
        'Height_cm': heights,
        'Weight_kg': weights,
        'BMI': bmis,
        'Diet_Recommendation': diet_recommendations
    })
    return data

# Generate 1 million rows of data
num_rows = 1000000
synthetic_df = generate_synthetic_data(num_rows)
synthetic_df.to_csv('bmi_diet_data.csv', index=False)

print(f"Generated {num_rows} rows of synthetic data and saved to bmi_diet_data.csv")


