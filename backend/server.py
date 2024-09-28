from flask import Flask, request, jsonify
from PIL import Image
from transformers import pipeline
from flask_cors import CORS
import torch
import io
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Check if GPU is available, use device 0 (GPU) if available, else use CPU
device = 0 if torch.cuda.is_available() else -1

# Initialize the pipeline for image captioning
pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large", device=device)

# Configure Google Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Define the /caption route to handle image input and return the caption
@app.route("/caption", methods=["POST"])
def caption_image():
    
    # Check if an image file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    # Get the file from the request
    file = request.files['file']
    
    # Read the image and process it with PIL
    try:
        image = Image.open(io.BytesIO(file.read()))
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400
    
    # Generate the caption using the pipeline, set max_new_tokens for caption length control
    caption = pipe(image, max_new_tokens=100)
        
    # Return the generated caption
    return jsonify({"caption": caption[0]['generated_text']}), 200


# Define the /summarize_image route for summarizing image content using Gemini
@app.route("/summarize_image", methods=["POST"])
def summarize_image():
    
    # Check if an image file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    # Get the file from the request
    file = request.files['file']
    
    # Save the image file temporarily to upload it to Gemini
    temp_file_path = "temp_image.jpeg"
    try:
        with open(temp_file_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        return jsonify({"error": f"Failed to save image file: {str(e)}"}), 500
    
    # Upload the image file to Gemini
    try:
        uploaded_file = genai.upload_file(temp_file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to upload image to Gemini: {str(e)}"}), 500
    
    # Generate content using the Gemini model
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [uploaded_file, "\n\n", "Can you summarize the given text in this photo? If you can't find any text, print There is no text in the image and discribe the image."],
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate summary with Gemini: {str(e)}"}), 500
    
    # Return the summarized content
    return jsonify({"summary": result.text}), 200


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)