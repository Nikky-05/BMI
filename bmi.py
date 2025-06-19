from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import os

bmi_bp = Blueprint('bmi', __name__)

# Load the trained model
model_path = os.path.join(os.path.dirname(__file__), '..', 'bmi_diet_model.pkl')
model = joblib.load(model_path)

@bmi_bp.route('/predict', methods=['POST'])
def predict_diet():
    try:
        data = request.get_json()
        
        # Extract input data
        gender = data.get('gender')
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        
        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)
        
        # Prepare input for the model
        input_data = pd.DataFrame({
            'Height_cm': [height],
            'Weight_kg': [weight],
            'BMI': [bmi],
            'Gender_Male': [1 if gender.lower() == 'male' else 0]
        })
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Get detailed diet recommendations
        diet_details = get_diet_details(prediction, bmi)
        
        return jsonify({
            'success': True,
            'bmi': round(bmi, 2),
            'diet_recommendation': prediction,
            'diet_details': diet_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def get_diet_details(diet_type, bmi):
    """Get detailed diet recommendations based on diet type and BMI"""
    
    if diet_type == 'Gain Weight Diet':
        return {
            'category': 'Underweight',
            'bmi_range': 'Below 18.5',
            'recommendations': [
                'Increase caloric intake with nutrient-dense foods',
                'Include healthy fats like nuts, avocados, and olive oil',
                'Eat frequent, smaller meals throughout the day',
                'Focus on protein-rich foods like lean meats, fish, and legumes',
                'Add healthy snacks between meals'
            ],
            'foods_to_include': [
                'Nuts and nut butters',
                'Whole grain breads and cereals',
                'Lean proteins (chicken, fish, eggs)',
                'Dairy products',
                'Healthy oils and fats'
            ],
            'foods_to_avoid': [
                'Empty calorie foods',
                'Excessive caffeine',
                'Foods high in sugar without nutrients'
            ]
        }
    
    elif diet_type == 'Balanced Diet':
        return {
            'category': 'Normal Weight',
            'bmi_range': '18.5 - 24.9',
            'recommendations': [
                'Maintain current weight with balanced nutrition',
                'Include variety from all food groups',
                'Practice portion control',
                'Stay hydrated with plenty of water',
                'Regular physical activity'
            ],
            'foods_to_include': [
                'Fruits and vegetables',
                'Whole grains',
                'Lean proteins',
                'Low-fat dairy',
                'Healthy fats in moderation'
            ],
            'foods_to_avoid': [
                'Processed foods',
                'Excessive sugar and salt',
                'Trans fats',
                'Excessive alcohol'
            ]
        }
    
    elif diet_type == 'Weight Loss Diet':
        return {
            'category': 'Overweight',
            'bmi_range': '25.0 - 29.9',
            'recommendations': [
                'Create a moderate caloric deficit',
                'Focus on nutrient-dense, low-calorie foods',
                'Increase fiber intake for satiety',
                'Practice mindful eating',
                'Combine diet with regular exercise'
            ],
            'foods_to_include': [
                'Leafy greens and vegetables',
                'Lean proteins (fish, chicken breast, tofu)',
                'Whole grains in moderation',
                'Fruits (especially berries)',
                'Low-fat dairy or alternatives'
            ],
            'foods_to_avoid': [
                'High-calorie processed foods',
                'Sugary drinks and snacks',
                'Fried foods',
                'Refined carbohydrates',
                'Large portion sizes'
            ]
        }
    
    else:  # Obesity Management Diet
        return {
            'category': 'Obese',
            'bmi_range': '30.0 and above',
            'recommendations': [
                'Consult with healthcare provider for personalized plan',
                'Focus on significant caloric reduction',
                'Emphasize high-fiber, low-calorie foods',
                'Consider meal planning and preparation',
                'Incorporate regular physical activity as approved by doctor'
            ],
            'foods_to_include': [
                'Non-starchy vegetables',
                'Lean proteins',
                'Small portions of whole grains',
                'Low-sugar fruits',
                'Plenty of water'
            ],
            'foods_to_avoid': [
                'High-calorie beverages',
                'Fast food and processed meals',
                'Sweets and desserts',
                'High-fat foods',
                'Large portion sizes'
            ]
        }

@bmi_bp.route('/bmi-categories', methods=['GET'])
def get_bmi_categories():
    """Return BMI categories for reference"""
    return jsonify({
        'categories': [
            {'range': 'Below 18.5', 'category': 'Underweight'},
            {'range': '18.5 - 24.9', 'category': 'Normal Weight'},
            {'range': '25.0 - 29.9', 'category': 'Overweight'},
            {'range': '30.0 and above', 'category': 'Obese'}
        ]
    })

