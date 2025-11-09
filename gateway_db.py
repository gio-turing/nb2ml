"""
GatewayDB - Pydantic BaseModel for Stripe entity collections
Contains all Stripe entities as attributes
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from entities import (
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
)


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
