import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)


def create_payment_link(amount, description):
    payment_link = client.payment_link.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "description": description
    })

    return payment_link