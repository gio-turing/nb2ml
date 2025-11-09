"""
GatewayTools - MCP tool implementations for Stripe API operations
Interacts with Stripe API and manages GatewayDB
"""

from typing import Any, Dict
import stripe
import time
from gateway_db import GatewayDB
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
from models import (
    GatewayDBConfig,
    CreateCouponParams,
    ListCouponsParams,
    CreateCustomerParams,
    ListCustomersParams,
    ListDisputesParams,
    UpdateDisputeParams,
    CreateInvoiceParams,
    CreateInvoiceItemParams,
    FinalizeInvoiceParams,
    ListInvoicesParams,
    CreatePaymentLinkParams,
    ListPaymentIntentsParams,
    CreatePriceParams,
    ListPricesParams,
    CreateProductParams,
    ListProductsParams,
    CreateRefundParams,
    CancelSubscriptionParams,
    ListSubscriptionsParams,
    UpdateSubscriptionParams,
    SearchStripeResourcesParams,
    FetchStripeResourceParams,
    SearchStripeDocumentationParams,
)


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
        stripe.default_http_client = stripe.http_client.RequestsClient(timeout=config.timeout)

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
