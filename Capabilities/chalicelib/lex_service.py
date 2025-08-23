# chalicelib/lex_service.py

import calendar
from chalicelib.receipt_service import ReceiptService

receipt_service = ReceiptService("ReceiptData")

def build_lex_response(message, intent):
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": message
            }
        }
    }

def handle_intent(intent_name, slots):
    if intent_name == "GetMonthlyExpense":
        return handle_monthly_expense(slots)
    elif intent_name == "GetCategoryExpense":
        return handle_category_expense(slots)
    elif intent_name == "GetTotalExpenseSummary":
        return handle_total_expense(slots)
    elif intent_name == "HelpIntent":
        return build_lex_response(
            "You can ask:\n• What did I spend in March 2025?\n• Grocery expense for April 2024\n• Total spent so far.",
            intent_name
        )
    else:
        return build_lex_response(f"Unknown intent: {intent_name}", intent_name)

def handle_monthly_expense(slots):
    month = slots.get("month")
    year = slots.get("year")
    try:
        month_num = str(list(calendar.month_name).index(month)).zfill(2)
        receipts = receipt_service.get_receipts_for_month(year, month_num)
        total = sum(float(r.get("TotalPrice", 0)) for r in receipts)
        return build_lex_response(f"You spent ${total:.2f} in {month} {year}.", "GetMonthlyExpense")
    except Exception as e:
        return build_lex_response(f"Error: {str(e)}", "GetMonthlyExpense")

def handle_category_expense(slots):
    month = slots.get("month")
    year = slots.get("year")
    category = slots.get("category")
    try:
        month_num = str(list(calendar.month_name).index(month)).zfill(2)
        receipts = receipt_service.get_receipts_for_month(year, month_num)
        total = 0.0
        for r in receipts:
            for item in r.get("items", []):
                if item.get("category", "").lower() == category.lower():
                    total += float(item.get("price", 0))
        return build_lex_response(f"You spent ${total:.2f} on {category} in {month} {year}.", "GetCategoryExpense")
    except Exception as e:
        return build_lex_response(f"Error: {str(e)}", "GetCategoryExpense")

def handle_total_expense(slots):
    try:
        receipts = receipt_service.get_all_receipts()
        total = sum(float(r.get("TotalPrice", 0)) for r in receipts)
        return build_lex_response(f"Your total spend so far is ${total:.2f}.", "GetTotalExpenseSummary")
    except Exception as e:
        return build_lex_response(f"Error: {str(e)}", "GetTotalExpenseSummary")
