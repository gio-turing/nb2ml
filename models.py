"""
Pydantic models for Stripe API operations
"""

from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# ==================== Common Models ====================

class PaginationParams(BaseModel):
    """Common pagination parameters"""
    limit: Optional[int] = Field(None, ge=1, le=100, description="Number of objects to return (1-100)")
    starting_after: Optional[str] = Field(None, description="Cursor for pagination (object ID)")
    ending_before: Optional[str] = Field(None, description="Cursor for pagination (object ID)")

    model_config = ConfigDict(extra='forbid')


class DateRangeFilter(BaseModel):
    """Date range filter for queries"""
    gt: Optional[int] = Field(None, description="Greater than timestamp")
    gte: Optional[int] = Field(None, description="Greater than or equal to timestamp")
    lt: Optional[int] = Field(None, description="Less than timestamp")
    lte: Optional[int] = Field(None, description="Less than or equal to timestamp")

    model_config = ConfigDict(extra='forbid')


class Address(BaseModel):
    """Address model"""
    line1: Optional[str] = Field(None, description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Two-letter country code")

    model_config = ConfigDict(extra='forbid')


# ==================== Coupon Models ====================

class CreateCouponParams(BaseModel):
    """Parameters for creating a coupon"""
    duration: Literal['forever', 'once', 'repeating'] = Field(..., description="Duration of the coupon")
    id: Optional[str] = Field(None, description="Unique coupon ID")
    amount_off: Optional[int] = Field(None, description="Amount in cents to subtract")
    percent_off: Optional[float] = Field(None, ge=0, le=100, description="Percentage to subtract")
    currency: Optional[str] = Field(None, pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    duration_in_months: Optional[int] = Field(None, ge=1, description="Number of months (required if duration='repeating')")
    max_redemptions: Optional[int] = Field(None, ge=1, description="Maximum number of redemptions")
    name: Optional[str] = Field(None, description="Name of the coupon")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(extra='forbid')


class ListCouponsParams(PaginationParams):
    """Parameters for listing coupons"""
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Customer Models ====================

class ShippingDetails(BaseModel):
    """Shipping details"""
    name: str = Field(..., description="Recipient name")
    address: Address = Field(..., description="Shipping address")
    carrier: Optional[str] = Field(None, description="Shipping carrier")
    phone: Optional[str] = Field(None, description="Phone number")
    tracking_number: Optional[str] = Field(None, description="Tracking number")

    model_config = ConfigDict(extra='forbid')


class InvoiceSettings(BaseModel):
    """Customer invoice settings"""
    custom_fields: Optional[List[Dict[str, str]]] = None
    default_payment_method: Optional[str] = None
    footer: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class TaxInfo(BaseModel):
    """Tax information"""
    automatic_tax: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class CreateCustomerParams(BaseModel):
    """Parameters for creating a customer"""
    email: Optional[str] = Field(None, description="Customer's email address")
    name: Optional[str] = Field(None, description="Customer's full name")
    description: Optional[str] = Field(None, description="Description of the customer")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    address: Optional[Address] = Field(None, description="Customer's address")
    payment_method: Optional[str] = Field(None, description="PaymentMethod ID")
    invoice_settings: Optional[InvoiceSettings] = Field(None, description="Invoice settings")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    shipping: Optional[ShippingDetails] = Field(None, description="Shipping information")
    tax: Optional[TaxInfo] = Field(None, description="Tax information")

    model_config = ConfigDict(extra='forbid')


class ListCustomersParams(PaginationParams):
    """Parameters for listing customers"""
    email: Optional[str] = Field(None, description="Filter by customer email")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Dispute Models ====================

class DisputeEvidence(BaseModel):
    """Evidence for dispute resolution"""
    customer_name: Optional[str] = None
    customer_email_address: Optional[str] = None
    customer_purchase_ip: Optional[str] = None
    billing_address: Optional[str] = None
    receipt: Optional[str] = None
    customer_signature: Optional[str] = None
    shipping_documentation: Optional[str] = None
    uncategorized_text: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class ListDisputesParams(PaginationParams):
    """Parameters for listing disputes"""
    charge: Optional[str] = Field(None, description="Filter by charge ID")
    payment_intent: Optional[str] = Field(None, description="Filter by PaymentIntent ID")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


class UpdateDisputeParams(BaseModel):
    """Parameters for updating a dispute"""
    dispute_id: str = Field(..., description="The ID of the dispute to update")
    evidence: Optional[DisputeEvidence] = Field(None, description="Evidence to respond to the dispute")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    submit: Optional[bool] = Field(None, description="Whether to immediately submit evidence")

    model_config = ConfigDict(extra='forbid')


# ==================== Invoice Models ====================

class CreateInvoiceParams(BaseModel):
    """Parameters for creating an invoice"""
    customer: str = Field(..., description="Customer ID")
    auto_advance: Optional[bool] = Field(None, description="Automatically finalize invoice")
    collection_method: Optional[Literal['charge_automatically', 'send_invoice']] = Field(None, description="How to collect payment")
    description: Optional[str] = Field(None, description="Description of the invoice")
    due_date: Optional[int] = Field(None, description="Due date timestamp")
    currency: Optional[str] = Field(None, pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    days_until_due: Optional[int] = Field(None, ge=0, description="Number of days until due")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    subscription: Optional[str] = Field(None, description="Subscription ID")

    model_config = ConfigDict(extra='forbid')


class CreateInvoiceItemParams(BaseModel):
    """Parameters for creating an invoice item"""
    customer: str = Field(..., description="Customer ID")
    currency: str = Field(..., pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    amount: Optional[int] = Field(None, description="Amount in cents")
    description: Optional[str] = Field(None, description="Description")
    invoice: Optional[str] = Field(None, description="Invoice ID")
    price: Optional[str] = Field(None, description="Price ID")
    quantity: Optional[int] = Field(None, ge=1, description="Quantity")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    subscription: Optional[str] = Field(None, description="Subscription ID")

    model_config = ConfigDict(extra='forbid')


class FinalizeInvoiceParams(BaseModel):
    """Parameters for finalizing an invoice"""
    invoice_id: str = Field(..., description="The ID of the invoice to finalize")
    auto_advance: Optional[bool] = Field(None, description="Whether to automatically advance")

    model_config = ConfigDict(extra='forbid')


class ListInvoicesParams(PaginationParams):
    """Parameters for listing invoices"""
    customer: Optional[str] = Field(None, description="Filter by customer ID")
    subscription: Optional[str] = Field(None, description="Filter by subscription ID")
    status: Optional[Literal['draft', 'open', 'paid', 'uncollectible', 'void']] = Field(None, description="Filter by status")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Payment Link Models ====================

class PaymentLinkLineItem(BaseModel):
    """Line item for payment link"""
    price: str = Field(..., description="Price ID")
    quantity: int = Field(..., ge=1, description="Quantity")

    model_config = ConfigDict(extra='forbid')


class AfterCompletion(BaseModel):
    """After completion behavior"""
    type: Literal['redirect', 'hosted_confirmation'] = Field(..., description="Completion type")
    redirect: Optional[Dict[str, str]] = None
    hosted_confirmation: Optional[Dict[str, str]] = None

    model_config = ConfigDict(extra='forbid')


class AutomaticTax(BaseModel):
    """Automatic tax settings"""
    enabled: bool = Field(..., description="Enable automatic tax")

    model_config = ConfigDict(extra='forbid')


class CreatePaymentLinkParams(BaseModel):
    """Parameters for creating a payment link"""
    line_items: List[PaymentLinkLineItem] = Field(..., min_length=1, description="Line items")
    after_completion: Optional[AfterCompletion] = Field(None, description="Behavior after completion")
    allow_promotion_codes: Optional[bool] = Field(None, description="Enable promotion codes")
    application_fee_amount: Optional[int] = Field(None, description="Application fee amount")
    application_fee_percent: Optional[float] = Field(None, ge=0, le=100, description="Application fee percent")
    automatic_tax: Optional[AutomaticTax] = Field(None, description="Automatic tax settings")
    billing_address_collection: Optional[Literal['auto', 'required']] = Field(None, description="Billing address collection mode")
    currency: Optional[str] = Field(None, pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    customer_creation: Optional[Literal['always', 'if_required']] = Field(None, description="Customer creation mode")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    payment_method_types: Optional[List[str]] = Field(None, description="Payment method types")
    phone_number_collection: Optional[Dict[str, bool]] = Field(None, description="Phone number collection settings")
    shipping_address_collection: Optional[Dict[str, Any]] = Field(None, description="Shipping address collection")
    submit_type: Optional[Literal['auto', 'book', 'donate', 'pay']] = Field(None, description="Submit button type")

    model_config = ConfigDict(extra='forbid')


# ==================== PaymentIntent Models ====================

class ListPaymentIntentsParams(PaginationParams):
    """Parameters for listing payment intents"""
    customer: Optional[str] = Field(None, description="Filter by customer ID")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Price Models ====================

class RecurringPrice(BaseModel):
    """Recurring pricing settings"""
    interval: Literal['day', 'week', 'month', 'year'] = Field(..., description="Billing interval")
    interval_count: Optional[int] = Field(1, ge=1, description="Number of intervals between billing")
    usage_type: Optional[Literal['metered', 'licensed']] = Field('licensed', description="Usage type")

    model_config = ConfigDict(extra='forbid')


class PriceTier(BaseModel):
    """Price tier for tiered pricing"""
    up_to: Optional[Union[int, Literal['inf']]] = Field(None, description="Up to quantity")
    unit_amount: Optional[int] = Field(None, description="Unit amount")
    flat_amount: Optional[int] = Field(None, description="Flat amount")

    model_config = ConfigDict(extra='forbid')


class ProductData(BaseModel):
    """Product data for creating a new product with a price"""
    name: str = Field(..., description="Product name")
    active: Optional[bool] = None
    metadata: Optional[Dict[str, str]] = None

    model_config = ConfigDict(extra='forbid')


class CreatePriceParams(BaseModel):
    """Parameters for creating a price"""
    currency: str = Field(..., pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    product: Optional[str] = Field(None, description="Product ID")
    unit_amount: Optional[int] = Field(None, description="Price in cents")
    unit_amount_decimal: Optional[str] = Field(None, description="Price as decimal string")
    active: Optional[bool] = Field(None, description="Whether price can be used")
    billing_scheme: Optional[Literal['per_unit', 'tiered']] = Field(None, description="Billing scheme")
    currency_options: Optional[Dict[str, Any]] = Field(None, description="Prices in different currencies")
    custom_unit_amount: Optional[Dict[str, int]] = Field(None, description="Customer-provided unit amount")
    lookup_key: Optional[str] = Field(None, description="Lookup key")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    nickname: Optional[str] = Field(None, description="Brief description")
    product_data: Optional[ProductData] = Field(None, description="Data to create new product")
    recurring: Optional[RecurringPrice] = Field(None, description="Recurring billing settings")
    tax_behavior: Optional[Literal['exclusive', 'inclusive', 'unspecified']] = Field(None, description="Tax behavior")
    tiers: Optional[List[PriceTier]] = Field(None, description="Pricing tiers")
    tiers_mode: Optional[Literal['graduated', 'volume']] = Field(None, description="Tiered pricing mode")
    transfer_lookup_key: Optional[bool] = Field(None, description="Apply lookup_key to product")

    model_config = ConfigDict(extra='forbid')


class ListPricesParams(PaginationParams):
    """Parameters for listing prices"""
    product: Optional[str] = Field(None, description="Filter by product ID")
    active: Optional[bool] = Field(None, description="Filter by active status")
    currency: Optional[str] = Field(None, pattern="^[a-z]{3}$", description="Filter by currency")
    type: Optional[Literal['one_time', 'recurring']] = Field(None, description="Filter by price type")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Product Models ====================

class PackageDimensions(BaseModel):
    """Package dimensions for shipping"""
    height: float = Field(..., gt=0, description="Height")
    length: float = Field(..., gt=0, description="Length")
    weight: float = Field(..., gt=0, description="Weight")
    width: float = Field(..., gt=0, description="Width")

    model_config = ConfigDict(extra='forbid')


class ProductFeature(BaseModel):
    """Product feature"""
    name: str = Field(..., description="Feature name")

    model_config = ConfigDict(extra='forbid')


class DefaultPriceData(BaseModel):
    """Default price data for product"""
    currency: str = Field(..., pattern="^[a-z]{3}$", description="Three-letter ISO currency code")
    unit_amount: Optional[int] = Field(None, description="Price in cents")
    recurring: Optional[RecurringPrice] = None

    model_config = ConfigDict(extra='forbid')


class CreateProductParams(BaseModel):
    """Parameters for creating a product"""
    name: str = Field(..., description="Product name")
    active: Optional[bool] = Field(None, description="Whether product is available")
    description: Optional[str] = Field(None, description="Product description")
    default_price_data: Optional[DefaultPriceData] = Field(None, description="Data to generate default price")
    features: Optional[List[ProductFeature]] = Field(None, description="List of product features")
    images: Optional[List[str]] = Field(None, description="List of image URLs")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    package_dimensions: Optional[PackageDimensions] = Field(None, description="Package dimensions")
    shippable: Optional[bool] = Field(None, description="Whether product is shipped")
    statement_descriptor: Optional[str] = Field(None, max_length=22, description="Statement descriptor")
    tax_code: Optional[str] = Field(None, description="Tax code")
    unit_label: Optional[str] = Field(None, description="Unit label")
    url: Optional[str] = Field(None, description="Product URL")

    model_config = ConfigDict(extra='forbid')


class ListProductsParams(PaginationParams):
    """Parameters for listing products"""
    active: Optional[bool] = Field(None, description="Filter by active status")
    ids: Optional[List[str]] = Field(None, description="Filter by product IDs")
    shippable: Optional[bool] = Field(None, description="Filter by shippable status")
    url: Optional[str] = Field(None, description="Filter by URL")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


# ==================== Refund Models ====================

class CreateRefundParams(BaseModel):
    """Parameters for creating a refund"""
    charge: Optional[str] = Field(None, description="Charge ID")
    payment_intent: Optional[str] = Field(None, description="PaymentIntent ID")
    amount: Optional[int] = Field(None, ge=0, description="Amount to refund in cents")
    reason: Optional[Literal['duplicate', 'fraudulent', 'requested_by_customer']] = Field(None, description="Reason for refund")
    refund_application_fee: Optional[bool] = Field(None, description="Whether to refund application fee")
    reverse_transfer: Optional[bool] = Field(None, description="Whether to reverse transfer")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(extra='forbid')


# ==================== Subscription Models ====================

class CancellationDetails(BaseModel):
    """Cancellation details"""
    comment: Optional[str] = Field(None, description="Comment about cancellation")
    feedback: Optional[str] = Field(None, description="Feedback about cancellation")

    model_config = ConfigDict(extra='forbid')


class CancelSubscriptionParams(BaseModel):
    """Parameters for canceling a subscription"""
    subscription_id: str = Field(..., description="Subscription ID")
    invoice_now: Optional[bool] = Field(None, description="Create invoice for unpaid charges")
    prorate: Optional[bool] = Field(None, description="Create prorations")
    cancellation_details: Optional[CancellationDetails] = Field(None, description="Cancellation details")

    model_config = ConfigDict(extra='forbid')


class ListSubscriptionsParams(PaginationParams):
    """Parameters for listing subscriptions"""
    customer: Optional[str] = Field(None, description="Filter by customer ID")
    price: Optional[str] = Field(None, description="Filter by price ID")
    status: Optional[Literal['active', 'past_due', 'unpaid', 'canceled', 'incomplete', 'incomplete_expired', 'trialing', 'all', 'ended']] = Field(None, description="Filter by status")
    created: Optional[Union[int, DateRangeFilter]] = Field(None, description="Filter by creation timestamp")

    model_config = ConfigDict(extra='forbid')


class SubscriptionItem(BaseModel):
    """Subscription item update"""
    id: Optional[str] = Field(None, description="Subscription item ID")
    price: Optional[str] = Field(None, description="Price ID")
    quantity: Optional[int] = Field(None, ge=1, description="Quantity")

    model_config = ConfigDict(extra='forbid')


class UpdateSubscriptionParams(BaseModel):
    """Parameters for updating a subscription"""
    subscription_id: str = Field(..., description="Subscription ID")
    cancel_at_period_end: Optional[bool] = Field(None, description="Cancel at period end")
    default_payment_method: Optional[str] = Field(None, description="Default payment method ID")
    items: Optional[List[SubscriptionItem]] = Field(None, description="Subscription items to update")
    proration_behavior: Optional[Literal['create_prorations', 'none', 'always_invoice']] = Field(None, description="Proration behavior")
    proration_date: Optional[int] = Field(None, description="Proration date timestamp")
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")
    payment_behavior: Optional[Literal['allow_incomplete', 'default_incomplete', 'error_if_incomplete', 'pending_if_incomplete']] = Field(None, description="Payment behavior")
    billing_cycle_anchor: Optional[Literal['now', 'unchanged']] = Field(None, description="Billing cycle anchor")
    trial_end: Optional[Union[int, Literal['now']]] = Field(None, description="Trial end timestamp or 'now'")

    model_config = ConfigDict(extra='forbid')


# ==================== Search and Utility Models ====================

class SearchStripeResourcesParams(BaseModel):
    """Parameters for searching Stripe resources"""
    resource_type: Literal['charges', 'customers', 'invoices', 'payment_intents', 'prices', 'products', 'subscriptions'] = Field(..., description="Type of resource to search")
    query: str = Field(..., min_length=1, description="Search query string")
    limit: Optional[int] = Field(None, ge=1, le=100, description="Number of results to return")
    page: Optional[str] = Field(None, description="Pagination token")

    model_config = ConfigDict(extra='forbid')


class FetchStripeResourceParams(BaseModel):
    """Parameters for fetching a Stripe resource"""
    resource_type: Literal['accounts', 'charges', 'customers', 'invoices', 'payment_intents', 'payment_methods', 'prices', 'products', 'refunds', 'disputes', 'coupons', 'subscriptions', 'balances'] = Field(..., description="Type of resource to fetch")
    resource_id: str = Field(..., description="ID of the resource")

    model_config = ConfigDict(extra='forbid')


class SearchStripeDocumentationParams(BaseModel):
    """Parameters for searching Stripe documentation"""
    query: str = Field(..., min_length=1, description="Search query")
    category: Optional[Literal['api', 'guides', 'webhooks', 'integrations', 'all']] = Field('all', description="Documentation category")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

    model_config = ConfigDict(extra='forbid')


# ==================== Configuration Models ====================

class GatewayDBConfig(BaseModel):
    """Configuration for GatewayDB"""
    api_key: str = Field(..., description="Stripe API key")
    api_version: Optional[str] = Field("2023-10-16", description="Stripe API version")
    timeout: Optional[int] = Field(80, ge=1, description="Request timeout in seconds")
    max_network_retries: Optional[int] = Field(3, ge=0, description="Maximum network retries")

    model_config = ConfigDict(extra='forbid')
