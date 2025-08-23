from chalice import Chalice, CORSConfig, Response
from chalicelib.receipt_service import ReceiptService
from chalicelib.storage_service import StorageService
from chalicelib.textract_service import TextractService
from chalicelib.lex_service import handle_intent
import mimetypes


import os
import base64
import json
from datetime import datetime
from decimal import Decimal

# Enable CORS for local frontend
cors_config = CORSConfig(
    allow_origin='*',
    allow_headers=['Content-Type', 'filename'],
    max_age=600,
    expose_headers=['Content-Type'],
    allow_credentials=True
)

app = Chalice(app_name='ExpenseBudgetAssistant')
app.debug = True

# Services
receipt_service = ReceiptService('ReceiptData')
storage_service = StorageService('expense-tracker-301380198')
textract_service = TextractService('AIzaSyBfXHGv_LCiLZSX9GMfjqulk10WTBV5DdA')



# Go one directory up from Capabilities and into Website
STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Website'))

@app.route('/', methods=['GET'], cors=cors_config)
def index():
    try:
        with open(os.path.join(STATIC_PATH, 'index.html'), 'r') as f:
            html_content = f.read()

        return Response(
            body=html_content,
            status_code=200,
            headers={'Content-Type': 'text/html'}
        )
    except Exception as e:
        return Response(
            body=f"<h1>Error loading page</h1><p>{str(e)}</p>",
            status_code=500,
            headers={'Content-Type': 'text/html'}
        )

@app.route('/upload', methods=['POST'], cors=cors_config)
def upload_receipt():
    try:
        request_data = json.loads(app.current_request.raw_body)
        file_name = request_data['filename']
        file_bytes = base64.b64decode(request_data['filebytes'])

        # Step 1: Upload to S3
        upload_response = storage_service.upload_file(file_bytes, file_name)

        # Step 2: Extract grocery-related items and prices with Textract
        receipt_items, total_price, date_of_purchase, receipt_name = textract_service.extract_receipt_data(file_bytes)

        # If no items found or empty text extracted, raise error
        if not receipt_items or not receipt_name:
            raise ValueError("No valid text or items found in the receipt. Please upload a clear image.")

        # Step 3: Get the current date and time as the created_date
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Step 4: Store extracted data in DynamoDB
        receipt_service.store_receipt_data(file_name, receipt_name, date_of_purchase, receipt_items, total_price, created_date)

        return {
            "upload": upload_response,
            "receipt_name": receipt_name,
            "date_of_purchase": date_of_purchase,
            "created_date": created_date,
            "receipt_items": receipt_items,
            "total_price": total_price
        }

    except Exception as e:
        return Response(
            body=json.dumps({"error": str(e)}),
            status_code=400,
            headers={'Content-Type': 'application/json'}
        )


# Helper function to handle Decimal conversion
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

@app.route('/receipts', methods=['GET'], cors=cors_config)
def get_all_receipts():
    try:
        # Fetch all receipts
        receipts = receipt_service.get_all_receipts()

        print("Receipts", receipts)
        if receipts:
            # Return the receipts as JSON after converting Decimal values
            return Response(
                body=json.dumps(receipts, default=decimal_default),
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        else:
            return Response(
                body=json.dumps({"message": "No receipts found."}),
                status_code=404,
                headers={'Content-Type': 'application/json'}
            )
    except Exception as e:
        return Response(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )


# Serve static files like style.css, main.js
@app.route('/static/{filename}', methods=['GET'], cors=True)
def serve_static(filename):
    file_path = os.path.join('Website/static', filename)
    if not os.path.exists(file_path):
        return Response(body='Not Found', status_code=404)

    content_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, 'rb') as f:
        return Response(body=f.read(), status_code=200, headers={
            'Content-Type': content_type or 'application/octet-stream'
        })

@app.route('/receipts/{year}/{month}', methods=['GET'], cors=cors_config)
def get_receipts_for_month(year, month):
    try:
        receipts = receipt_service.get_receipts_for_month(year, month)
        if receipts:
            return Response(
                body=json.dumps(receipts, default=decimal_default),
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        else:
            return Response(
                body=json.dumps([]),
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
    except Exception as e:
        return Response(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )

@app.route('/lex/expense', methods=['POST'], cors=cors_config)
def handle_lex_expense():
    try:
        payload = app.current_request.json_body
        intent_name = payload["currentIntent"]["name"]
        slots = payload["currentIntent"].get("slots", {})
        return handle_intent(intent_name, slots)
    except Exception as e:
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": f"Error: {str(e)}"
                }
            }
        }

# @app.route('/forecast/{category}', methods=['GET'], cors=cors_config)
# def get_forecast(category):
#     try:
#         predicted_value = forecast_service.predict_next_month(category.lower())
#         if predicted_value is not None:
#             return Response(
#                 body=json.dumps({'predicted_value': predicted_value}),
#                 status_code=200,
#                 headers={'Content-Type': 'application/json'}
#             )
#         else:
#             return Response(
#                 body=json.dumps({'message': 'No forecast data available for this category'}),
#                 status_code=404,
#                 headers={'Content-Type': 'application/json'}
#             )
#     except Exception as e:
#         return Response(
#             body=json.dumps({'error': str(e)}),
#             status_code=500,
#             headers={'Content-Type': 'application/json'}
#         )




