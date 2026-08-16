import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask("SuperKart Sales Prediction API")

# Load the trained sales prediction model (full pipeline with preprocessing)
model = joblib.load("superkart_sales_prediction_model.joblib")

# Home route
@app.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API"

# Single prediction endpoint
@app.post('/v1/predict')
def predict_sales():
    """Predict sales for a single product-store combination."""
    data = request.get_json()

    sample = {
        'Product_Weight': data['Product_Weight'],
        'Product_Sugar_Content': data['Product_Sugar_Content'],
        'Product_Allocated_Area': data['Product_Allocated_Area'],
        'Product_Type': data['Product_Type'],
        'Product_MRP': data['Product_MRP'],
        'Store_Size': data['Store_Size'],
        'Store_Location_City_Type': data['Store_Location_City_Type'],
        'Store_Type': data['Store_Type'],
        'Store_Age': data['Store_Age']
    }

    input_data = pd.DataFrame([sample])
    prediction = model.predict(input_data).tolist()[0]

    return jsonify({'Predicted_Sales': round(prediction, 2)})

# Batch prediction endpoint
@app.post('/v1/predict_batch')
def predict_sales_batch():
    """Predict sales for a batch of products from an uploaded CSV."""
    file = request.files['file']
    input_data = pd.read_csv(file)

    # Drop identifier columns if present
    cols_to_drop = [c for c in ['Product_Id', 'Store_Id', 'Store_Establishment_Year'] if c in input_data.columns]
    
    # If Store_Age is not present but Store_Establishment_Year is, create it
    if 'Store_Age' not in input_data.columns and 'Store_Establishment_Year' in input_data.columns:
        input_data['Store_Age'] = 2026 - input_data['Store_Establishment_Year']
    
    # Fix Product_Sugar_Content inconsistency
    if 'Product_Sugar_Content' in input_data.columns:
        input_data['Product_Sugar_Content'] = input_data['Product_Sugar_Content'].replace('reg', 'Regular')
    
    predict_data = input_data.drop(columns=cols_to_drop, errors='ignore')
    
    # Also drop target column if present
    if 'Product_Store_Sales_Total' in predict_data.columns:
        predict_data = predict_data.drop(columns=['Product_Store_Sales_Total'])

    predictions = model.predict(predict_data).tolist()
    predictions_rounded = [round(p, 2) for p in predictions]

    # Return predictions with product IDs if available
    if 'Product_Id' in input_data.columns:
        result = dict(zip(input_data['Product_Id'].tolist(), predictions_rounded))
    else:
        result = {'predictions': predictions_rounded}

    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
