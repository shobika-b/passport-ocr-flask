from flask import Flask, request, jsonify
from passporteye import read_mrz
from datetime import datetime
import re

app = Flask(__name__)

@app.get("/")
def ping():
    return "<p>Server is up and running</p>"

# Reformat the dates to 'DD-MM-YYYY'
def reformat_date(date_str: str):
    try:
        # Convert YYMMDD to DD-MM-YYYY
        return datetime.strptime(date_str, "%y%m%d").strftime("%d-%m-%Y")
    except ValueError:
        return None  # Return None if the date is invalid
        
@app.post("/extract")
def extract_from_mrz():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    image_data = file.read()

    # Use passporteye to extract MRZ
    mrz = read_mrz(image_data)

    if mrz is None:
        return jsonify({'error': 'Could not detect MRZ'}), 400

    mrz_data = mrz.to_dict()
    
    # Reformat date_of_birth and expiration_date
    mrz_data["date_of_birth"] = reformat_date(mrz_data.get("date_of_birth", ""))
    mrz_data["expiration_date"] = reformat_date(mrz_data.get("expiration_date", ""))

    # Replace <<
    mrz_data["nationality"] = mrz_data.get("nationality").replace('<', ' ').strip()
    mrz_data["country"] = mrz_data.get("country").replace('<', ' ').strip()
    mrz_data["type"] = mrz_data.get("type").replace('<', ' ').strip()
    mrz_data["names"] = re.sub(r'[\sK]+$|\s+', '', mrz_data.get("names"))

    return jsonify({'mrz_data': mrz_data})