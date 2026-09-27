from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=API_KEY)


@app.route("/")
def home():
    return "JARVIS backend is online."


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    command = data.get("command", "")

    if not command:
        return jsonify({
            "success": False,
            "error": "No command received"
        }), 400

    try:

        response = client.chats.create(
            model="gemini-3.6-flash"
        ).send_message(
            f"Answer in 2-3 sentences maximum, be concise and direct: {command}"
        )

        return jsonify({
            "success": True,
            "response": response.text
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )