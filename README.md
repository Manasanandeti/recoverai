# RecoverAI

AI-powered Revenue Recovery System built for the Razorpay AI Buildathon.

## Problem

RecoverAI identifies failed payments and detects revenue at risk.

## Solution

The system analyzes payment failures and recommends a suitable recovery action.

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI (Python)
- Database: MySQL
- Payments: Razorpay Test Mode

## Key Features

- Failed payment detection
- Revenue at Risk calculation
- AI recovery recommendation
- Razorpay Payment Link integration
- Duplicate recovery protection
- Recovered amount tracking
- Recovery rate calculation
- Audit Trail

## Workflow

Failed Payment -> Risk Analysis -> AI Decision -> Recovery Action -> Payment -> Recovery Tracking -> Audit Trail

## Demo Result

- Test Transaction Amount: INR 500
- Recovered Amount: INR 500
- Recovery Rate: 100%

## Project Structure

RecoverAI/
- backend/
  - main.py
  - database.py
  - razorpay_service.py
- frontend/
  - index.html
- .env
- README.md

## Run Locally

```text
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload