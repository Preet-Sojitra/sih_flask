import pickle
from flask import Flask, request, jsonify
from transformers import MBart50TokenizerFast

app = Flask(__name__)

# Load the saved model and tokenizer
with open("mbart_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("mbart_tokenizer.pkl", "rb") as tokenizer_file:
    tokenizer = pickle.load(tokenizer_file)

# Define the source language (English)
src_lang = "en_XX"

# Define the target languages and their language codes
tgt_languages = {
    "Hindi": "hi_IN",
    "Gujarati": "gu_IN",
    "Bengali": "bn_IN",
    "Tamil": "ta_IN",
    "Telugu": "te_IN",
}

@app.route("/", methods=["GET"])
def home():
    return "Translation API is up and running!"

@app.route("/translate", methods=["POST"])
def translate():
    input_data = request.get_json()
    input_text = input_data.get("text")
    target_language = input_data.get("target_language")

    if not input_text or target_language not in tgt_languages:
        return jsonify({"error": "Invalid input"}), 400

    lang_code = tgt_languages[target_language]
    model_inputs = tokenizer(input_text, return_tensors="pt")
    generated_tokens = model.generate(
        **model_inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[lang_code]
    )
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

    return jsonify({"translation": translated_text})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

