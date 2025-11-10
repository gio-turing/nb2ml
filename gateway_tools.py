"""
GatewayTools - MCP tool implementations for Stripe API operations

This module contains:
1. All parameter models (CreateCustomerParams, ListInvoicesParams, etc.)
2. GatewayTools class - the main tools class with all 25 MCP implementations
"""

from typing import Any, Dict, Optional, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
import stripe
import time
from gateway_db import (
    GatewayDB,
    AccountEntity,
    BalanceEntity,
    CouponEntity,
    CustomerEntity,
    DisputeEntity,
    InvoiceEntity,
    InvoiceItemEntity,
    PaymentLinkEntity,
    PaymentIntentEntity,
    PriceEntity,
    ProductEntity,
    RefundEntity,
    SubscriptionEntity,
    Address,
)


# ==================== Parameter Models ====================

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


# Note: Address is imported from gateway_db, not defined here


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


class GatewayTools:
    """
    GatewayTools - MCP tool implementations for Stripe API

    This class implements all 25 Stripe MCP tools and manages
    the GatewayDB entity database.

    All operations:
    1. Call Stripe API
    2. Convert response to entity model
    3. Store entity in GatewayDB
    4. Return the entity

    Attributes:
        db: GatewayDB instance containing all entities
        config: Configuration for Stripe API
    """

    def __init__(self, config: GatewayDBConfig, db: GatewayDB = None):
        """
        Initialize GatewayTools with Stripe configuration

        Args:
            config: GatewayDBConfig instance with API credentials
            db: Optional GatewayDB instance (creates new one if not provided)
        """
        self.config = config
        self.db = db if db is not None else GatewayDB()

        # Configure Stripe
        stripe.api_key = config.api_key
        stripe.api_version = config.api_version
        stripe.max_network_retries = config.max_network_retries

        # Set HTTP client with timeout (if available)
        try:
            if hasattr(stripe, 'http_client'):
                stripe.default_http_client = stripe.http_client.RequestsClient(timeout=config.timeout)
        except (AttributeError, ImportError):
            # Older/newer Stripe versions may not have http_client
            pass

    # ==================== Account Operations ====================

    def get_stripe_account_info(self) -> AccountEntity:
        """
        Retrieves the details of the Stripe account

        Returns:
            AccountEntity: The account entity
        """
        account = stripe.Account.retrieve()
        entity = AccountEntity(**account)
        self.db.add_account(entity)
        self._update_sync_time()
        return entity

    # ==================== Balance Operations ====================

    def retrieve_balance(self) -> BalanceEntity:
        """
        Retrieves the current account balance

        Returns:
            BalanceEntity: The balance entity
        """
        balance = stripe.Balance.retrieve()
        entity = BalanceEntity(**balance)
        self.db.add_balance(entity)
        self._update_sync_time()
        return entity

    # ==================== Coupon Operations ====================

    def create_coupon(self, params: CreateCouponParams) -> CouponEntity:
        """
        Creates a new coupon object

        Args:
            params: CreateCouponParams with coupon details

        Returns:
            CouponEntity: The created coupon entity
        """
        data = params.model_dump(exclude_none=True)
        coupon = stripe.Coupon.create(**data)
        entity = CouponEntity(**coupon)
        self.db.add_coupon(entity)
        self._update_sync_time()
        return entity

    def list_coupons(self, params: ListCouponsParams = ListCouponsParams()) -> Dict[str, Any]:
        """
        Returns a list of your coupons

        Args:
            params: ListCouponsParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Coupon.list(**data)

        # Store all coupons in DB
        for coupon_data in response.data:
            entity = CouponEntity(**coupon_data)
            self.db.add_coupon(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [CouponEntity(**c).model_dump() for c in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Customer Operations ====================

    def create_customer(self, params: CreateCustomerParams = CreateCustomerParams()) -> CustomerEntity:
        """
        Creates a new customer object

        Args:
            params: CreateCustomerParams with customer details

        Returns:
            CustomerEntity: The created customer entity
        """
        data = params.model_dump(exclude_none=True)
        # Convert nested Pydantic models to dicts
        if 'address' in data and params.address:
            data['address'] = params.address.model_dump(exclude_none=True)
        if 'shipping' in data and params.shipping:
            data['shipping'] = params.shipping.model_dump(exclude_none=True)
        if 'invoice_settings' in data and params.invoice_settings:
            data['invoice_settings'] = params.invoice_settings.model_dump(exclude_none=True)
        if 'tax' in data and params.tax:
            data['tax'] = params.tax.model_dump(exclude_none=True)

        customer = stripe.Customer.create(**data)
        entity = CustomerEntity(**customer)
        self.db.add_customer(entity)
        self._update_sync_time()
        return entity

    def list_customers(self, params: ListCustomersParams = ListCustomersParams()) -> Dict[str, Any]:
        """
        Returns a list of your customers

        Args:
            params: ListCustomersParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Customer.list(**data)

        # Store all customers in DB
        for customer_data in response.data:
            entity = CustomerEntity(**customer_data)
            self.db.add_customer(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [CustomerEntity(**c).model_dump() for c in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Dispute Operations ====================

    def list_disputes(self, params: ListDisputesParams = ListDisputesParams()) -> Dict[str, Any]:
        """
        Returns a list of your disputes

        Args:
            params: ListDisputesParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Dispute.list(**data)

        # Store all disputes in DB
        for dispute_data in response.data:
            entity = DisputeEntity(**dispute_data)
            self.db.add_dispute(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [DisputeEntity(**d).model_dump() for d in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    def update_dispute(self, params: UpdateDisputeParams) -> DisputeEntity:
        """
        Updates a specific dispute

        Args:
            params: UpdateDisputeParams with dispute update details

        Returns:
            DisputeEntity: The updated dispute entity
        """
        dispute_id = params.dispute_id
        data = params.model_dump(exclude_none=True, exclude={'dispute_id'})

        # Convert nested Pydantic models to dicts
        if 'evidence' in data and params.evidence:
            data['evidence'] = params.evidence.model_dump(exclude_none=True)

        dispute = stripe.Dispute.modify(dispute_id, **data)
        entity = DisputeEntity(**dispute)
        self.db.add_dispute(entity)
        self._update_sync_time()
        return entity

    # ==================== Invoice Operations ====================

    def create_invoice(self, params: CreateInvoiceParams) -> InvoiceEntity:
        """
        Creates a draft invoice for a given customer

        Args:
            params: CreateInvoiceParams with invoice details

        Returns:
            InvoiceEntity: The created invoice entity
        """
        data = params.model_dump(exclude_none=True)
        invoice = stripe.Invoice.create(**data)
        entity = InvoiceEntity(**invoice)
        self.db.add_invoice(entity)
        self._update_sync_time()
        return entity

    def create_invoice_item(self, params: CreateInvoiceItemParams) -> InvoiceItemEntity:
        """
        Creates an invoice item

        Args:
            params: CreateInvoiceItemParams with invoice item details

        Returns:
            InvoiceItemEntity: The created invoice item entity
        """
        data = params.model_dump(exclude_none=True)
        item = stripe.InvoiceItem.create(**data)
        entity = InvoiceItemEntity(**item)
        self.db.add_invoice_item(entity)
        self._update_sync_time()
        return entity

    def finalize_invoice(self, params: FinalizeInvoiceParams) -> InvoiceEntity:
        """
        Finalizes a draft invoice

        Args:
            params: FinalizeInvoiceParams with finalization details

        Returns:
            InvoiceEntity: The finalized invoice entity
        """
        invoice_id = params.invoice_id
        data = params.model_dump(exclude_none=True, exclude={'invoice_id'})
        invoice = stripe.Invoice.finalize_invoice(invoice_id, **data)
        entity = InvoiceEntity(**invoice)
        self.db.add_invoice(entity)
        self._update_sync_time()
        return entity

    def list_invoices(self, params: ListInvoicesParams = ListInvoicesParams()) -> Dict[str, Any]:
        """
        Returns a list of your invoices

        Args:
            params: ListInvoicesParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Invoice.list(**data)

        # Store all invoices in DB
        for invoice_data in response.data:
            entity = InvoiceEntity(**invoice_data)
            self.db.add_invoice(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [InvoiceEntity(**i).model_dump() for i in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Payment Link Operations ====================

    def create_payment_link(self, params: CreatePaymentLinkParams) -> PaymentLinkEntity:
        """
        Creates a payment link

        Args:
            params: CreatePaymentLinkParams with payment link details

        Returns:
            PaymentLinkEntity: The created payment link entity
        """
        data = params.model_dump(exclude_none=True)

        # Convert line items
        if 'line_items' in data:
            data['line_items'] = [item.model_dump(exclude_none=True) if hasattr(item, 'model_dump') else item
                                   for item in params.line_items]

        # Convert nested models
        if 'after_completion' in data and params.after_completion:
            data['after_completion'] = params.after_completion.model_dump(exclude_none=True)

        if 'automatic_tax' in data and params.automatic_tax:
            data['automatic_tax'] = params.automatic_tax.model_dump(exclude_none=True)

        link = stripe.PaymentLink.create(**data)
        entity = PaymentLinkEntity(**link)
        self.db.add_payment_link(entity)
        self._update_sync_time()
        return entity

    # ==================== PaymentIntent Operations ====================

    def list_payment_intents(self, params: ListPaymentIntentsParams = ListPaymentIntentsParams()) -> Dict[str, Any]:
        """
        Returns a list of PaymentIntents

        Args:
            params: ListPaymentIntentsParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.PaymentIntent.list(**data)

        # Store all payment intents in DB
        for intent_data in response.data:
            entity = PaymentIntentEntity(**intent_data)
            self.db.add_payment_intent(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [PaymentIntentEntity(**pi).model_dump() for pi in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Price Operations ====================

    def create_price(self, params: CreatePriceParams) -> PriceEntity:
        """
        Creates a new price for an existing product

        Args:
            params: CreatePriceParams with price details

        Returns:
            PriceEntity: The created price entity
        """
        data = params.model_dump(exclude_none=True)

        # Convert nested models
        if 'recurring' in data and params.recurring:
            data['recurring'] = params.recurring.model_dump(exclude_none=True)

        if 'product_data' in data and params.product_data:
            data['product_data'] = params.product_data.model_dump(exclude_none=True)

        if 'tiers' in data and params.tiers:
            data['tiers'] = [tier.model_dump(exclude_none=True) for tier in params.tiers]

        price = stripe.Price.create(**data)
        entity = PriceEntity(**price)
        self.db.add_price(entity)
        self._update_sync_time()
        return entity

    def list_prices(self, params: ListPricesParams = ListPricesParams()) -> Dict[str, Any]:
        """
        Returns a list of your prices

        Args:
            params: ListPricesParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Price.list(**data)

        # Store all prices in DB
        for price_data in response.data:
            entity = PriceEntity(**price_data)
            self.db.add_price(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [PriceEntity(**p).model_dump() for p in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Product Operations ====================

    def create_product(self, params: CreateProductParams) -> ProductEntity:
        """
        Creates a new product object

        Args:
            params: CreateProductParams with product details

        Returns:
            ProductEntity: The created product entity
        """
        data = params.model_dump(exclude_none=True)

        # Convert nested models
        if 'default_price_data' in data and params.default_price_data:
            data['default_price_data'] = params.default_price_data.model_dump(exclude_none=True)
            if params.default_price_data.recurring:
                data['default_price_data']['recurring'] = params.default_price_data.recurring.model_dump(exclude_none=True)

        if 'features' in data and params.features:
            data['features'] = [feature.model_dump(exclude_none=True) for feature in params.features]

        if 'package_dimensions' in data and params.package_dimensions:
            data['package_dimensions'] = params.package_dimensions.model_dump(exclude_none=True)

        product = stripe.Product.create(**data)
        entity = ProductEntity(**product)
        self.db.add_product(entity)
        self._update_sync_time()
        return entity

    def list_products(self, params: ListProductsParams = ListProductsParams()) -> Dict[str, Any]:
        """
        Returns a list of your products

        Args:
            params: ListProductsParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Product.list(**data)

        # Store all products in DB
        for product_data in response.data:
            entity = ProductEntity(**product_data)
            self.db.add_product(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [ProductEntity(**p).model_dump() for p in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    # ==================== Refund Operations ====================

    def create_refund(self, params: CreateRefundParams) -> RefundEntity:
        """
        Creates a refund for a charge

        Args:
            params: CreateRefundParams with refund details

        Returns:
            RefundEntity: The created refund entity
        """
        data = params.model_dump(exclude_none=True)
        refund = stripe.Refund.create(**data)
        entity = RefundEntity(**refund)
        self.db.add_refund(entity)
        self._update_sync_time()
        return entity

    # ==================== Subscription Operations ====================

    def cancel_subscription(self, params: CancelSubscriptionParams) -> SubscriptionEntity:
        """
        Cancels a customer's subscription

        Args:
            params: CancelSubscriptionParams with cancellation details

        Returns:
            SubscriptionEntity: The canceled subscription entity
        """
        subscription_id = params.subscription_id
        data = params.model_dump(exclude_none=True, exclude={'subscription_id'})

        # Convert nested models
        if 'cancellation_details' in data and params.cancellation_details:
            data['cancellation_details'] = params.cancellation_details.model_dump(exclude_none=True)

        subscription = stripe.Subscription.delete(subscription_id, **data)
        entity = SubscriptionEntity(**subscription)

        # Remove from DB if fully canceled
        if entity.status == "canceled":
            self.db.remove_subscription(subscription_id)
        else:
            self.db.add_subscription(entity)

        self._update_sync_time()
        return entity

    def list_subscriptions(self, params: ListSubscriptionsParams = ListSubscriptionsParams()) -> Dict[str, Any]:
        """
        Returns a list of your subscriptions

        Args:
            params: ListSubscriptionsParams with filtering options

        Returns:
            Dict: Response with data array and metadata
        """
        data = params.model_dump(exclude_none=True)
        response = stripe.Subscription.list(**data)

        # Store all subscriptions in DB
        for subscription_data in response.data:
            entity = SubscriptionEntity(**subscription_data)
            self.db.add_subscription(entity)

        self._update_sync_time()

        return {
            "object": "list",
            "data": [SubscriptionEntity(**s).model_dump() for s in response.data],
            "has_more": response.has_more,
            "url": response.url,
        }

    def update_subscription(self, params: UpdateSubscriptionParams) -> SubscriptionEntity:
        """
        Updates an existing subscription

        Args:
            params: UpdateSubscriptionParams with update details

        Returns:
            SubscriptionEntity: The updated subscription entity
        """
        subscription_id = params.subscription_id
        data = params.model_dump(exclude_none=True, exclude={'subscription_id'})

        # Convert items list
        if 'items' in data and params.items:
            data['items'] = [item.model_dump(exclude_none=True) for item in params.items]

        subscription = stripe.Subscription.modify(subscription_id, **data)
        entity = SubscriptionEntity(**subscription)
        self.db.add_subscription(entity)
        self._update_sync_time()
        return entity

    # ==================== Search and Utility Operations ====================

    def search_stripe_resources(self, params: SearchStripeResourcesParams) -> Dict[str, Any]:
        """
        Searches across Stripe resources using a query string

        Args:
            params: SearchStripeResourcesParams with search criteria

        Returns:
            Dict: Search results with metadata
        """
        resource_type = params.resource_type
        data = params.model_dump(exclude_none=True, exclude={'resource_type'})

        resource_map = {
            "charges": stripe.Charge,
            "customers": stripe.Customer,
            "invoices": stripe.Invoice,
            "payment_intents": stripe.PaymentIntent,
            "prices": stripe.Price,
            "products": stripe.Product,
            "subscriptions": stripe.Subscription,
        }

        if resource_type not in resource_map:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        response = resource_map[resource_type].search(**data)

        return {
            "object": "search_result",
            "data": response.data,
            "has_more": response.has_more,
            "total_count": getattr(response, 'total_count', None),
            "url": response.url,
        }

    def fetch_stripe_resource(self, params: FetchStripeResourceParams) -> Any:
        """
        Fetches a specific Stripe resource by ID

        Args:
            params: FetchStripeResourceParams with resource details

        Returns:
            Entity: The requested resource entity
        """
        resource_type = params.resource_type
        resource_id = params.resource_id

        resource_map = {
            "accounts": (stripe.Account, AccountEntity, self.db.add_account),
            "customers": (stripe.Customer, CustomerEntity, self.db.add_customer),
            "invoices": (stripe.Invoice, InvoiceEntity, self.db.add_invoice),
            "payment_intents": (stripe.PaymentIntent, PaymentIntentEntity, self.db.add_payment_intent),
            "prices": (stripe.Price, PriceEntity, self.db.add_price),
            "products": (stripe.Product, ProductEntity, self.db.add_product),
            "refunds": (stripe.Refund, RefundEntity, self.db.add_refund),
            "disputes": (stripe.Dispute, DisputeEntity, self.db.add_dispute),
            "coupons": (stripe.Coupon, CouponEntity, self.db.add_coupon),
            "subscriptions": (stripe.Subscription, SubscriptionEntity, self.db.add_subscription),
        }

        if resource_type == "balances":
            return self.retrieve_balance()

        if resource_type not in resource_map:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        stripe_class, entity_class, add_method = resource_map[resource_type]
        response = stripe_class.retrieve(resource_id)
        entity = entity_class(**response)
        add_method(entity)
        self._update_sync_time()
        return entity

    def search_stripe_documentation(self, params: SearchStripeDocumentationParams) -> Dict[str, Any]:
        """
        Searches Stripe documentation

        Note: This is a placeholder for integration with Stripe's documentation API
        or a custom search service.

        Args:
            params: SearchStripeDocumentationParams with search criteria

        Returns:
            Dict: Search results structure
        """
        data = params.model_dump()
        return {
            "query": data["query"],
            "category": data["category"],
            "limit": data["limit"],
            "results": [],
            "message": "Documentation search requires integration with Stripe Docs API or custom search service",
        }

    # ==================== Helper Methods ====================

    def _update_sync_time(self) -> None:
        """Update the last sync timestamp"""
        self.db.last_sync = int(time.time())

    def test_connection(self) -> bool:
        """
        Tests the API connection

        Returns:
            bool: True if connection is successful
        """
        try:
            stripe.Balance.retrieve()
            return True
        except Exception as e:
            print(f"Stripe connection test failed: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        Gets API configuration (with redacted API key)

        Returns:
            Dict: Configuration dictionary
        """
        return {
            "api_key": "***REDACTED***",
            "api_version": self.config.api_version,
            "timeout": self.config.timeout,
            "max_network_retries": self.config.max_network_retries,
        }

    def get_database(self) -> GatewayDB:
        """
        Gets the GatewayDB instance

        Returns:
            GatewayDB: The database instance
        """
        return self.db

    def sync_all_data(self) -> Dict[str, int]:
        """
        Syncs all data from Stripe API to local database

        Returns:
            Dict: Count of synced entities
        """
        stats = {}

        # Sync account and balance
        self.get_stripe_account_info()
        self.retrieve_balance()

        # Sync all collections
        self.list_coupons(ListCouponsParams(limit=100))
        stats['coupons'] = len(self.db.coupons)

        self.list_customers(ListCustomersParams(limit=100))
        stats['customers'] = len(self.db.customers)

        self.list_invoices(ListInvoicesParams(limit=100))
        stats['invoices'] = len(self.db.invoices)

        self.list_payment_intents(ListPaymentIntentsParams(limit=100))
        stats['payment_intents'] = len(self.db.payment_intents)

        self.list_prices(ListPricesParams(limit=100))
        stats['prices'] = len(self.db.prices)

        self.list_products(ListProductsParams(limit=100))
        stats['products'] = len(self.db.products)

        self.list_subscriptions(ListSubscriptionsParams(limit=100))
        stats['subscriptions'] = len(self.db.subscriptions)

        return stats
