# AI Expense & Budgeting Assistant 💰📊

![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Serverless](https://img.shields.io/badge/Serverless-FD5750?style=for-the-badge&logo=serverless&logoColor=white)

**Cloud Personal Finance • AWS • OCR • Serverless**

## 📖 Overview

The **AI Expense & Budgeting Assistant** is a cloud-native application designed to automate personal finance management. It leverages the power of AWS serverless architecture to scan receipts, classify spending using Large Language Models (LLMs), and provide an interactive chatbot interface for querying financial data.

By combining **OCR (Optical Character Recognition)** with **Generative AI**, this tool eliminates manual data entry and provides real-time insights into your financial health.

## ✨ Key Features

- **🧾 Receipt Scanning & OCR**: Automatically extracts transaction details from receipt images using **Amazon Textract**.
- **🧠 LLM-Based Categorization**: Uses advanced Large Language Models to intelligently classify expenses into categories (e.g., Food, Transport, Utilities) with high accuracy.
- **💬 AI Chatbot**: Integrated **Amazon Lex** chatbot allows users to ask questions like *"How much did I spend on coffee last month?"* or *"What is my remaining budget?"*.
- **📊 Real-time Dashboard**: Visualizes spending habits and budget tracking in real-time.
- **☁️ Fully Serverless**: Built entirely on AWS Serverless architecture for scalability and cost-efficiency.

## 🛠️ Tech Stack & Architecture

This project is built using a modern, event-driven serverless architecture on AWS.

| Category | Technologies |
|----------|--------------|
| **Backend Framework** | AWS Chalice (Python Serverless Microframework) |
| **Compute** | AWS Lambda |
| **Storage & Database** | Amazon S3 (Receipts), Amazon DynamoDB (Transaction Data) |
| **AI & ML** | Amazon Textract (OCR), Amazon Lex (Chatbot), LLMs (Categorization) |
| **Frontend** | React Native, JavaScript |
| **Infrastructure** | API Gateway |

## 🚀 How It Works

1.  **Upload**: User uploads a receipt image via the mobile app.
2.  **Trigger**: The upload to S3 triggers a Lambda function.
3.  **Process**:
    *   **Textract** extracts text from the receipt.
    *   **LLM** analyzes the text to identify vendor, date, and total amount, and assigns a category.
4.  **Store**: Structured data is saved to **DynamoDB**.
5.  **Interact**: Users can view the dashboard or chat with the bot (via Lex) to query their data.

## 📦 Installation & Setup

*(Note: Detailed setup instructions to be added based on specific deployment steps)*

### Prerequisites
*   AWS Account with appropriate permissions
*   Python 3.8+
*   Node.js & npm
*   AWS CLI configured

### Backend Deployment
```bash
cd backend
pip install -r requirements.txt
chalice deploy
```

### Frontend Run
```bash
cd frontend
npm install
npm run start
```

## 🔮 Future Enhancements
*   Multi-currency support.
*   Integration with bank APIs (Plaid).
*   Advanced budget forecasting using ML.

---
*Built with ❤️ by [Priyanka Unnikrishnan](https://github.com/priyankaunnikrishnan)*
