"""
Entity models for Stripe resources
These models represent the actual Stripe objects/entities
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ==================== Common Entity Models ====================

class Address(BaseModel):
    """Address entity"""
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(extra='allow')


class Metadata(BaseModel):
    """Metadata dictionary"""
    model_config = ConfigDict(extra='allow')


# ==================== Account Entity ====================

class AccountEntity(BaseModel):
    """Stripe Account entity"""
    id: str
    object: Literal["account"] = "account"
    business_type: Optional[str] = None
    charges_enabled: bool
    country: str
    created: int
    default_currency: str
    details_submitted: Optional[bool] = None
    email: Optional[str] = None
    payouts_enabled: bool
    type: Literal["standard", "express", "custom"]
    metadata: Optional[Dict[str, str]] = None

    model_config = ConfigDict(extra='allow')


# ==================== Balance Entity ====================

class BalanceAmount(BaseModel):
    """Balance amount for a currency"""
    amount: int
    currency: str
    source_types: Optional[Dict[str, int]] = None

    model_config = ConfigDict(extra='allow')


class BalanceEntity(BaseModel):
    """Stripe Balance entity"""
    object: Literal["balance"] = "balance"
    available: List[BalanceAmount]
    pending: List[BalanceAmount]
    livemode: bool

    model_config = ConfigDict(extra='allow')


# ==================== Coupon Entity ====================

class CouponEntity(BaseModel):
    """Stripe Coupon entity"""
    id: str
    object: Literal["coupon"] = "coupon"
    amount_off: Optional[int] = None
    created: int
    currency: Optional[str] = None
    duration: Literal["forever", "once", "repeating"]
    duration_in_months: Optional[int] = None
    livemode: bool
    max_redemptions: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None
    name: Optional[str] = None
    percent_off: Optional[float] = None
    times_redeemed: int
    valid: bool

    model_config = ConfigDict(extra='allow')


# ==================== Customer Entity ====================

class CustomerEntity(BaseModel):
    """Stripe Customer entity"""
    id: str
    object: Literal["customer"] = "customer"
    address: Optional[Address] = None
    balance: Optional[int] = None
    created: int
    currency: Optional[str] = None
    delinquent: Optional[bool] = None
    description: Optional[str] = None
    email: Optional[str] = None
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    name: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(extra='allow')


# ==================== Dispute Entity ====================

class DisputeEntity(BaseModel):
    """Stripe Dispute entity"""
    id: str
    object: Literal["dispute"] = "dispute"
    amount: int
    charge: str
    created: int
    currency: str
    is_charge_refundable: bool
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    payment_intent: Optional[str] = None
    reason: str
    status: str

    model_config = ConfigDict(extra='allow')


# ==================== Invoice Entity ====================

class InvoiceEntity(BaseModel):
    """Stripe Invoice entity"""
    id: str
    object: Literal["invoice"] = "invoice"
    account_country: Optional[str] = None
    account_name: Optional[str] = None
    amount_due: int
    amount_paid: int
    amount_remaining: int
    attempt_count: int
    attempted: bool
    auto_advance: Optional[bool] = None
    collection_method: Literal["charge_automatically", "send_invoice"]
    created: int
    currency: str
    customer: Optional[str] = None
    description: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    number: Optional[str] = None
    paid: bool
    status: Optional[Literal["draft", "open", "paid", "uncollectible", "void"]] = None
    subscription: Optional[str] = None
    subtotal: int
    total: int

    model_config = ConfigDict(extra='allow')


# ==================== InvoiceItem Entity ====================

class InvoiceItemEntity(BaseModel):
    """Stripe InvoiceItem entity"""
    id: str
    object: Literal["invoiceitem"] = "invoiceitem"
    amount: int
    currency: str
    customer: str
    date: int
    description: Optional[str] = None
    invoice: Optional[str] = None
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    proration: bool
    quantity: Optional[int] = None
    subscription: Optional[str] = None

    model_config = ConfigDict(extra='allow')


# ==================== PaymentLink Entity ====================

class PaymentLinkEntity(BaseModel):
    """Stripe PaymentLink entity"""
    id: str
    object: Literal["payment_link"] = "payment_link"
    active: bool
    allow_promotion_codes: Optional[bool] = None
    billing_address_collection: Optional[str] = None
    currency: Optional[str] = None
    customer_creation: Optional[str] = None
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    url: str

    model_config = ConfigDict(extra='allow')


# ==================== PaymentIntent Entity ====================

class PaymentIntentEntity(BaseModel):
    """Stripe PaymentIntent entity"""
    id: str
    object: Literal["payment_intent"] = "payment_intent"
    amount: int
    amount_received: int
    capture_method: str
    client_secret: Optional[str] = None
    confirmation_method: str
    created: int
    currency: str
    customer: Optional[str] = None
    description: Optional[str] = None
    invoice: Optional[str] = None
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    payment_method: Optional[str] = None
    status: str

    model_config = ConfigDict(extra='allow')


# ==================== Price Entity ====================

class PriceEntity(BaseModel):
    """Stripe Price entity"""
    id: str
    object: Literal["price"] = "price"
    active: bool
    billing_scheme: Literal["per_unit", "tiered"]
    created: int
    currency: str
    livemode: bool
    lookup_key: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    nickname: Optional[str] = None
    product: str
    recurring: Optional[Dict[str, Any]] = None
    type: Literal["one_time", "recurring"]
    unit_amount: Optional[int] = None
    unit_amount_decimal: Optional[str] = None

    model_config = ConfigDict(extra='allow')


# ==================== Product Entity ====================

class ProductEntity(BaseModel):
    """Stripe Product entity"""
    id: str
    object: Literal["product"] = "product"
    active: bool
    created: int
    default_price: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = []
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    name: str
    shippable: Optional[bool] = None
    statement_descriptor: Optional[str] = None
    type: Literal["good", "service"]
    unit_label: Optional[str] = None
    updated: int
    url: Optional[str] = None

    model_config = ConfigDict(extra='allow')


# ==================== Refund Entity ====================

class RefundEntity(BaseModel):
    """Stripe Refund entity"""
    id: str
    object: Literal["refund"] = "refund"
    amount: int
    charge: Optional[str] = None
    created: int
    currency: str
    metadata: Optional[Dict[str, str]] = None
    payment_intent: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(extra='allow')


# ==================== Subscription Entity ====================

class SubscriptionEntity(BaseModel):
    """Stripe Subscription entity"""
    id: str
    object: Literal["subscription"] = "subscription"
    cancel_at_period_end: bool
    created: int
    current_period_end: int
    current_period_start: int
    customer: str
    currency: str
    livemode: bool
    metadata: Optional[Dict[str, str]] = None
    status: str
    start_date: int

    model_config = ConfigDict(extra='allow')
