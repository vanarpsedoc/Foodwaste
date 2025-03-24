from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HF_API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
HF_API_KEY = ""

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

recipes = {
    "apple": ["Apple Pie", "Caramelized Apples", "Apple Smoothie"],
    "banana": ["Banana Bread", "Banana Pancakes", "Banana Smoothie"],
    "carrot": ["Carrot Soup", "Carrot Cake", "Carrot Salad"],
    "tomato": ["Tomato Soup", "Bruschetta", "Tomato Pasta"]
}

expiry_days = {
    "apple": 10,
    "banana": 5,
    "carrot": 15,
    "tomato": 7
}

@app.route("/")
def home():
    return jsonify({"message": "BiteRight API is running with AI!"})

def classify_food(file_path):
    """Sends image to Hugging Face API for classification."""
    with open(file_path, "rb") as f:
        response = requests.post(HF_API_URL, headers=headers, files={"file": f})
    
    if response.status_code != 200:
        return None
    
    predictions = response.json()
    if predictions:
        return predictions[0]["label"].lower()
    
    return None

@app.route("/suggest-recipe", methods=["POST"])
def suggest_recipe():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400  

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    food_item = classify_food(file_path)

    if not food_item or food_item not in recipes:
        return jsonify({"message": "Could not identify food item or no recipe available."})

    suggestion = recipes[food_item][0]  # Pick the first recipe for simplicity
    return jsonify({"message": f"Suggested Recipe: {suggestion} (Ingredient: {food_item})"})

@app.route("/predict-expiry", methods=["POST"])
def predict_expiry():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400  

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    food_item = classify_food(file_path)

    if not food_item or food_item not in expiry_days:
        return jsonify({"message": "Could not identify food item or no expiry data available."})

    days_left = expiry_days[food_item]
    return jsonify({"message": f"{food_item.capitalize()} expires in {days_left} days."})

if __name__ == "__main__":
    app.run(debug=True)
