from flask import Flask, request, jsonify
from PIL import Image
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Configure Google Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Define the /summarize_image route for summarizing image content using Gemini
@app.route("/summarize_image", methods=["POST"])
def summarize_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    try:
        # Open the image using PIL directly from the uploaded file
        image = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Failed to open image: {str(e)}"}), 500

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [
                image,
                "\n\nCan you summarize the given text in this photo? If you can't find any text, print There is no text in the image and describe the image."
            ]
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate summary with Gemini: {str(e)}"}), 500

    return jsonify({"summary": result.text}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)