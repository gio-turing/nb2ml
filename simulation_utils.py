"""
Simulation utilities for generating Stripe-like data

This module provides utilities to simulate Stripe's behavior without
calling their actual API, including ID generation and timestamp management.
"""

import time
import random
import string
from typing import Optional


class StripeIDGenerator:
    """Generates Stripe-like IDs for various resource types"""

    # Stripe ID prefixes for different resource types
    PREFIXES = {
        'account': 'acct_',
        'balance_transaction': 'txn_',
        'charge': 'ch_',
        'coupon': 'coupon_',
        'customer': 'cus_',
        'dispute': 'dp_',
        'invoice': 'in_',
        'invoice_item': 'ii_',
        'payment_intent': 'pi_',
        'payment_link': 'plink_',
        'payout': 'po_',
        'price': 'price_',
        'product': 'prod_',
        'refund': 're_',
        'subscription': 'sub_',
        'subscription_item': 'si_',
    }

    @classmethod
    def generate(cls, resource_type: str, length: int = 24) -> str:
        """
        Generate a Stripe-like ID for a given resource type

        Args:
            resource_type: Type of resource (e.g., 'customer', 'invoice')
            length: Length of random string after prefix (default 24)

        Returns:
            Generated ID string (e.g., 'cus_1a2b3c4d5e6f7g8h')
        """
        prefix = cls.PREFIXES.get(resource_type, f'{resource_type}_')
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return f"{prefix}{random_str}"

    @classmethod
    def customer(cls) -> str:
        """Generate customer ID"""
        return cls.generate('customer')

    @classmethod
    def invoice(cls) -> str:
        """Generate invoice ID"""
        return cls.generate('invoice')

    @classmethod
    def invoice_item(cls) -> str:
        """Generate invoice item ID"""
        return cls.generate('invoice_item')

    @classmethod
    def subscription(cls) -> str:
        """Generate subscription ID"""
        return cls.generate('subscription')

    @classmethod
    def product(cls) -> str:
        """Generate product ID"""
        return cls.generate('product')

    @classmethod
    def price(cls) -> str:
        """Generate price ID"""
        return cls.generate('price')

    @classmethod
    def coupon(cls) -> str:
        """Generate coupon ID"""
        return cls.generate('coupon')

    @classmethod
    def payment_intent(cls) -> str:
        """Generate payment intent ID"""
        return cls.generate('payment_intent')

    @classmethod
    def payment_link(cls) -> str:
        """Generate payment link ID"""
        return cls.generate('payment_link')

    @classmethod
    def refund(cls) -> str:
        """Generate refund ID"""
        return cls.generate('refund')

    @classmethod
    def dispute(cls) -> str:
        """Generate dispute ID"""
        return cls.generate('dispute')


def current_timestamp() -> int:
    """
    Get current Unix timestamp (seconds since epoch)

    Returns:
        Current Unix timestamp as integer
    """
    return int(time.time())


def simulate_api_delay(min_ms: int = 50, max_ms: int = 200) -> None:
    """
    Simulate API network delay

    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    delay = random.uniform(min_ms, max_ms) / 1000.0
    time.sleep(delay)


def calculate_invoice_total(
    subtotal: int,
    tax: Optional[int] = None,
    discount: Optional[int] = None
) -> int:
    """
    Calculate invoice total amount

    Args:
        subtotal: Subtotal amount in cents
        tax: Tax amount in cents (optional)
        discount: Discount amount in cents (optional)

    Returns:
        Total amount in cents
    """
    total = subtotal
    if tax:
        total += tax
    if discount:
        total -= discount
    return max(0, total)


def apply_coupon_discount(
    amount: int,
    coupon_percent_off: Optional[float] = None,
    coupon_amount_off: Optional[int] = None
) -> int:
    """
    Apply coupon discount to an amount

    Args:
        amount: Original amount in cents
        coupon_percent_off: Percentage discount (0-100)
        coupon_amount_off: Fixed discount amount in cents

    Returns:
        Discounted amount in cents
    """
    if coupon_percent_off:
        discount = int(amount * (coupon_percent_off / 100))
        return max(0, amount - discount)
    elif coupon_amount_off:
        return max(0, amount - coupon_amount_off)
    return amount
