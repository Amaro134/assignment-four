import datetime

USD = "USD"
DISCOUNTS = {
    "SUMMER20": 0.20,
    "WELCOME10": 10,
}
REFUND_FEE_RATE = 0.05
CURRENCY_CONVERSION_RATE = 1.2


class PaymentDetails:
    def __init__(self, amount, currency, user_id, method, metadata, discount=None, fraud_level=0):
        self.amount = amount
        self.currency = currency
        self.user_id = user_id
        self.method = method
        self.metadata = metadata
        self.discount = discount
        self.fraud_level = fraud_level


class PaymentProcessor:
    def __init__(self, api_client):
        self.api_client = api_client

    def process_payment(self, payment: PaymentDetails):
        self._validate_payment_method(payment.method, payment.metadata)
        self._run_fraud_check(payment)
        
        final_amount = self._apply_discount(payment.amount, payment.discount)
        final_amount = self._convert_currency(final_amount, payment.currency)

        transaction = self._build_transaction(payment, final_amount)
        self._send_to_api(payment.method, transaction)
        self._send_email(payment.user_id, final_amount, payment.currency)
        self._log_analytics(payment.user_id, final_amount, payment.currency, payment.method)

        return transaction

    def refund_payment(self, transaction_id, user_id, reason, amount, currency, metadata):
        refund_fee = amount * REFUND_FEE_RATE
        refund = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "reason": reason,
            "amount": amount,
            "net_amount": amount - refund_fee,
            "currency": currency,
            "metadata": metadata,
            "date": datetime.datetime.now().isoformat()
        }
        self.api_client.post("/payments/refund", refund)
        return refund

    def _validate_payment_method(self, method, metadata):
        if method == "credit_card":
            if not metadata.get("card_number") or not metadata.get("expiry"):
                raise ValueError("Invalid card metadata")
        elif method == "paypal":
            if not metadata.get("paypal_account"):
                raise ValueError("Invalid PayPal metadata")
        else:
            raise ValueError("Unsupported payment method")

    def _run_fraud_check(self, payment):
        if payment.fraud_level > 0:
            if payment.amount < 100:
                self._light_fraud_check(payment.user_id, payment.amount)
            else:
                self._heavy_fraud_check(payment.user_id, payment.amount)

    def _apply_discount(self, amount, discount_code):
        if discount_code:
            if discount_code in DISCOUNTS:
                discount_value = DISCOUNTS[discount_code]
                return amount * (1 - discount_value) if discount_value < 1 else amount - discount_value
            else:
                print(f"Unknown discount code: {discount_code}")
        return amount

    def _convert_currency(self, amount, currency):
        return amount * CURRENCY_CONVERSION_RATE if currency != USD else amount

    def _build_transaction(self, payment, final_amount):
        return {
            "user_id": payment.user_id,
            "original_amount": payment.amount,
            "final_amount": final_amount,
            "currency": payment.currency,
            "payment_method": payment.method,
            "metadata": payment.metadata,
            "discount_code": payment.discount,
            "fraud_checked": payment.fraud_level,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def _send_to_api(self, method, transaction):
        endpoint = f"/payments/{method.replace('_', '')}"
        self.api_client.post(endpoint, transaction)

    def _send_email(self, user_id, amount, currency):
        print(f"Email to user {user_id}: Payment of {amount} {currency} successful.")

    def _log_analytics(self, user_id, amount, currency, method):
        print(f"Analytics event: {user_id} paid {amount} {currency} via {method}")

    def _light_fraud_check(self, user_id, amount):
        print(f"Light fraud check for user {user_id}, amount: {amount}")

    def _heavy_fraud_check(self, user_id, amount):
        print(f"Heavy fraud check for user {user_id}, amount: {amount}")
