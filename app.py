import os
import base64
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# 🌍 Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🗣️ Optional Voice Init (local only)
USE_VOICE = os.getenv("USE_VOICE", "false").lower() == "true"
if USE_VOICE:
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)

# 📢 Speak text only if enabled
def speak_text(text):
    if USE_VOICE:
        engine.say(text)
        engine.runAndWait()

# ⚙️ Flask Setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔁 Image Encoding
def base64_encode(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 🏠 Home Route
@app.route("/")
def index():
    return render_template("index.html")

# 🧠 Analyze Image
@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    try:
        image = request.files["image"]
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        image_base64 = base64_encode(image_path)
        image_data = {
            "mime_type": "image/jpeg",
            "data": base64.b64decode(image_base64)
        }

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(["Describe this image in detail.", image_data])
        result = response.text.strip()
        speak_text(result)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ❓ Ask Questions About Image
@app.route("/ask-about-image", methods=["POST"])
def ask_about_image():
    try:
        image = request.files["image"]
        question = request.form.get("question", "")
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        image_base64 = base64_encode(image_path)
        image_data = {
            "mime_type": "image/jpeg",
            "data": base64.b64decode(image_base64)
        }

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([question, image_data])
        result = response.text.strip()
        speak_text(result)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Run App
if __name__ == "__main__":
    app.run(debug=True)



