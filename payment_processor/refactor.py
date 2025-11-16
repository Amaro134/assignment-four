import datetime

# All magic numbers in one place
DISCOUNTS = {
    "SUMMER20": 0.20,
    "WELCOME10": 10
}

CURRENCY_RATES = {
    "USD": 1,
    "EUR": 1.2
}

REFUND_FEE_RATE = 0.05


class PaymentProcessor:
    def __init__(self, api_client):
        self.api_client = api_client


    def _validate_metadata(self, method, metadata):
        if method == "credit_card":
            if not metadata.get("card_number") or not metadata.get("expiry"):
                raise ValueError("Invalid card metadata")

        elif method == "paypal":
            if not metadata.get("paypal_account"):
                raise ValueError("Invalid PayPal metadata")

        else:
            raise ValueError("Unsupported payment method")

    def _apply_discount(self, amount, discount_code):
        if not discount_code:
            return amount

        if discount_code == "SUMMER20":
            return amount * (1 - DISCOUNTS["SUMMER20"])

        if discount_code == "WELCOME10":
            return amount - DISCOUNTS["WELCOME10"]

        print("Unknown discount code")
        return amount

    def _convert_currency(self, amount, currency):
        rate = CURRENCY_RATES.get(currency, 1)
        return amount * rate

    def _fraud_check(self, amount, user_id, level):
        if level == 0:
            return

        if amount < 100:
            print("Light fraud check")
            print(f"Checking {user_id} for small amount {amount}")
        else:
            print("Heavy fraud check")
            print(f"Checking {user_id} for large amount {amount}")

    def _send_api_payment(self, method, data):
        endpoint = "/payments/" + method
        self.api_client.post(endpoint, data)

    def _send_confirmation_email(self, user_id, amount, currency):
        print(f"Email to {user_id}: You paid {amount} {currency}")

    def _log(self, data):
        print("Analytics:", data)


# making the payment
    def process_payment(self, amount, currency, user_id, payment_method, metadata, discount_code, fraud_check_level):

        self._validate_metadata(payment_method, metadata)
        self._fraud_check(amount, user_id, fraud_check_level)

        final_amount = self._apply_discount(amount, discount_code)
        final_amount = self._convert_currency(final_amount, currency)

        # Creating a  transaction
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

        self._send_api_payment(payment_method, transaction)
        self._send_confirmation_email(user_id, final_amount, currency)
        self._log({
            "user_id": user_id,
            "amount": final_amount,
            "currency": currency,
            "method": payment_method
        })

        return transaction
# the refunding method
    def refund_payment(self, transaction_id, user_id, reason, amount, currency, metadata):

        refund_fee = amount * REFUND_FEE_RATE
        net_amount = amount - refund_fee

        refund = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "reason": reason,
            "amount": amount,
            "currency": currency,
            "metadata": metadata,
            "net_amount": net_amount,
            "date": datetime.datetime.now()
        }

        self.api_client.post("/payments/refund", refund)

        print("Refund processed:", refund)
        return refund
