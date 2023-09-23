import os
from flask import Flask, request
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

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
    print("Extracted Text is: ", end="\n")
    print(text)


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

    read_file(destination)

    # session["uploadFilePath"] = destination
    response = "File successfully uploaded"
    return response


if __name__ == "__main__":
    # app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", port=8000)

# flask_cors.CORS(app, expose_headers="Authorization")
