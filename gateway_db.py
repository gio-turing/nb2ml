"""
GatewayDB - Stripe API Gateway Database Class with Pydantic Models
Encapsulates all Stripe API operations for payment processing and management
"""

from typing import Any, Dict
import stripe
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


class GatewayDB:
    """
    GatewayDB - Main class for Stripe API operations

    This class encapsulates all Stripe API operations including:
    - Account and Balance management
    - Coupon operations
    - Customer management
    - Dispute handling
    - Invoice operations
    - Payment Links
    - PaymentIntents
    - Price management
    - Product catalog
    - Refunds
    - Subscription management
    - Search and utility functions

    All methods use Pydantic models for input validation and type safety.
    """

    def __init__(self, config: GatewayDBConfig):
        """
        Initialize GatewayDB with Stripe configuration

        Args:
            config: GatewayDBConfig instance with API credentials
        """
        self.config = config
        stripe.api_key = config.api_key
        stripe.api_version = config.api_version
        stripe.max_network_retries = config.max_network_retries
        stripe.default_http_client = stripe.http_client.RequestsClient(timeout=config.timeout)

    # ==================== Account Operations ====================

    def get_stripe_account_info(self) -> stripe.Account:
        """
        Retrieves the details of the Stripe account

        Returns:
            stripe.Account: The account object
        """
        return stripe.Account.retrieve()

    # ==================== Balance Operations ====================

    def retrieve_balance(self) -> stripe.Balance:
        """
        Retrieves the current account balance

        Returns:
            stripe.Balance: The balance object
        """
        return stripe.Balance.retrieve()

    # ==================== Coupon Operations ====================

    def create_coupon(self, params: CreateCouponParams) -> stripe.Coupon:
        """
        Creates a new coupon object

        Args:
            params: CreateCouponParams with coupon details

        Returns:
            stripe.Coupon: The created coupon object
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Coupon.create(**data)

    def list_coupons(self, params: ListCouponsParams = ListCouponsParams()) -> stripe.ListObject:
        """
        Returns a list of your coupons

        Args:
            params: ListCouponsParams with filtering options

        Returns:
            stripe.ListObject: List of coupons
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Coupon.list(**data)

    # ==================== Customer Operations ====================

    def create_customer(self, params: CreateCustomerParams = CreateCustomerParams()) -> stripe.Customer:
        """
        Creates a new customer object

        Args:
            params: CreateCustomerParams with customer details

        Returns:
            stripe.Customer: The created customer object
        """
        data = params.model_dump(exclude_none=True)
        # Convert nested Pydantic models to dicts
        if 'address' in data and data['address']:
            data['address'] = params.address.model_dump(exclude_none=True) if params.address else None
        if 'shipping' in data and data['shipping']:
            data['shipping'] = params.shipping.model_dump(exclude_none=True) if params.shipping else None
        if 'invoice_settings' in data and data['invoice_settings']:
            data['invoice_settings'] = params.invoice_settings.model_dump(exclude_none=True) if params.invoice_settings else None
        if 'tax' in data and data['tax']:
            data['tax'] = params.tax.model_dump(exclude_none=True) if params.tax else None

        return stripe.Customer.create(**data)

    def list_customers(self, params: ListCustomersParams = ListCustomersParams()) -> stripe.ListObject:
        """
        Returns a list of your customers

        Args:
            params: ListCustomersParams with filtering options

        Returns:
            stripe.ListObject: List of customers
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Customer.list(**data)

    # ==================== Dispute Operations ====================

    def list_disputes(self, params: ListDisputesParams = ListDisputesParams()) -> stripe.ListObject:
        """
        Returns a list of your disputes

        Args:
            params: ListDisputesParams with filtering options

        Returns:
            stripe.ListObject: List of disputes
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Dispute.list(**data)

    def update_dispute(self, params: UpdateDisputeParams) -> stripe.Dispute:
        """
        Updates a specific dispute

        Args:
            params: UpdateDisputeParams with dispute update details

        Returns:
            stripe.Dispute: The updated dispute object
        """
        dispute_id = params.dispute_id
        data = params.model_dump(exclude_none=True, exclude={'dispute_id'})

        # Convert nested Pydantic models to dicts
        if 'evidence' in data and data['evidence']:
            data['evidence'] = params.evidence.model_dump(exclude_none=True) if params.evidence else None

        return stripe.Dispute.modify(dispute_id, **data)

    # ==================== Invoice Operations ====================

    def create_invoice(self, params: CreateInvoiceParams) -> stripe.Invoice:
        """
        Creates a draft invoice for a given customer

        Args:
            params: CreateInvoiceParams with invoice details

        Returns:
            stripe.Invoice: The created invoice object
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Invoice.create(**data)

    def create_invoice_item(self, params: CreateInvoiceItemParams) -> stripe.InvoiceItem:
        """
        Creates an invoice item

        Args:
            params: CreateInvoiceItemParams with invoice item details

        Returns:
            stripe.InvoiceItem: The created invoice item object
        """
        data = params.model_dump(exclude_none=True)
        return stripe.InvoiceItem.create(**data)

    def finalize_invoice(self, params: FinalizeInvoiceParams) -> stripe.Invoice:
        """
        Finalizes a draft invoice

        Args:
            params: FinalizeInvoiceParams with finalization details

        Returns:
            stripe.Invoice: The finalized invoice object
        """
        invoice_id = params.invoice_id
        data = params.model_dump(exclude_none=True, exclude={'invoice_id'})
        return stripe.Invoice.finalize_invoice(invoice_id, **data)

    def list_invoices(self, params: ListInvoicesParams = ListInvoicesParams()) -> stripe.ListObject:
        """
        Returns a list of your invoices

        Args:
            params: ListInvoicesParams with filtering options

        Returns:
            stripe.ListObject: List of invoices
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Invoice.list(**data)

    # ==================== Payment Link Operations ====================

    def create_payment_link(self, params: CreatePaymentLinkParams) -> stripe.PaymentLink:
        """
        Creates a payment link

        Args:
            params: CreatePaymentLinkParams with payment link details

        Returns:
            stripe.PaymentLink: The created payment link object
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

        return stripe.PaymentLink.create(**data)

    # ==================== PaymentIntent Operations ====================

    def list_payment_intents(self, params: ListPaymentIntentsParams = ListPaymentIntentsParams()) -> stripe.ListObject:
        """
        Returns a list of PaymentIntents

        Args:
            params: ListPaymentIntentsParams with filtering options

        Returns:
            stripe.ListObject: List of PaymentIntents
        """
        data = params.model_dump(exclude_none=True)
        return stripe.PaymentIntent.list(**data)

    # ==================== Price Operations ====================

    def create_price(self, params: CreatePriceParams) -> stripe.Price:
        """
        Creates a new price for an existing product

        Args:
            params: CreatePriceParams with price details

        Returns:
            stripe.Price: The created price object
        """
        data = params.model_dump(exclude_none=True)

        # Convert nested models
        if 'recurring' in data and params.recurring:
            data['recurring'] = params.recurring.model_dump(exclude_none=True)

        if 'product_data' in data and params.product_data:
            data['product_data'] = params.product_data.model_dump(exclude_none=True)

        if 'tiers' in data and params.tiers:
            data['tiers'] = [tier.model_dump(exclude_none=True) for tier in params.tiers]

        return stripe.Price.create(**data)

    def list_prices(self, params: ListPricesParams = ListPricesParams()) -> stripe.ListObject:
        """
        Returns a list of your prices

        Args:
            params: ListPricesParams with filtering options

        Returns:
            stripe.ListObject: List of prices
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Price.list(**data)

    # ==================== Product Operations ====================

    def create_product(self, params: CreateProductParams) -> stripe.Product:
        """
        Creates a new product object

        Args:
            params: CreateProductParams with product details

        Returns:
            stripe.Product: The created product object
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

        return stripe.Product.create(**data)

    def list_products(self, params: ListProductsParams = ListProductsParams()) -> stripe.ListObject:
        """
        Returns a list of your products

        Args:
            params: ListProductsParams with filtering options

        Returns:
            stripe.ListObject: List of products
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Product.list(**data)

    # ==================== Refund Operations ====================

    def create_refund(self, params: CreateRefundParams) -> stripe.Refund:
        """
        Creates a refund for a charge

        Args:
            params: CreateRefundParams with refund details

        Returns:
            stripe.Refund: The created refund object
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Refund.create(**data)

    # ==================== Subscription Operations ====================

    def cancel_subscription(self, params: CancelSubscriptionParams) -> stripe.Subscription:
        """
        Cancels a customer's subscription

        Args:
            params: CancelSubscriptionParams with cancellation details

        Returns:
            stripe.Subscription: The canceled subscription object
        """
        subscription_id = params.subscription_id
        data = params.model_dump(exclude_none=True, exclude={'subscription_id'})

        # Convert nested models
        if 'cancellation_details' in data and params.cancellation_details:
            data['cancellation_details'] = params.cancellation_details.model_dump(exclude_none=True)

        return stripe.Subscription.delete(subscription_id, **data)

    def list_subscriptions(self, params: ListSubscriptionsParams = ListSubscriptionsParams()) -> stripe.ListObject:
        """
        Returns a list of your subscriptions

        Args:
            params: ListSubscriptionsParams with filtering options

        Returns:
            stripe.ListObject: List of subscriptions
        """
        data = params.model_dump(exclude_none=True)
        return stripe.Subscription.list(**data)

    def update_subscription(self, params: UpdateSubscriptionParams) -> stripe.Subscription:
        """
        Updates an existing subscription

        Args:
            params: UpdateSubscriptionParams with update details

        Returns:
            stripe.Subscription: The updated subscription object
        """
        subscription_id = params.subscription_id
        data = params.model_dump(exclude_none=True, exclude={'subscription_id'})

        # Convert items list
        if 'items' in data and params.items:
            data['items'] = [item.model_dump(exclude_none=True) for item in params.items]

        return stripe.Subscription.modify(subscription_id, **data)

    # ==================== Search and Utility Operations ====================

    def search_stripe_resources(self, params: SearchStripeResourcesParams) -> stripe.SearchResult:
        """
        Searches across Stripe resources using a query string

        Args:
            params: SearchStripeResourcesParams with search criteria

        Returns:
            stripe.SearchResult: Search results
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

        return resource_map[resource_type].search(**data)

    def fetch_stripe_resource(self, params: FetchStripeResourceParams) -> Any:
        """
        Fetches a specific Stripe resource by ID

        Args:
            params: FetchStripeResourceParams with resource details

        Returns:
            Stripe object: The requested resource
        """
        resource_type = params.resource_type
        resource_id = params.resource_id

        resource_map = {
            "accounts": stripe.Account,
            "charges": stripe.Charge,
            "customers": stripe.Customer,
            "invoices": stripe.Invoice,
            "payment_intents": stripe.PaymentIntent,
            "payment_methods": stripe.PaymentMethod,
            "prices": stripe.Price,
            "products": stripe.Product,
            "refunds": stripe.Refund,
            "disputes": stripe.Dispute,
            "coupons": stripe.Coupon,
            "subscriptions": stripe.Subscription,
        }

        if resource_type == "balances":
            return stripe.Balance.retrieve()

        if resource_type not in resource_map:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        return resource_map[resource_type].retrieve(resource_id)

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
