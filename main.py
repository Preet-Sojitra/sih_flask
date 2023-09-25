import os
from flask import Flask, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging
import pdfkit
import cloudinary.uploader
from transformers import AutoTokenizer, TFAutoModelForSeq2SeqLM
from PyPDF2 import PdfReader
from gtts import gTTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HELLO WORLD")

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


with app.app_context():
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
    model = TFAutoModelForSeq2SeqLM.from_pretrained("tf_model/")


def read_file(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    print("Number of pages: ", number_of_pages)
    page = reader.pages[0]
    text = page.extract_text()
    # print("Extracted Text is: ", end="\n")
    # print(text)
    return text


def generate_translation(input_text):
    with current_app.app_context():
        tokenized = tokenizer(input_text, return_tensors="np")
        out = model.generate(**tokenized, max_length=128)
        # print(out)

        with tokenizer.as_target_tokenizer():
            output = tokenizer.decode(out[0], skip_special_tokens=True)
            # print(tokenizer.decode(out[0], skip_special_tokens=True))
            return {"Translation": output}


# def translate(text):
#     # Here we will pass to ML model

#     translated_text = generate_translation(text)
#     # For now we will return some dummy hindi paragraph
#     # translated_text = "हिंदी हमारी राष्ट्रीय भाषा है। हमारे हिंदी भाषा कौशल को सीखना और सुधारना भारत के अधिकांश स्थानों में सेवा करने के लिए बहुत महत्वपूर्ण है। स्कूली दिनों से ही हम हिंदी भाषा सीखते थे। कुछ स्कूल और कॉलेज हिंदी के अतिरिक्त बोर्ड और निबंध बोर्ड में निबंध लेखन का आयोजन करते हैं, छात्रों को बोर्ड परीक्षा में हिंदी निबंध लिखने की आवश्यकता होती है।"

#     return translated_text["Translation"]


def upload_to_cloudinary(file_path):
    cloudinary.config(
        cloud_name="deiuvjdci",
        api_key="176911155882982",
        api_secret="Zx9PINZVO99Nzp-fh11zdAOz26w",
    )

    # file_path = "./out/out.pdf"

    upload_result = cloudinary.uploader.upload(
        file_path,
        resource_type="auto",
    )
    # app.logger.info(upload_result)
    return jsonify(upload_result)


# @app.route("/upload", methods=["POST"])
def fileTranslate(file):
    # print(request.files["file"])
    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.mkdir(UPLOAD_FOLDER)
    logger.info("welcome to upload")
    # file = request.files["file"]
    # print("File is: ", file)
    filename = secure_filename(file.filename)  # type: ignore
    print("File name is: ", filename)
    destination = "/".join([UPLOAD_FOLDER, filename])
    print("File destination is: ", destination)
    file.save(destination)

    # Extract text from the pdf
    text = read_file(destination)
    # print("Text is: ", text)

    # now translate the text and generate pdf
    translated_text = generate_translation(text)
    # generate_pdf(translated_text)

    # session["uploadFilePath"] = destination
    # response = "File successfully uploaded"
    return translated_text["Translation"]


# Main route for pdf translation
@app.route("/predict-pdf", methods=["POST"])
def generate_pdf():
    print(request.files["file"])
    translated_text = fileTranslate(request.files["file"])
    print(translated_text)

    # translated_text = translate("hello")

    html_content = (
        """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            /* Specify the font for Hindi text */
            body {
            font-family: Arial, sans-serif;
            font-size: 22px;
            lang: hi;
            line-height: 1.5;
            }
        </style>
        </head>
        <body>
        <p>
        """
        + translated_text
        + """
        </p>
        </body>
        </html>
        """
    )

    options = {
        "page-size": "Letter",
        "encoding": "UTF-8",
        "no-outline": None,
    }

    pdfkit.from_string(html_content, "./out/out.pdf", options=options)

    upload_result = upload_to_cloudinary("./out/out.pdf")

    upload_data = {
        "data": upload_result.get_data(
            as_text=True
        )  # Convert binary data to a string if needed
    }

    res = {"upload_result": upload_data, "translated_text": translated_text}

    print(res)
    type(res)

    return jsonify(res)


# Main route for text translation
@app.route("/predict", methods=["POST"])
def generate():
    # print(request.data)
    # print(request.get_json())  # this has json data now
    input_text = request.get_json()
    # print(input_text.get("input"))

    translation = generate_translation(input_text.get("input"))

    # tokenized = tokenizer(input_text, return_tensors="np")
    # out = model.generate(**tokenized, max_length=128)
    # # print(out)

    # with tokenizer.as_target_tokenizer():
    #     output = tokenizer.decode(out[0], skip_special_tokens=True)
    #     print(tokenizer.decode(out[0], skip_special_tokens=True))
    #     return {"Translation": output}
    return jsonify(translation)


@app.route("/audio", methods=["POST"])
def tts():
    user_input = request.get_json()
    text = user_input.get("input")
    lang = user_input.get("lang")
    print(text, lang)

    tts = gTTS(
        text=text,
        lang=lang,
    )
    tts.save("./audio/hello.mp3")

    res = upload_to_cloudinary("./audio/hello.mp3")

    return res


if __name__ == "__main__":
    # app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", port=8000)

# flask_cors.CORS(app, expose_headers="Authorization")


# * Unwanted code as of now
# import docx
# from dotenv import load_dotenv
# from docx2pdf import convert
# import tensorflow as tf
# import numpy as np
# from fastapi import FastAPI
# from pydantic import BaseModel
# load_dotenv()

# import transformers
# print(os.getenv("CLOUD_NAME"))

# import flask_cors

# MODEL = tf.keras.models.load_model('model')

# def generate_pdf():
#     document = docx.Document()
#     document.add_paragraph(translate("dummy"))
#     document.save("test.docx")
# * In this approach docx file is generated but it is not converted to pdf. Because docx2pdf only works in Microsoft Windows
#     convert("test.docx")


# def generate_pdf():
#     pdfkit.from_string(translate("hello"), "./out/out.pdf")
#     return "PDF generated"


# for uploading to cloudinary
# @app.route("/test", methods=["GET"])
