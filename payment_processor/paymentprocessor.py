import datetime

class PaymentProcessor:
    def __init__(self, api_client):
        self.api_client = api_client
        self.currency_conversion_rate = 1.2  # magic number

    def process_payment(self, amount, currency, user_id, payment_method, metadata, discount_code, fraud_check_level):
        # Long method, too many parameters

        # 1. Validate payment method
        if payment_method == "credit_card":
            if not metadata.get("card_number") or not metadata.get("expiry"):
                raise ValueError("Invalid card metadata")
        elif payment_method == "paypal":
            if not metadata.get("paypal_account"):
                raise ValueError("Invalid PayPal metadata")
        else:
            raise ValueError("Unsupported payment method")

        # 2. Check for fraud
        if fraud_check_level > 0:
            if amount < 100:
                print("Performing light fraud check for small payment")
                self._light_fraud_check(user_id, amount)
            else:
                print("Performing heavy fraud check for large payment")
                self._heavy_fraud_check(user_id, amount)

        # 3. Apply discount
        final_amount = amount
        if discount_code:
            if discount_code == "SUMMER20":
                final_amount = amount * 0.8  # magic number
            elif discount_code == "WELCOME10":
                final_amount = amount - 10  # magic number
            else:
                print("Unknown discount code")

        # 4. Convert currency if needed
        if currency != "USD":
            final_amount = final_amount * self.currency_conversion_rate  # magic number

        # 5. Create transaction object
        transaction = {
            "user_id": user_id,
            "original_amount": amount,
            "final_amount": final_amount,
            "currency": currency,
            "payment_method": payment_method,
            "metadata": metadata,
            "discount_code": discount_code,
            "fraud_checked": fraud_check_level,
            "timestamp": datetime.datetime.now().isoformat()
        }

        # 6. Send to API
        try:
            if payment_method == "credit_card":
                self.api_client.post("/payments/credit", transaction)
            elif payment_method == "paypal":
                self.api_client.post("/payments/paypal", transaction)
            print("Payment sent to API:", transaction)
        except Exception as e:
            print("Failed to send payment:", e)
            raise e

        # 7. Send confirmation email
        self._send_confirmation_email(user_id, final_amount, currency)

        # 8. Log analytics
        self._log_analytics({
            "user_id": user_id,
            "amount": final_amount,
            "currency": currency,
            "method": payment_method
        })

        return transaction

    def _light_fraud_check(self, user_id, amount):
        print(f"Light fraud check for user {user_id} on amount {amount}")
        if amount < 10:
            print("Very low risk")
        else:
            print("Low risk")

    def _heavy_fraud_check(self, user_id, amount):
        print(f"Heavy fraud check for user {user_id} on amount {amount}")
        if amount < 1000:
            print("Medium risk")
        else:
            print("High risk")

    def _send_confirmation_email(self, user_id, amount, currency):
        print(f"Sending email to user {user_id}: Your payment of {amount} {currency} was successful.")

    def _log_analytics(self, data):
        print("Analytics event:", data)

    def refund_payment(self, transaction_id, user_id, reason, amount, currency, metadata):
        refund = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "reason": reason,
            "amount": amount,
            "currency": currency,
            "metadata": metadata,
            "date": datetime.datetime.now()
        }

        # Magic number for refund fee
        refund_fee = amount * 0.05
        refund["net_amount"] = amount - refund_fee

        # Duplicated API logic
        self.api_client.post("/payments/refund", refund)

        print("Refund processed:", refund)
        return refund