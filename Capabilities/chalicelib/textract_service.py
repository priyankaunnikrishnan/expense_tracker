import boto3
import google.generativeai as genai
import logging
import os
import re
import json


class TextractService:
    def __init__(self, gemini_api_key):
        # Set up Gemini API key
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        self.textract_client = boto3.client('textract')
        self.logger = logging.getLogger(__name__)

        # Configure the Gemini model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 20000,
                "response_mime_type": "text/plain",
            },
        )

    def extract_receipt_data(self, file_bytes):
        response = self.textract_client.analyze_document(
            Document={'Bytes': file_bytes},
            FeatureTypes=['FORMS']
        )

        lines = [
            block['Text'] for block in response['Blocks']
            if block['BlockType'] == 'LINE'
        ]

        self.logger.info("Extracted Lines: %s", lines)

        # Send the extracted lines to Gemini for parsing
        receipt_items, total_price, date_of_purchase, receipt_name = self.extract_with_gemini(lines)

        return receipt_items, total_price, date_of_purchase, receipt_name

    def extract_with_gemini(self, lines):
        prompt = (
                "Given the following receipt lines, extract the name of the store (as 'receiptName'), "
                "the date of purchase, categorize the items based on predefined categories, and extract the items with their price and total price. "
                "The categories are: Grocery, Transport, Food, Household, Apparel, Cosmetics, Health, Education, Gift, Electronics, Other, Automobile. "
                "Output should be in strict JSON format as: "
                "{\"receiptName\": \"Store Name\", \"items\": [{\"item\": \"Item Name\", \"price\": 0.00, \"category\": \"Category\"}], \"total\": 0.00, \"date\": \"DD-MM-YYYY\"} "
                "Receipt lines:\n" + "\n".join(lines)
        )

        try:
            # Request content from Gemini model
            response = self.model.generate_content(prompt)

            if hasattr(response, "text"):
                text = response.text.strip()
            else:
                self.logger.error("Error: No response text received from Gemini")
                return [], 0.0, None

            # Extract JSON from the response
            json_start = text.find('[')
            json_end = text.rfind(']') + 1
            items_json = text[json_start:json_end]
            items = json.loads(items_json)

            print("Text", text)

            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            receipt_json = text[json_start:json_end]


            receipt_content = json.loads(receipt_json)

            print("receipt_content",receipt_content)

            # # Extract total from the rest of the text
            # total_match = re.search(r'total\s*[:=]?\s*(\d+\.\d{2})', text, re.IGNORECASE)
            # total_price = float(total_match.group(1)) if total_match else sum(item['price'] for item in items)
            #
            # # Extract the date of purchase
            # date_match = re.search(r'(?:date|purchase)\s*[:=]?\s*(\d{2}-\d{2}-\d{4})', text, re.IGNORECASE)
            # date_of_purchase = date_match.group(1) if date_match else None

            receipt_name = receipt_content.get('receiptName', 'Unknown')
            total_price = receipt_content.get('total', 0.0)
            date_of_purchase = receipt_content.get('date', None)

            return items, round(total_price, 2), date_of_purchase, receipt_name

        except Exception as e:
            self.logger.error("Error processing with Gemini: %s", e)
            return [], 0.0, None
