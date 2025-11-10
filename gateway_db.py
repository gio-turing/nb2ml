"""
GatewayDB - Pydantic BaseModel for Stripe entity collections
Contains all Stripe entities as attributes

This module contains:
1. All entity models (AccountEntity, CustomerEntity, etc.)
2. GatewayDB class - the main data model class
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


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


# ==================== Stripe Entity Models ====================

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


# ==================== Main Data Model Class ====================

class GatewayDB(BaseModel):
    """
    GatewayDB - Main database model for Stripe entities

    This class serves as a Pydantic BaseModel container for all Stripe entities.
    Each entity type is stored as a collection (dict keyed by ID).

    Attributes:
        account: The Stripe account entity
        balance: The current balance entity
        coupons: Collection of coupon entities
        customers: Collection of customer entities
        disputes: Collection of dispute entities
        invoices: Collection of invoice entities
        invoice_items: Collection of invoice item entities
        payment_links: Collection of payment link entities
        payment_intents: Collection of payment intent entities
        prices: Collection of price entities
        products: Collection of product entities
        refunds: Collection of refund entities
        subscriptions: Collection of subscription entities
    """

    # Account and Balance (singular)
    account: Optional[AccountEntity] = Field(
        None,
        description="The Stripe account entity"
    )
    balance: Optional[BalanceEntity] = Field(
        None,
        description="Current account balance"
    )

    # Collections of entities (keyed by ID)
    coupons: Dict[str, CouponEntity] = Field(
        default_factory=dict,
        description="Collection of coupon entities keyed by coupon ID"
    )
    customers: Dict[str, CustomerEntity] = Field(
        default_factory=dict,
        description="Collection of customer entities keyed by customer ID"
    )
    disputes: Dict[str, DisputeEntity] = Field(
        default_factory=dict,
        description="Collection of dispute entities keyed by dispute ID"
    )
    invoices: Dict[str, InvoiceEntity] = Field(
        default_factory=dict,
        description="Collection of invoice entities keyed by invoice ID"
    )
    invoice_items: Dict[str, InvoiceItemEntity] = Field(
        default_factory=dict,
        description="Collection of invoice item entities keyed by item ID"
    )
    payment_links: Dict[str, PaymentLinkEntity] = Field(
        default_factory=dict,
        description="Collection of payment link entities keyed by link ID"
    )
    payment_intents: Dict[str, PaymentIntentEntity] = Field(
        default_factory=dict,
        description="Collection of payment intent entities keyed by intent ID"
    )
    prices: Dict[str, PriceEntity] = Field(
        default_factory=dict,
        description="Collection of price entities keyed by price ID"
    )
    products: Dict[str, ProductEntity] = Field(
        default_factory=dict,
        description="Collection of product entities keyed by product ID"
    )
    refunds: Dict[str, RefundEntity] = Field(
        default_factory=dict,
        description="Collection of refund entities keyed by refund ID"
    )
    subscriptions: Dict[str, SubscriptionEntity] = Field(
        default_factory=dict,
        description="Collection of subscription entities keyed by subscription ID"
    )

    # Metadata for the database
    api_version: Optional[str] = Field(
        "2023-10-16",
        description="Stripe API version"
    )
    livemode: bool = Field(
        False,
        description="Whether this database contains live or test data"
    )
    last_sync: Optional[int] = Field(
        None,
        description="Unix timestamp of last sync with Stripe"
    )

    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
        use_enum_values=True
    )

    # ==================== Helper Methods ====================

    def add_account(self, account: AccountEntity) -> None:
        """Add or update the account entity"""
        self.account = account

    def add_balance(self, balance: BalanceEntity) -> None:
        """Add or update the balance entity"""
        self.balance = balance

    def add_coupon(self, coupon: CouponEntity) -> None:
        """Add a coupon to the collection"""
        self.coupons[coupon.id] = coupon

    def get_coupon(self, coupon_id: str) -> Optional[CouponEntity]:
        """Get a coupon by ID"""
        return self.coupons.get(coupon_id)

    def add_customer(self, customer: CustomerEntity) -> None:
        """Add a customer to the collection"""
        self.customers[customer.id] = customer

    def get_customer(self, customer_id: str) -> Optional[CustomerEntity]:
        """Get a customer by ID"""
        return self.customers.get(customer_id)

    def add_dispute(self, dispute: DisputeEntity) -> None:
        """Add a dispute to the collection"""
        self.disputes[dispute.id] = dispute

    def get_dispute(self, dispute_id: str) -> Optional[DisputeEntity]:
        """Get a dispute by ID"""
        return self.disputes.get(dispute_id)

    def add_invoice(self, invoice: InvoiceEntity) -> None:
        """Add an invoice to the collection"""
        self.invoices[invoice.id] = invoice

    def get_invoice(self, invoice_id: str) -> Optional[InvoiceEntity]:
        """Get an invoice by ID"""
        return self.invoices.get(invoice_id)

    def add_invoice_item(self, item: InvoiceItemEntity) -> None:
        """Add an invoice item to the collection"""
        self.invoice_items[item.id] = item

    def get_invoice_item(self, item_id: str) -> Optional[InvoiceItemEntity]:
        """Get an invoice item by ID"""
        return self.invoice_items.get(item_id)

    def add_payment_link(self, link: PaymentLinkEntity) -> None:
        """Add a payment link to the collection"""
        self.payment_links[link.id] = link

    def get_payment_link(self, link_id: str) -> Optional[PaymentLinkEntity]:
        """Get a payment link by ID"""
        return self.payment_links.get(link_id)

    def add_payment_intent(self, intent: PaymentIntentEntity) -> None:
        """Add a payment intent to the collection"""
        self.payment_intents[intent.id] = intent

    def get_payment_intent(self, intent_id: str) -> Optional[PaymentIntentEntity]:
        """Get a payment intent by ID"""
        return self.payment_intents.get(intent_id)

    def add_price(self, price: PriceEntity) -> None:
        """Add a price to the collection"""
        self.prices[price.id] = price

    def get_price(self, price_id: str) -> Optional[PriceEntity]:
        """Get a price by ID"""
        return self.prices.get(price_id)

    def add_product(self, product: ProductEntity) -> None:
        """Add a product to the collection"""
        self.products[product.id] = product

    def get_product(self, product_id: str) -> Optional[ProductEntity]:
        """Get a product by ID"""
        return self.products.get(product_id)

    def add_refund(self, refund: RefundEntity) -> None:
        """Add a refund to the collection"""
        self.refunds[refund.id] = refund

    def get_refund(self, refund_id: str) -> Optional[RefundEntity]:
        """Get a refund by ID"""
        return self.refunds.get(refund_id)

    def add_subscription(self, subscription: SubscriptionEntity) -> None:
        """Add a subscription to the collection"""
        self.subscriptions[subscription.id] = subscription

    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionEntity]:
        """Get a subscription by ID"""
        return self.subscriptions.get(subscription_id)

    def remove_coupon(self, coupon_id: str) -> bool:
        """Remove a coupon from the collection"""
        if coupon_id in self.coupons:
            del self.coupons[coupon_id]
            return True
        return False

    def remove_customer(self, customer_id: str) -> bool:
        """Remove a customer from the collection"""
        if customer_id in self.customers:
            del self.customers[customer_id]
            return True
        return False

    def remove_subscription(self, subscription_id: str) -> bool:
        """Remove a subscription from the collection"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False

    # ==================== Query Methods ====================

    def list_all_coupons(self) -> List[CouponEntity]:
        """Get all coupons"""
        return list(self.coupons.values())

    def list_all_customers(self) -> List[CustomerEntity]:
        """Get all customers"""
        return list(self.customers.values())

    def list_all_invoices(self) -> List[InvoiceEntity]:
        """Get all invoices"""
        return list(self.invoices.values())

    def list_all_products(self) -> List[ProductEntity]:
        """Get all products"""
        return list(self.products.values())

    def list_all_prices(self) -> List[PriceEntity]:
        """Get all prices"""
        return list(self.prices.values())

    def list_all_subscriptions(self) -> List[SubscriptionEntity]:
        """Get all subscriptions"""
        return list(self.subscriptions.values())

    def find_customers_by_email(self, email: str) -> List[CustomerEntity]:
        """Find customers by email"""
        return [c for c in self.customers.values() if c.email == email]

    def find_active_subscriptions(self) -> List[SubscriptionEntity]:
        """Find all active subscriptions"""
        return [s for s in self.subscriptions.values() if s.status == "active"]

    def find_invoices_by_customer(self, customer_id: str) -> List[InvoiceEntity]:
        """Find all invoices for a specific customer"""
        return [i for i in self.invoices.values() if i.customer == customer_id]

    def find_products_by_active_status(self, active: bool) -> List[ProductEntity]:
        """Find products by active status"""
        return [p for p in self.products.values() if p.active == active]

    # ==================== Statistics ====================

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the database"""
        return {
            "total_coupons": len(self.coupons),
            "total_customers": len(self.customers),
            "total_disputes": len(self.disputes),
            "total_invoices": len(self.invoices),
            "total_invoice_items": len(self.invoice_items),
            "total_payment_links": len(self.payment_links),
            "total_payment_intents": len(self.payment_intents),
            "total_prices": len(self.prices),
            "total_products": len(self.products),
            "total_refunds": len(self.refunds),
            "total_subscriptions": len(self.subscriptions),
        }

    def clear_all(self) -> None:
        """Clear all collections"""
        self.account = None
        self.balance = None
        self.coupons.clear()
        self.customers.clear()
        self.disputes.clear()
        self.invoices.clear()
        self.invoice_items.clear()
        self.payment_links.clear()
        self.payment_intents.clear()
        self.prices.clear()
        self.products.clear()
        self.refunds.clear()
        self.subscriptions.clear()
