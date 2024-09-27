from flask import Flask, request, jsonify
from PIL import Image
from transformers import pipeline
import torch
import io

# Initialize the Flask app
app = Flask(__name__)

# Check if GPU is available, use device 0 (GPU) if available, else use CPU
device = 0 if torch.cuda.is_available() else -1

# Initialize the pipeline for image captioning
pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large", device=device)

# Define the /summarize route to handle image input and return the caption
@app.route("/summarize", methods=["POST"])
def summarize_image():
    
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

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)