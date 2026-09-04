from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.database import get_db_connection
from backend.razorpay_service import create_payment_link

app = FastAPI(title="RecoverAI")
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/")
def home():
    return {
        "message": "RecoverAI Backend is running!",
        "status": "success"
    }


@app.get("/db-test")
def database_test():
    try:
        connection = get_db_connection()

        if connection.is_connected():
            connection.close()

            return {
                "status": "success",
                "message": "MySQL connection successful!"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/create-payment-link")
def payment_link():
    try:
        payment_link = create_payment_link(
            500,
            "RecoverAI Payment Recovery"
        )

        return {
            "status": "success",
            "payment_link": payment_link["short_url"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.post("/customers")
def create_customer(name: str, email: str, phone: str = None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO customers (name, email, phone)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, email, phone))
        connection.commit()

        customer_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "customer_id": customer_id,
            "message": "Customer created successfully!"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.post("/transactions")
def create_transaction(
    customer_id: int,
    amount: float,
    payment_method: str,
    status: str,
    failure_reason: str = None
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO transactions
        (customer_id, amount, payment_method, status, failure_reason)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (customer_id, amount, payment_method, status, failure_reason)
        )

        connection.commit()

        transaction_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": "Transaction created successfully!"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.post("/analyze")
def analyze_transaction(transaction_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get transaction details
        query = """
        SELECT id, amount, payment_method, status, failure_reason
        FROM transactions
        WHERE id = %s
        """

        cursor.execute(query, (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            cursor.close()
            connection.close()

            return {
                "status": "error",
                "message": "Transaction not found"
            }

        amount = float(transaction["amount"])
        failure_reason = transaction["failure_reason"]

        # AI Decision Engine
        if failure_reason and "insufficient" in failure_reason.lower():
            recoverable = True
            priority = "HIGH"
            reason = "Payment failed due to insufficient balance"
            recommended_action = "PAYMENT_LINK"
            expected_recovery = amount

        elif failure_reason and "network" in failure_reason.lower():
            recoverable = True
            priority = "MEDIUM"
            reason = "Temporary network-related payment failure"
            recommended_action = "RETRY"
            expected_recovery = amount

        else:
            recoverable = True
            priority = "MEDIUM"
            reason = "Payment failure may be recoverable"
            recommended_action = "PAYMENT_LINK"
            expected_recovery = amount

        # Save AI decision
        insert_query = """
        INSERT INTO ai_decisions
        (transaction_id, recoverable, priority, reason,
         recommended_action, expected_recovery)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                transaction_id,
                recoverable,
                priority,
                reason,
                recommended_action,
                expected_recovery
            )
        )

        connection.commit()

        decision_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "decision_id": decision_id,
            "transaction_id": transaction_id,
            "recoverable": recoverable,
            "priority": priority,
            "reason": reason,
            "recommended_action": recommended_action,
            "expected_recovery": expected_recovery
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }  
@app.post("/recover")
def recover_transaction(transaction_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get AI decision
        query = """
        SELECT *
        FROM ai_decisions
        WHERE transaction_id = %s
        ORDER BY id DESC
        LIMIT 1
        """

        cursor.execute(query, (transaction_id,))
        decision = cursor.fetchone()

        if not decision:
            cursor.close()
            connection.close()

            return {
                "status": "error",
                "message": "AI decision not found. Analyze transaction first."
            }
        # Check if recovery was already executed
        cursor.execute("""
            SELECT COUNT(*) AS recovery_count
            FROM recovery_actions
            WHERE transaction_id = %s
        """, (transaction_id,))

        recovery_check = cursor.fetchone()
        print("RECOVERY CHECK:", recovery_check)

        if recovery_check["recovery_count"] > 0:
            cursor.close()
            connection.close()

            return {
                "status": "error",
                "transaction_id": transaction_id,
                "message": "Transaction already recovered."
            }
        # Execute recommended action
        if decision["recommended_action"] == "PAYMENT_LINK":

            payment_link = create_payment_link(
                500,
                "RecoverAI Payment Recovery"
            )

            action_query = """
            INSERT INTO recovery_actions
            (transaction_id, action_type, status, payment_link)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                action_query,
                (
                    transaction_id,
                    "PAYMENT_LINK",
                    "SENT",
                    payment_link["short_url"]
                )
            )
            # Save audit log
            audit_query = """
            INSERT INTO audit_logs
            (transaction_id, action, details)
            VALUES (%s, %s, %s)
            """

            cursor.execute(
                audit_query,
                (
                    transaction_id,
                    "PAYMENT_LINK",
                    "Recovery payment link created and sent"
                )
            )

            connection.commit()

            action_id = cursor.lastrowid

            cursor.close()
            connection.close()

            return {
                "status": "success",
                "action_id": action_id,
                "transaction_id": transaction_id,
                "action": "PAYMENT_LINK",
                "payment_link": payment_link["short_url"],
                "message": "Recovery action executed successfully!"
            }

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "action": decision["recommended_action"],
            "message": "Recovery action processed"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
@app.get("/audit-logs")
def get_audit_logs():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            id,
            transaction_id,
            action,
            details,
            created_at
        FROM audit_logs
        ORDER BY id DESC
        """

        cursor.execute(query)
        logs = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "total_logs": len(logs),
            "logs": logs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        } 
@app.get("/dashboard")
def dashboard():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Total failed transaction amount
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS revenue_at_risk
            FROM transactions
            WHERE status = 'FAILED'
        """)
        revenue_at_risk = cursor.fetchone()["revenue_at_risk"]

        # Total recovered amount
        cursor.execute("""
            SELECT COALESCE(SUM(recovered_amount), 0) AS recovered
            FROM recovery_actions
        """)
        recovered = cursor.fetchone()["recovered"]

        # Failed payments count
        cursor.execute("""
            SELECT COUNT(*) AS failed_payments
            FROM transactions
            WHERE status = 'FAILED'
        """)
        failed_payments = cursor.fetchone()["failed_payments"]

        # AI decisions count
        cursor.execute("""
            SELECT COUNT(*) AS ai_decisions
            FROM ai_decisions
        """)
        ai_decisions = cursor.fetchone()["ai_decisions"]

        # Recovery rate
        if revenue_at_risk > 0:
            recovery_rate = round(
                (float(recovered) / float(revenue_at_risk)) * 100, 2
            )
        else:
            recovery_rate = 0

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "revenue_at_risk": float(revenue_at_risk),
            "recovered": float(recovered),
            "failed_payments": failed_payments,
            "ai_decisions": ai_decisions,
            "recovery_rate": recovery_rate
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
