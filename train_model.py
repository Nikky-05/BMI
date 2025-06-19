
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load the synthetic data
data = pd.read_csv("bmi_diet_data.csv")

# Prepare the data for training
X = data[["Gender", "Height_cm", "Weight_kg", "BMI"]]
y = data["Diet_Recommendation"]

# Convert 'Gender' to numerical using one-hot encoding
X = pd.get_dummies(X, columns=["Gender"], drop_first=True)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the RandomForestClassifier model
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1) # n_jobs=-1 to use all available cores
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")

# Save the trained model
joblib.dump(model, "bmi_diet_model.pkl")
print("Trained model saved as bmi_diet_model.pkl")


