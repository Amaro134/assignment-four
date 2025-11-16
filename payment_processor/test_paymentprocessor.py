import unittest
from unittest.mock import Mock
from paymentprocessor import PaymentProcessor

class TestPaymentProcessor(unittest.TestCase):
    def setUp(self):
        self.api_client = Mock()
        self.processor = PaymentProcessor(self.api_client)
    
    def test_valid_credit_card_payment(self):
        # checking for valid credit card payment
        transaction = self.processor.process_payment(
            amount=100,
            currency="USD",
            user_id=1,
            payment_method="credit_card",
            metadata={"card_number": "1234", "expiry": "12/25"},
            discount_code=None,
            fraud_check_level=0
        )
        
        # Checking if the final amount stays the same
        self.assertEqual(transaction["final_amount"], 100)
        self.api_client.post.assert_called_once_with("/payments/credit", transaction)

    def test_invalid_credit_card_metadata(self):
        with self.assertRaises(ValueError):
            self.processor.process_payment(
                50, "USD", 1, "credit_card", {"expiry": "12/25"}, None, 0
            )

    def test_discount_applied(self):
        transaction = self.processor.process_payment(
            100, "USD", 1, "credit_card", {"card_number": "1234", "expiry": "12/25"}, "SUMMER20", 0
        )
        self.assertEqual(transaction["final_amount"], 80)

    def test_currency_conversion(self):
        transaction = self.processor.process_payment(
            100, "EUR", 1, "credit_card", {"card_number": "1234", "expiry": "12/25"}, None, 0
        )
        self.assertEqual(transaction["final_amount"], 120)

    def test_refund_payment(self):
        #this is the refund fee and it is 5%
        refund = self.processor.refund_payment("TXN123", 1, "Test refund", 100, "USD", {})
        self.assertEqual(refund["net_amount"], 95)
        self.api_client.post.assert_called_once_with("/payments/refund", refund)

if __name__ == '__main__':
    unittest.main()
