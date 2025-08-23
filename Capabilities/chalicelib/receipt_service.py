import boto3
import time
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from datetime import datetime
import calendar

class ReceiptService:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def store_receipt_data(self, file_name, receipt_name, date_of_purchase, receipt_items, total_price,created_date):
        # Convert float values in receipt_items to Decimal
        for item in receipt_items:
            if 'price' in item:
                item['price'] = Decimal(str(item['price']))

        # Convert total_price to Decimal
        total_price = Decimal(str(total_price))

        self.table.put_item(
            Item={
                'ReceiptID': str(int(time.time())),
                'FileName': file_name,
                'receiptName': receipt_name,
                'dateOfPurchase': date_of_purchase,
                'items': receipt_items,
                'TotalPrice': total_price,
                'createdDate': created_date
            }
        )

    def get_receipts_for_month(self, year, month):
        # Format start and end date properly
        start_date = f"{year}-{month.zfill(2)}-01"
        last_day = calendar.monthrange(int(year), int(month))[1]
        end_date = f"{year}-{month.zfill(2)}-{last_day:02d}"

        # Use scan with FilterExpression instead of query
        response = self.table.scan(
            FilterExpression=Attr('createdDate').between(start_date, end_date)
        )

        return response.get('Items', [])

    def get_all_receipts(self):
        """
        Fetch all receipts from the DynamoDB table without date filtering.
        """
        try:
            # Fetching all items from the table

            print("Inside get_all_receipts")

            response = self.table.scan()  # Using scan to get all records
            print("Response ", response)
            return response['Items']  # Return all items from the table

        except ClientError as e:
            print(f"Error fetching receipts: {e}")
            return None
