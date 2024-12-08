from flask import Flask, render_template, request, send_file
import matplotlib.pyplot as plt
import pickle
from fpdf import FPDF
import os

app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

@app.route("/")
def home():
    return render_template("web.html")

@app.route("/predict", methods=["POST"])
def predict():
    input_data = {
        "Name of the Patient": request.form["name"],
        "Specific Gravity": request.form["sg"],
        "Serum Creatinine": request.form["sc"],
        "Hemoglobin": request.form["hg"],
        "Red Blood Cell Count": request.form["rbcc"],
        "Hypertension": request.form["ht"],
    }
    feature_values = [
    float(input_data["Specific Gravity"]),
    float(input_data["Serum Creatinine"]),
    float(input_data["Hemoglobin"]),
    float(input_data["Red Blood Cell Count"]),
    float(input_data["Hypertension"]),
    ]
    print("Feature values for prediction:", feature_values)
    #feature_values = [float(x) for x in feature_values.values()]
    scaled_features = scaler.transform([feature_values])

    prediction = model.predict(scaled_features)[0]

    input_data["Prediction"] = "CKD" if prediction == 1 else "Not CKD"
    print("Input data with prediction:", input_data)

    pdf_filename = generate_pdf(input_data, scaled_features)
    return send_file(pdf_filename, as_attachment=True)

def create_combined_histogram_scaled(features, scaled_values):
    plt.figure(figsize=(8,6))
    plt.bar(features, scaled_values[0], color='blue', alpha=0.7, edgecolor='black')
    plt.title("Proportion of the Features")
    plt.xlabel("Features")
    plt.ylabel("Scaled Values")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle="--", alpha=0.5)

    image_filename = "scaled_features.png"
    plt.tight_layout()
    plt.savefig(image_filename)
    plt.close()
    return image_filename


def generate_pdf(data, scaled_features):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 128)
    pdf.cell(200, 10, txt="Chronic Kidney Disease Prediction Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align="L")
        pdf.ln(1)

    feature_names = list(data.keys())[1:-1]
    image_file = create_combined_histogram_scaled(feature_names, scaled_features)

    pdf.image(image_file, x=10, y=120, w=190)
    pdf.ln(2)

    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(200, 10, txt="Generated by Chronic Kidney Disease Prediction System", ln=True, align="C")

    pdf_filename = "CKD_Prediction_Report.pdf"
    pdf.output(pdf_filename)
    os.remove(image_file)
    return pdf_filename

if __name__ == "__main__":
    app.run(debug=True)