from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
CORS(app)

# Load the trained model
try:
    model = joblib.load('bmi_diet_model.pkl')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'bmi_diet_db',
    'user': 'root',
    'password': 'NKpallotti@99'
}

def create_database_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize database and create tables if they don't exist"""
    try:
        connection = create_database_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS bmi_diet_db")
            cursor.execute("USE bmi_diet_db")
            
            # Create users table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bmi_calculations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                gender VARCHAR(10),
                height FLOAT,
                weight FLOAT,
                bmi FLOAT,
                category VARCHAR(20),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Database initialized successfully!")
            
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def calculate_bmi(height, weight):
    """Calculate BMI from height (cm) and weight (kg)"""
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Get BMI category based on BMI value"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_diet_recommendations(bmi, gender):
    """Get diet recommendations based on BMI and gender"""
    category = get_bmi_category(bmi)
    
    recommendations = {
        "Underweight": {
            "category": "Underweight",
            "bmi_range": "Below 18.5",
            "recommendations": [
                "Increase caloric intake with nutrient-dense foods",
                "Include healthy fats like nuts, avocados, and olive oil",
                "Eat frequent, smaller meals throughout the day",
                "Focus on protein-rich foods for muscle building",
                "Consider consulting a nutritionist for personalized guidance"
            ],
            "foods_to_include": [
                "Nuts and nut butters", "Avocados", "Whole grains", "Lean proteins", 
                "Healthy oils", "Dried fruits", "Protein shakes", "Full-fat dairy"
            ],
            "foods_to_avoid": [
                "Empty calories from junk food", "Excessive caffeine", "Foods high in trans fats"
            ]
        },
        "Normal Weight": {
            "category": "Normal Weight",
            "bmi_range": "18.5 - 24.9",
            "recommendations": [
                "Maintain current weight with balanced nutrition",
                "Include variety from all food groups",
                "Practice portion control",
                "Stay hydrated with plenty of water",
                "Regular physical activity"
            ],
            "foods_to_include": [
                "Fruits and vegetables", "Whole grains", "Lean proteins", 
                "Low-fat dairy", "Healthy fats in moderation"
            ],
            "foods_to_avoid": [
                "Processed foods", "Excessive sugar and salt", "Trans fats", "Excessive alcohol"
            ]
        },
        "Overweight": {
            "category": "Overweight",
            "bmi_range": "25.0 - 29.9",
            "recommendations": [
                "Create a moderate caloric deficit for gradual weight loss",
                "Focus on nutrient-dense, low-calorie foods",
                "Increase fiber intake to promote satiety",
                "Practice mindful eating and portion control",
                "Incorporate regular physical activity"
            ],
            "foods_to_include": [
                "Vegetables", "Fruits", "Lean proteins", "Whole grains", 
                "Low-fat dairy", "Legumes", "Water-rich foods"
            ],
            "foods_to_avoid": [
                "High-calorie processed foods", "Sugary drinks", "Refined carbohydrates", 
                "Fried foods", "High-fat snacks"
            ]
        },
        "Obese": {
            "category": "Obese",
            "bmi_range": "30.0 and above",
            "recommendations": [
                "Consult healthcare professionals for comprehensive weight management",
                "Create a structured meal plan with caloric deficit",
                "Focus on high-fiber, low-calorie foods",
                "Consider working with a registered dietitian",
                "Gradual lifestyle changes for sustainable results"
            ],
            "foods_to_include": [
                "Non-starchy vegetables", "Lean proteins", "Whole grains in moderation", 
                "Fruits in moderation", "Low-fat dairy", "Legumes"
            ],
            "foods_to_avoid": [
                "High-calorie processed foods", "Sugary beverages", "Fast food", 
                "Refined sugars", "High-fat foods", "Large portion sizes"
            ]
        }
    }
    
    return recommendations.get(category, recommendations["Normal Weight"])

def save_calculation_to_db(gender, height, weight, bmi, category):
    """Save BMI calculation to database"""
    try:
        connection = create_database_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO bmi_calculations (gender, height, weight, bmi, category)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (gender, height, weight, bmi, category))
            connection.commit()
            print("Calculation saved to database!")
    except Error as e:
        print(f"Error saving to database: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for BMI calculation and diet recommendations"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not all(key in data for key in ['gender', 'height', 'weight']):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: gender, height, weight'
            }), 400
        
        gender = data['gender']
        height = float(data['height'])
        weight = float(data['weight'])
        
        # Validate ranges
        if not (100 <= height <= 250):
            return jsonify({
                'success': False,
                'error': 'Height must be between 100-250 cm'
            }), 400
            
        if not (30 <= weight <= 300):
            return jsonify({
                'success': False,
                'error': 'Weight must be between 30-300 kg'
            }), 400
        
        # Calculate BMI
        bmi = calculate_bmi(height, weight)
        category = get_bmi_category(bmi)
        
        # Get diet recommendations
        diet_details = get_diet_recommendations(bmi, gender)
        
        # Save to database (optional, comment out if MySQL is not available)
        # save_calculation_to_db(gender, height, weight, bmi, category)
        
        return jsonify({
            'success': True,
            'bmi': bmi,
            'category': category,
            'diet_details': diet_details
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid input values'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    # Initialize database (comment out if MySQL is not available)
    # init_database()
    
    app.run(host='0.0.0.0', port=5001, debug=True)

