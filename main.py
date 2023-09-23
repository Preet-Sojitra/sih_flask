# import os
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging
import pdfkit

# import docx
# from docx2pdf import convert


# import flask_cors
from PyPDF2 import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HELLO WORLD")

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def read_file(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    print("Number of pages: ", number_of_pages)
    page = reader.pages[0]
    text = page.extract_text()
    # print("Extracted Text is: ", end="\n")
    # print(text)


def translate(text):
    # Here we will pass to ML model

    # For now we will return some dummy hindi paragraph
    translated_text = "हिंदी हमारी राष्ट्रीय भाषा है। हमारे हिंदी भाषा कौशल को सीखना और सुधारना भारत के अधिकांश स्थानों में सेवा करने के लिए बहुत महत्वपूर्ण है। स्कूली दिनों से ही हम हिंदी भाषा सीखते थे। कुछ स्कूल और कॉलेज हिंदी के अतिरिक्त बोर्ड और निबंध बोर्ड में निबंध लेखन का आयोजन करते हैं, छात्रों को बोर्ड परीक्षा में हिंदी निबंध लिखने की आवश्यकता होती है।"

    return translated_text


# def generate_pdf():
#     pdfkit.from_string(translate("hello"), "./out/out.pdf")
#     return "PDF generated"


@app.route("/")
def generate_pdf():
    translated_text = translate("hello")

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
    return "PDF generated"


# def generate_pdf():
#     document = docx.Document()
#     document.add_paragraph(translate("dummy"))
#     document.save("test.docx")
# * In this approach docx file is generated but it is not converted to pdf. Because docx2pdf only works in Microsoft Windows
#     convert("test.docx")


@app.route("/upload", methods=["POST"])
def fileUpload():
    # print(request.files["file"])
    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.mkdir(UPLOAD_FOLDER)
    logger.info("welcome to upload")
    file = request.files["file"]
    # print("File is: ", file)
    filename = secure_filename(file.filename)  # type: ignore
    print("File name is: ", filename)
    destination = "/".join([UPLOAD_FOLDER, filename])
    print("File destination is: ", destination)
    file.save(destination)

    text = read_file(destination)

    # now translate the text and generate pdf
    translated_text = translate(text)
    # generate_pdf(translated_text)

    # session["uploadFilePath"] = destination
    response = "File successfully uploaded"
    return response


if __name__ == "__main__":
    # app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", port=8000)

# flask_cors.CORS(app, expose_headers="Authorization")
