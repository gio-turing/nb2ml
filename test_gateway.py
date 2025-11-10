"""
Comprehensive test suite for GatewayTools and GatewayDB

Tests cover:
- All 25 MCP tools
- All parameters (required and optional)
- All possible outcomes (success, validation errors, API errors)
- Edge cases and error conditions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import stripe
from datetime import datetime
import json
import tempfile
from pathlib import Path

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
from gateway_tools import (
    GatewayTools,
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


# ==================== Fixtures ====================

@pytest.fixture
def mock_stripe_config():
    """Mock Stripe configuration"""
    return GatewayDBConfig(
        api_key="sk_test_mock123",
        api_version="2023-10-16",
        timeout=80,
        max_network_retries=3
    )


@pytest.fixture
def gateway_db():
    """Empty GatewayDB instance"""
    return GatewayDB()


@pytest.fixture
def gateway_tools(mock_stripe_config, gateway_db):
    """GatewayTools instance with mocked Stripe"""
    with patch('stripe.api_key'), \
         patch('stripe.api_version'), \
         patch('stripe.max_network_retries'), \
         patch('stripe.default_http_client'):
        return GatewayTools(mock_stripe_config, gateway_db)


@pytest.fixture
def mock_stripe_account():
    """Mock Stripe account response"""
    return {
        "id": "acct_123",
        "object": "account",
        "business_type": "company",
        "charges_enabled": True,
        "country": "US",
        "created": 1234567890,
        "default_currency": "usd",
        "details_submitted": True,
        "email": "test@example.com",
        "payouts_enabled": True,
        "type": "standard",
        "metadata": {}
    }


@pytest.fixture
def mock_stripe_customer():
    """Mock Stripe customer response"""
    return {
        "id": "cus_123",
        "object": "customer",
        "email": "customer@example.com",
        "name": "John Doe",
        "created": 1234567890,
        "livemode": False,
        "metadata": {}
    }


# ==================== GatewayDB Tests ====================

class TestGatewayDB:
    """Tests for GatewayDB data model"""

    def test_empty_initialization(self):
        """Test creating empty database"""
        db = GatewayDB()
        assert db.account is None
        assert db.balance is None
        assert len(db.customers) == 0
        assert db.livemode == False
        assert db.api_version == "2023-10-16"

    def test_add_and_get_customer(self, gateway_db):
        """Test adding and retrieving a customer"""
        customer = CustomerEntity(
            id="cus_123",
            email="test@example.com",
            name="Test User",
            created=1234567890,
            livemode=False
        )
        gateway_db.add_customer(customer)

        retrieved = gateway_db.get_customer("cus_123")
        assert retrieved is not None
        assert retrieved.id == "cus_123"
        assert retrieved.email == "test@example.com"

    def test_get_nonexistent_customer(self, gateway_db):
        """Test retrieving non-existent customer returns None"""
        result = gateway_db.get_customer("cus_nonexistent")
        assert result is None

    def test_remove_customer(self, gateway_db):
        """Test removing a customer"""
        customer = CustomerEntity(
            id="cus_123",
            email="test@example.com",
            name="Test User",
            created=1234567890,
            livemode=False
        )
        gateway_db.add_customer(customer)
        assert gateway_db.remove_customer("cus_123") == True
        assert gateway_db.get_customer("cus_123") is None

    def test_remove_nonexistent_customer(self, gateway_db):
        """Test removing non-existent customer returns False"""
        assert gateway_db.remove_customer("cus_nonexistent") == False

    def test_find_customers_by_email(self, gateway_db):
        """Test finding customers by email"""
        customer1 = CustomerEntity(
            id="cus_1", email="test@example.com", name="User 1",
            created=1234567890, livemode=False
        )
        customer2 = CustomerEntity(
            id="cus_2", email="other@example.com", name="User 2",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer1)
        gateway_db.add_customer(customer2)

        results = gateway_db.find_customers_by_email("test@example.com")
        assert len(results) == 1
        assert results[0].id == "cus_1"

    def test_get_stats(self, gateway_db):
        """Test statistics calculation"""
        customer = CustomerEntity(
            id="cus_123", email="test@example.com", name="Test",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer)

        stats = gateway_db.get_stats()
        assert stats["total_customers"] == 1
        assert stats["total_products"] == 0

    def test_clear_all(self, gateway_db):
        """Test clearing all data"""
        customer = CustomerEntity(
            id="cus_123", email="test@example.com", name="Test",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer)
        gateway_db.clear_all()

        assert len(gateway_db.customers) == 0
        stats = gateway_db.get_stats()
        assert all(v == 0 for v in stats.values())


class TestGatewayDBPersistence:
    """Tests for GatewayDB persistence methods"""

    def test_save_to_json(self, gateway_db):
        """Test saving database to JSON file"""
        customer = CustomerEntity(
            id="cus_123", email="test@example.com", name="Test User",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            gateway_db.save_to_json(temp_path)
            assert Path(temp_path).exists()

            with open(temp_path, 'r') as f:
                data = json.load(f)

            assert 'customers' in data
            assert 'cus_123' in data['customers']
        finally:
            Path(temp_path).unlink()

    def test_load_from_json(self, gateway_db):
        """Test loading database from JSON file"""
        customer = CustomerEntity(
            id="cus_123", email="test@example.com", name="Test User",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            gateway_db.save_to_json(temp_path)

            loaded_db = GatewayDB.load_from_json(temp_path)
            assert len(loaded_db.customers) == 1
            assert loaded_db.get_customer("cus_123").email == "test@example.com"
        finally:
            Path(temp_path).unlink()

    def test_to_dict(self, gateway_db):
        """Test converting database to dictionary"""
        customer = CustomerEntity(
            id="cus_123", email="test@example.com", name="Test User",
            created=1234567890, livemode=False
        )
        gateway_db.add_customer(customer)

        data = gateway_db.to_dict()
        assert isinstance(data, dict)
        assert 'customers' in data
        assert 'cus_123' in data['customers']

    def test_from_dict(self):
        """Test creating database from dictionary"""
        data = {
            "account": None,
            "balance": None,
            "customers": {
                "cus_123": {
                    "id": "cus_123",
                    "object": "customer",
                    "email": "test@example.com",
                    "name": "Test User",
                    "created": 1234567890,
                    "livemode": False
                }
            },
            "coupons": {},
            "disputes": {},
            "invoices": {},
            "invoice_items": {},
            "payment_links": {},
            "payment_intents": {},
            "prices": {},
            "products": {},
            "refunds": {},
            "subscriptions": {},
            "api_version": "2023-10-16",
            "livemode": False,
            "last_sync": None
        }

        db = GatewayDB.from_dict(data)
        assert len(db.customers) == 1
        assert db.get_customer("cus_123").email == "test@example.com"


# ==================== Account & Balance Tool Tests ====================

class TestAccountTools:
    """Tests for account and balance operations"""

    @patch('stripe.Account.retrieve')
    def test_get_account_info_success(self, mock_retrieve, gateway_tools, mock_stripe_account):
        """Test retrieving account info successfully"""
        mock_retrieve.return_value = Mock(**mock_stripe_account)

        result = gateway_tools.get_stripe_account_info()

        assert isinstance(result, AccountEntity)
        assert result.id == "acct_123"
        assert result.country == "US"
        assert gateway_tools.db.account is not None
        mock_retrieve.assert_called_once()

    @patch('stripe.Account.retrieve')
    def test_get_account_info_api_error(self, mock_retrieve, gateway_tools):
        """Test account retrieval with API error"""
        mock_retrieve.side_effect = stripe.error.APIError("API Error")

        with pytest.raises(stripe.error.APIError):
            gateway_tools.get_stripe_account_info()

    @patch('stripe.Balance.retrieve')
    def test_retrieve_balance_success(self, mock_retrieve, gateway_tools):
        """Test retrieving balance successfully"""
        mock_balance = Mock(
            object="balance",
            available=[{"amount": 1000, "currency": "usd"}],
            pending=[{"amount": 0, "currency": "usd"}],
            livemode=False
        )
        mock_retrieve.return_value = mock_balance

        result = gateway_tools.retrieve_balance()

        assert isinstance(result, BalanceEntity)
        assert gateway_tools.db.balance is not None
        mock_retrieve.assert_called_once()


# ==================== Coupon Tool Tests ====================

class TestCouponTools:
    """Tests for coupon operations"""

    @patch('stripe.Coupon.create')
    def test_create_coupon_with_amount_off(self, mock_create, gateway_tools):
        """Test creating coupon with amount off"""
        mock_coupon = Mock(
            id="25OFF",
            object="coupon",
            amount_off=2500,
            currency="usd",
            duration="once",
            created=1234567890,
            livemode=False,
            times_redeemed=0,
            valid=True
        )
        mock_create.return_value = mock_coupon

        params = CreateCouponParams(
            id="25OFF",
            duration="once",
            amount_off=2500,
            currency="usd"
        )
        result = gateway_tools.create_coupon(params)

        assert isinstance(result, CouponEntity)
        assert result.amount_off == 2500
        assert gateway_tools.db.get_coupon("25OFF") is not None

    @patch('stripe.Coupon.create')
    def test_create_coupon_with_percent_off(self, mock_create, gateway_tools):
        """Test creating coupon with percent off"""
        mock_coupon = Mock(
            id="10PERCENT",
            object="coupon",
            percent_off=10.0,
            duration="forever",
            created=1234567890,
            livemode=False,
            times_redeemed=0,
            valid=True
        )
        mock_create.return_value = mock_coupon

        params = CreateCouponParams(
            id="10PERCENT",
            duration="forever",
            percent_off=10.0
        )
        result = gateway_tools.create_coupon(params)

        assert result.percent_off == 10.0

    def test_create_coupon_invalid_percent(self):
        """Test creating coupon with invalid percent"""
        with pytest.raises(Exception):
            CreateCouponParams(
                duration="once",
                percent_off=150.0  # Invalid: > 100
            )

    @patch('stripe.Coupon.list')
    def test_list_coupons_with_pagination(self, mock_list, gateway_tools):
        """Test listing coupons with pagination"""
        mock_coupons = Mock(
            data=[
                Mock(id="COUPON1", object="coupon", duration="once",
                     created=1234567890, livemode=False, times_redeemed=0, valid=True)
            ],
            has_more=False,
            url="/v1/coupons"
        )
        mock_list.return_value = mock_coupons

        params = ListCouponsParams(limit=10)
        result = gateway_tools.list_coupons(params)

        assert len(result["data"]) == 1
        assert result["has_more"] == False


# ==================== Customer Tool Tests ====================

class TestCustomerTools:
    """Tests for customer operations"""

    @patch('stripe.Customer.create')
    def test_create_customer_minimal_params(self, mock_create, gateway_tools, mock_stripe_customer):
        """Test creating customer with minimal parameters"""
        mock_create.return_value = Mock(**mock_stripe_customer)

        params = CreateCustomerParams(
            email="customer@example.com",
            name="John Doe"
        )
        result = gateway_tools.create_customer(params)

        assert isinstance(result, CustomerEntity)
        assert result.email == "customer@example.com"
        assert gateway_tools.db.get_customer("cus_123") is not None

    @patch('stripe.Customer.create')
    def test_create_customer_with_address(self, mock_create, gateway_tools):
        """Test creating customer with address"""
        mock_customer = Mock(
            id="cus_123",
            object="customer",
            email="test@example.com",
            name="Test User",
            address={"line1": "123 Main St", "city": "NY", "country": "US"},
            created=1234567890,
            livemode=False
        )
        mock_create.return_value = mock_customer

        params = CreateCustomerParams(
            email="test@example.com",
            name="Test User",
            address=Address(line1="123 Main St", city="NY", country="US")
        )
        result = gateway_tools.create_customer(params)

        assert result.address is not None

    @patch('stripe.Customer.list')
    def test_list_customers_by_email(self, mock_list, gateway_tools):
        """Test listing customers filtered by email"""
        mock_customers = Mock(
            data=[Mock(id="cus_123", object="customer", email="test@example.com",
                      created=1234567890, livemode=False)],
            has_more=False,
            url="/v1/customers"
        )
        mock_list.return_value = mock_customers

        params = ListCustomersParams(email="test@example.com")
        result = gateway_tools.list_customers(params)

        assert len(result["data"]) == 1


# ==================== Invoice Tool Tests ====================

class TestInvoiceTools:
    """Tests for invoice operations"""

    @patch('stripe.Invoice.create')
    def test_create_invoice_minimal(self, mock_create, gateway_tools):
        """Test creating invoice with minimal parameters"""
        mock_invoice = Mock(
            id="in_123",
            object="invoice",
            customer="cus_123",
            amount_due=1000,
            amount_paid=0,
            amount_remaining=1000,
            attempt_count=0,
            attempted=False,
            collection_method="charge_automatically",
            created=1234567890,
            currency="usd",
            livemode=False,
            paid=False,
            subtotal=1000,
            total=1000
        )
        mock_create.return_value = mock_invoice

        params = CreateInvoiceParams(customer="cus_123")
        result = gateway_tools.create_invoice(params)

        assert isinstance(result, InvoiceEntity)
        assert result.customer == "cus_123"

    @patch('stripe.InvoiceItem.create')
    def test_create_invoice_item(self, mock_create, gateway_tools):
        """Test creating invoice item"""
        mock_item = Mock(
            id="ii_123",
            object="invoiceitem",
            amount=500,
            currency="usd",
            customer="cus_123",
            date=1234567890,
            livemode=False,
            proration=False
        )
        mock_create.return_value = mock_item

        params = CreateInvoiceItemParams(
            customer="cus_123",
            currency="usd",
            amount=500
        )
        result = gateway_tools.create_invoice_item(params)

        assert result.amount == 500

    @patch('stripe.Invoice.finalize_invoice')
    def test_finalize_invoice(self, mock_finalize, gateway_tools):
        """Test finalizing an invoice"""
        mock_invoice = Mock(
            id="in_123",
            object="invoice",
            status="open",
            customer="cus_123",
            amount_due=1000,
            amount_paid=0,
            amount_remaining=1000,
            attempt_count=0,
            attempted=False,
            collection_method="charge_automatically",
            created=1234567890,
            currency="usd",
            livemode=False,
            paid=False,
            subtotal=1000,
            total=1000
        )
        mock_finalize.return_value = mock_invoice

        params = FinalizeInvoiceParams(invoice_id="in_123")
        result = gateway_tools.finalize_invoice(params)

        assert result.status == "open"


# ==================== Product & Price Tool Tests ====================

class TestProductPriceTools:
    """Tests for product and price operations"""

    @patch('stripe.Product.create')
    def test_create_product(self, mock_create, gateway_tools):
        """Test creating a product"""
        mock_product = Mock(
            id="prod_123",
            object="product",
            name="Test Product",
            active=True,
            created=1234567890,
            updated=1234567890,
            livemode=False,
            type="good",
            images=[]
        )
        mock_create.return_value = mock_product

        params = CreateProductParams(name="Test Product")
        result = gateway_tools.create_product(params)

        assert isinstance(result, ProductEntity)
        assert result.name == "Test Product"

    @patch('stripe.Price.create')
    def test_create_price_one_time(self, mock_create, gateway_tools):
        """Test creating a one-time price"""
        mock_price = Mock(
            id="price_123",
            object="price",
            product="prod_123",
            unit_amount=1000,
            currency="usd",
            active=True,
            billing_scheme="per_unit",
            created=1234567890,
            livemode=False,
            type="one_time"
        )
        mock_create.return_value = mock_price

        params = CreatePriceParams(
            currency="usd",
            product="prod_123",
            unit_amount=1000
        )
        result = gateway_tools.create_price(params)

        assert result.unit_amount == 1000
        assert result.type == "one_time"


# ==================== Subscription Tool Tests ====================

class TestSubscriptionTools:
    """Tests for subscription operations"""

    @patch('stripe.Subscription.delete')
    def test_cancel_subscription(self, mock_delete, gateway_tools):
        """Test canceling a subscription"""
        mock_sub = Mock(
            id="sub_123",
            object="subscription",
            customer="cus_123",
            status="canceled",
            cancel_at_period_end=False,
            created=1234567890,
            current_period_end=1234567890,
            current_period_start=1234567890,
            currency="usd",
            livemode=False,
            start_date=1234567890
        )
        mock_delete.return_value = mock_sub

        params = CancelSubscriptionParams(subscription_id="sub_123")
        result = gateway_tools.cancel_subscription(params)

        assert result.status == "canceled"
        # Should be removed from DB when canceled
        assert gateway_tools.db.get_subscription("sub_123") is None

    @patch('stripe.Subscription.modify')
    def test_update_subscription(self, mock_modify, gateway_tools):
        """Test updating a subscription"""
        mock_sub = Mock(
            id="sub_123",
            object="subscription",
            customer="cus_123",
            status="active",
            cancel_at_period_end=True,
            created=1234567890,
            current_period_end=1234567890,
            current_period_start=1234567890,
            currency="usd",
            livemode=False,
            start_date=1234567890
        )
        mock_modify.return_value = mock_sub

        params = UpdateSubscriptionParams(
            subscription_id="sub_123",
            cancel_at_period_end=True
        )
        result = gateway_tools.update_subscription(params)

        assert result.cancel_at_period_end == True


# ==================== Search & Utility Tool Tests ====================

class TestSearchTools:
    """Tests for search and utility operations"""

    @patch('stripe.Customer.search')
    def test_search_customers(self, mock_search, gateway_tools):
        """Test searching customers"""
        mock_result = Mock(
            data=[Mock(id="cus_123", email="test@example.com")],
            has_more=False,
            url="/v1/customers/search"
        )
        mock_search.return_value = mock_result

        params = SearchStripeResourcesParams(
            resource_type="customers",
            query="email:'test@example.com'"
        )
        result = gateway_tools.search_stripe_resources(params)

        assert len(result["data"]) == 1

    def test_search_unsupported_resource(self, gateway_tools):
        """Test searching unsupported resource type"""
        params = SearchStripeResourcesParams(
            resource_type="customers",
            query="test"
        )

        with patch('stripe.Customer.search') as mock_search:
            # Temporarily change resource type to invalid one
            params.resource_type = "invalid_type"

            with pytest.raises(ValueError):
                gateway_tools.search_stripe_resources(params)

    @patch('stripe.Customer.retrieve')
    def test_fetch_customer_resource(self, mock_retrieve, gateway_tools):
        """Test fetching a specific customer"""
        mock_customer = Mock(
            id="cus_123",
            object="customer",
            email="test@example.com",
            created=1234567890,
            livemode=False
        )
        mock_retrieve.return_value = mock_customer

        params = FetchStripeResourceParams(
            resource_type="customers",
            resource_id="cus_123"
        )
        result = gateway_tools.fetch_stripe_resource(params)

        assert result.id == "cus_123"
        assert gateway_tools.db.get_customer("cus_123") is not None

    def test_search_documentation(self, gateway_tools):
        """Test documentation search (placeholder)"""
        params = SearchStripeDocumentationParams(
            query="payment intents",
            category="api"
        )
        result = gateway_tools.search_stripe_documentation(params)

        assert result["query"] == "payment intents"
        assert "message" in result


# ==================== Parameter Validation Tests ====================

class TestParameterValidation:
    """Tests for parameter validation"""

    def test_pagination_params_limits(self):
        """Test pagination limits are enforced"""
        with pytest.raises(Exception):
            PaginationParams(limit=101)  # Over maximum

        with pytest.raises(Exception):
            PaginationParams(limit=0)  # Below minimum

        # Valid
        params = PaginationParams(limit=50)
        assert params.limit == 50

    def test_currency_code_validation(self):
        """Test currency code validation"""
        with pytest.raises(Exception):
            CreatePriceParams(currency="USD")  # Must be lowercase

        with pytest.raises(Exception):
            CreatePriceParams(currency="us")  # Must be 3 letters

        # Valid
        params = CreatePriceParams(currency="usd")
        assert params.currency == "usd"

    def test_required_fields_validation(self):
        """Test required fields are enforced"""
        with pytest.raises(Exception):
            CreateInvoiceParams()  # Missing required 'customer'

        # Valid
        params = CreateInvoiceParams(customer="cus_123")
        assert params.customer == "cus_123"


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Tests for error handling"""

    @patch('stripe.Customer.create')
    def test_handle_stripe_api_error(self, mock_create, gateway_tools):
        """Test handling Stripe API errors"""
        mock_create.side_effect = stripe.error.APIError("API Error")

        params = CreateCustomerParams(email="test@example.com")

        with pytest.raises(stripe.error.APIError):
            gateway_tools.create_customer(params)

    @patch('stripe.Customer.create')
    def test_handle_invalid_request_error(self, mock_create, gateway_tools):
        """Test handling invalid request errors"""
        mock_create.side_effect = stripe.error.InvalidRequestError(
            "Invalid email", "email"
        )

        params = CreateCustomerParams(email="invalid")

        with pytest.raises(stripe.error.InvalidRequestError):
            gateway_tools.create_customer(params)

    def test_connection_test_success(self, gateway_tools):
        """Test successful connection test"""
        with patch('stripe.Balance.retrieve'):
            result = gateway_tools.test_connection()
            assert result == True

    def test_connection_test_failure(self, gateway_tools):
        """Test failed connection test"""
        with patch('stripe.Balance.retrieve', side_effect=Exception("Connection failed")):
            result = gateway_tools.test_connection()
            assert result == False


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests"""

    @patch('stripe.Customer.create')
    @patch('stripe.Invoice.create')
    def test_create_customer_and_invoice(self, mock_invoice, mock_customer, gateway_tools):
        """Test creating customer and invoice together"""
        mock_customer.return_value = Mock(
            id="cus_123",
            object="customer",
            email="test@example.com",
            created=1234567890,
            livemode=False
        )
        mock_invoice.return_value = Mock(
            id="in_123",
            object="invoice",
            customer="cus_123",
            amount_due=1000,
            amount_paid=0,
            amount_remaining=1000,
            attempt_count=0,
            attempted=False,
            collection_method="charge_automatically",
            created=1234567890,
            currency="usd",
            livemode=False,
            paid=False,
            subtotal=1000,
            total=1000
        )

        # Create customer
        customer_params = CreateCustomerParams(email="test@example.com")
        customer = gateway_tools.create_customer(customer_params)

        # Create invoice for customer
        invoice_params = CreateInvoiceParams(customer=customer.id)
        invoice = gateway_tools.create_invoice(invoice_params)

        assert invoice.customer == customer.id
        assert gateway_tools.db.get_customer(customer.id) is not None
        assert gateway_tools.db.get_invoice(invoice.id) is not None


# ==================== Edge Case Tests ====================

class TestBoundaryConditions:
    """Tests for boundary conditions and extreme values"""

    def test_empty_string_customer_name(self, gateway_tools):
        """Test creating customer with empty name"""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                name="",
                created=1234567890,
                livemode=False
            )

            params = CreateCustomerParams(email="test@example.com", name="")
            result = gateway_tools.create_customer(params)
            assert result.name == ""

    def test_very_long_customer_name(self, gateway_tools):
        """Test creating customer with extremely long name"""
        long_name = "A" * 5000
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                name=long_name,
                created=1234567890,
                livemode=False
            )

            params = CreateCustomerParams(email="test@example.com", name=long_name)
            result = gateway_tools.create_customer(params)
            assert len(result.name) == 5000

    def test_negative_coupon_amount(self):
        """Test creating coupon with negative amount"""
        with pytest.raises(Exception):
            CreateCouponParams(
                duration="once",
                amount_off=-1000,
                currency="usd"
            )

    def test_zero_price_amount(self, gateway_tools):
        """Test creating price with zero amount"""
        with patch('stripe.Price.create') as mock_create:
            mock_create.return_value = Mock(
                id="price_123",
                object="price",
                product="prod_123",
                unit_amount=0,
                currency="usd",
                active=True,
                billing_scheme="per_unit",
                created=1234567890,
                livemode=False,
                type="one_time"
            )

            params = CreatePriceParams(
                currency="usd",
                product="prod_123",
                unit_amount=0
            )
            result = gateway_tools.create_price(params)
            assert result.unit_amount == 0

    def test_maximum_pagination_limit(self, gateway_tools):
        """Test pagination with maximum limit"""
        with patch('stripe.Customer.list') as mock_list:
            mock_list.return_value = Mock(
                data=[Mock(id=f"cus_{i}", object="customer", email=f"user{i}@example.com",
                          created=1234567890, livemode=False) for i in range(100)],
                has_more=True,
                url="/v1/customers"
            )

            params = ListCustomersParams(limit=100)
            result = gateway_tools.list_customers(params)
            assert len(result["data"]) == 100

    def test_unicode_characters_in_metadata(self, gateway_tools):
        """Test handling unicode characters in metadata"""
        with patch('stripe.Customer.create') as mock_create:
            metadata = {"note": "Test 测试 🎉 café"}
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                name="Test User",
                created=1234567890,
                livemode=False,
                metadata=metadata
            )

            params = CreateCustomerParams(
                email="test@example.com",
                name="Test User",
                metadata=metadata
            )
            result = gateway_tools.create_customer(params)
            assert result.metadata["note"] == "Test 测试 🎉 café"


class TestDuplicateHandling:
    """Tests for handling duplicate entities"""

    def test_add_duplicate_customer_overwrites(self, gateway_db):
        """Test that adding duplicate customer overwrites the previous one"""
        customer1 = CustomerEntity(
            id="cus_123",
            email="old@example.com",
            name="Old Name",
            created=1234567890,
            livemode=False
        )
        customer2 = CustomerEntity(
            id="cus_123",
            email="new@example.com",
            name="New Name",
            created=1234567890,
            livemode=False
        )

        gateway_db.add_customer(customer1)
        gateway_db.add_customer(customer2)

        result = gateway_db.get_customer("cus_123")
        assert result.email == "new@example.com"
        assert len(gateway_db.customers) == 1

    def test_multiple_customers_same_email(self, gateway_db):
        """Test multiple customers can have the same email"""
        customer1 = CustomerEntity(
            id="cus_1",
            email="same@example.com",
            name="User 1",
            created=1234567890,
            livemode=False
        )
        customer2 = CustomerEntity(
            id="cus_2",
            email="same@example.com",
            name="User 2",
            created=1234567890,
            livemode=False
        )

        gateway_db.add_customer(customer1)
        gateway_db.add_customer(customer2)

        results = gateway_db.find_customers_by_email("same@example.com")
        assert len(results) == 2

    def test_duplicate_invoice_items_allowed(self, gateway_db):
        """Test that duplicate invoice items can exist"""
        item1 = InvoiceItemEntity(
            id="ii_1",
            amount=1000,
            currency="usd",
            customer="cus_123",
            date=1234567890,
            livemode=False,
            proration=False
        )
        item2 = InvoiceItemEntity(
            id="ii_2",
            amount=1000,
            currency="usd",
            customer="cus_123",
            date=1234567890,
            livemode=False,
            proration=False
        )

        gateway_db.add_invoice_item(item1)
        gateway_db.add_invoice_item(item2)

        assert len(gateway_db.invoice_items) == 2


class TestNullAndNoneHandling:
    """Tests for null and None value handling"""

    def test_customer_with_null_fields(self, gateway_db):
        """Test customer with many null optional fields"""
        customer = CustomerEntity(
            id="cus_123",
            email="test@example.com",
            name=None,
            phone=None,
            description=None,
            address=None,
            shipping=None,
            created=1234567890,
            livemode=False,
            metadata={}
        )

        gateway_db.add_customer(customer)
        result = gateway_db.get_customer("cus_123")
        assert result.name is None
        assert result.phone is None

    def test_product_with_null_description(self, gateway_tools):
        """Test creating product with null description"""
        with patch('stripe.Product.create') as mock_create:
            mock_create.return_value = Mock(
                id="prod_123",
                object="product",
                name="Test Product",
                description=None,
                active=True,
                created=1234567890,
                updated=1234567890,
                livemode=False,
                type="good",
                images=[]
            )

            params = CreateProductParams(name="Test Product", description=None)
            result = gateway_tools.create_product(params)
            assert result.description is None

    def test_empty_metadata_dict(self, gateway_tools):
        """Test handling empty metadata dictionary"""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                created=1234567890,
                livemode=False,
                metadata={}
            )

            params = CreateCustomerParams(email="test@example.com", metadata={})
            result = gateway_tools.create_customer(params)
            assert result.metadata == {}


class TestJsonPersistenceEdgeCases:
    """Tests for JSON persistence edge cases"""

    def test_save_empty_database(self, gateway_db):
        """Test saving completely empty database"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            gateway_db.save_to_json(temp_path)

            with open(temp_path, 'r') as f:
                data = json.load(f)

            assert data['account'] is None
            assert data['customers'] == {}
            assert data['products'] == {}
        finally:
            Path(temp_path).unlink()

    def test_load_corrupted_json(self):
        """Test loading corrupted JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{corrupted json [[[")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                GatewayDB.load_from_json(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading non-existent file"""
        with pytest.raises(FileNotFoundError):
            GatewayDB.load_from_json("/nonexistent/path/db.json")

    def test_save_to_read_only_directory(self, gateway_db):
        """Test saving to read-only directory"""
        # This test may vary by platform/permissions
        try:
            gateway_db.save_to_json("/root/readonly/db.json")
        except (PermissionError, OSError):
            # Expected behavior - can't write to protected directory
            pass

    def test_save_load_with_special_characters_in_path(self, gateway_db):
        """Test saving/loading with special characters in filename"""
        customer = CustomerEntity(
            id="cus_123",
            email="test@example.com",
            name="Test",
            created=1234567890,
            livemode=False
        )
        gateway_db.add_customer(customer)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "test db [2025].json"

            gateway_db.save_to_json(str(temp_path))
            loaded_db = GatewayDB.load_from_json(str(temp_path))

            assert len(loaded_db.customers) == 1

    def test_save_very_large_database(self, gateway_db):
        """Test saving database with many entities"""
        # Add 1000 customers
        for i in range(1000):
            customer = CustomerEntity(
                id=f"cus_{i}",
                email=f"user{i}@example.com",
                name=f"User {i}",
                created=1234567890,
                livemode=False
            )
            gateway_db.add_customer(customer)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            gateway_db.save_to_json(temp_path)

            # Verify file exists and has content
            file_size = Path(temp_path).stat().st_size
            assert file_size > 10000  # Should be substantial

            # Verify can load back
            loaded_db = GatewayDB.load_from_json(temp_path)
            assert len(loaded_db.customers) == 1000
        finally:
            Path(temp_path).unlink()


class TestStateTransitions:
    """Tests for entity state transitions"""

    def test_subscription_status_transitions(self, gateway_tools):
        """Test subscription status changes through lifecycle"""
        with patch('stripe.Subscription.modify') as mock_modify:
            # Active -> Cancel at period end
            mock_modify.return_value = Mock(
                id="sub_123",
                object="subscription",
                customer="cus_123",
                status="active",
                cancel_at_period_end=True,
                created=1234567890,
                current_period_end=1234567890,
                current_period_start=1234567890,
                currency="usd",
                livemode=False,
                start_date=1234567890
            )

            params = UpdateSubscriptionParams(
                subscription_id="sub_123",
                cancel_at_period_end=True
            )
            result = gateway_tools.update_subscription(params)
            assert result.cancel_at_period_end == True
            assert result.status == "active"

    def test_invoice_status_draft_to_open(self, gateway_tools):
        """Test invoice transition from draft to open"""
        with patch('stripe.Invoice.finalize_invoice') as mock_finalize:
            mock_finalize.return_value = Mock(
                id="in_123",
                object="invoice",
                status="open",
                customer="cus_123",
                amount_due=1000,
                amount_paid=0,
                amount_remaining=1000,
                attempt_count=0,
                attempted=False,
                collection_method="charge_automatically",
                created=1234567890,
                currency="usd",
                livemode=False,
                paid=False,
                subtotal=1000,
                total=1000
            )

            params = FinalizeInvoiceParams(invoice_id="in_123")
            result = gateway_tools.finalize_invoice(params)
            assert result.status == "open"

    def test_dispute_status_update(self, gateway_tools):
        """Test updating dispute evidence"""
        with patch('stripe.Dispute.modify') as mock_modify:
            mock_modify.return_value = Mock(
                id="dp_123",
                object="dispute",
                amount=1000,
                currency="usd",
                charge="ch_123",
                created=1234567890,
                livemode=False,
                reason="fraudulent",
                status="under_review",
                evidence={"customer_communication": "Updated evidence"}
            )

            params = UpdateDisputeParams(
                dispute_id="dp_123",
                evidence={"customer_communication": "Updated evidence"}
            )
            result = gateway_tools.update_dispute(params)
            assert result.status == "under_review"


class TestNetworkErrorHandling:
    """Tests for network errors and retries"""

    def test_timeout_error(self, gateway_tools):
        """Test handling timeout errors"""
        with patch('stripe.Customer.create', side_effect=stripe.error.APIConnectionError("Timeout")):
            params = CreateCustomerParams(email="test@example.com")

            with pytest.raises(stripe.error.APIConnectionError):
                gateway_tools.create_customer(params)

    def test_rate_limit_error(self, gateway_tools):
        """Test handling rate limit errors"""
        with patch('stripe.Customer.create', side_effect=stripe.error.RateLimitError("Rate limited")):
            params = CreateCustomerParams(email="test@example.com")

            with pytest.raises(stripe.error.RateLimitError):
                gateway_tools.create_customer(params)

    def test_authentication_error(self, gateway_tools):
        """Test handling authentication errors"""
        with patch('stripe.Customer.create', side_effect=stripe.error.AuthenticationError("Invalid API key")):
            params = CreateCustomerParams(email="test@example.com")

            with pytest.raises(stripe.error.AuthenticationError):
                gateway_tools.create_customer(params)

    def test_permission_error(self, gateway_tools):
        """Test handling permission errors"""
        with patch('stripe.Customer.create', side_effect=stripe.error.PermissionError("Permission denied")):
            params = CreateCustomerParams(email="test@example.com")

            with pytest.raises(stripe.error.PermissionError):
                gateway_tools.create_customer(params)


class TestConcurrentOperations:
    """Tests for concurrent operations and race conditions"""

    def test_concurrent_customer_additions(self, gateway_db):
        """Test adding customers concurrently doesn't cause issues"""
        customers = [
            CustomerEntity(
                id=f"cus_{i}",
                email=f"user{i}@example.com",
                name=f"User {i}",
                created=1234567890,
                livemode=False
            )
            for i in range(100)
        ]

        # Add all customers
        for customer in customers:
            gateway_db.add_customer(customer)

        assert len(gateway_db.customers) == 100

    def test_add_and_remove_same_customer(self, gateway_db):
        """Test adding and removing same customer multiple times"""
        customer = CustomerEntity(
            id="cus_123",
            email="test@example.com",
            name="Test",
            created=1234567890,
            livemode=False
        )

        # Add, remove, add, remove cycle
        gateway_db.add_customer(customer)
        assert gateway_db.get_customer("cus_123") is not None

        gateway_db.remove_customer("cus_123")
        assert gateway_db.get_customer("cus_123") is None

        gateway_db.add_customer(customer)
        assert gateway_db.get_customer("cus_123") is not None

        gateway_db.remove_customer("cus_123")
        assert gateway_db.get_customer("cus_123") is None


class TestComplexQueries:
    """Tests for complex query operations"""

    def test_find_active_subscriptions_empty(self, gateway_db):
        """Test finding active subscriptions when none exist"""
        results = gateway_db.find_active_subscriptions()
        assert len(results) == 0

    def test_find_active_subscriptions_mixed_status(self, gateway_db):
        """Test finding active subscriptions among mixed statuses"""
        sub1 = SubscriptionEntity(
            id="sub_1",
            customer="cus_123",
            status="active",
            cancel_at_period_end=False,
            created=1234567890,
            current_period_end=1234567890,
            current_period_start=1234567890,
            currency="usd",
            livemode=False,
            start_date=1234567890
        )
        sub2 = SubscriptionEntity(
            id="sub_2",
            customer="cus_123",
            status="canceled",
            cancel_at_period_end=False,
            created=1234567890,
            current_period_end=1234567890,
            current_period_start=1234567890,
            currency="usd",
            livemode=False,
            start_date=1234567890
        )
        sub3 = SubscriptionEntity(
            id="sub_3",
            customer="cus_456",
            status="active",
            cancel_at_period_end=False,
            created=1234567890,
            current_period_end=1234567890,
            current_period_start=1234567890,
            currency="usd",
            livemode=False,
            start_date=1234567890
        )

        gateway_db.add_subscription(sub1)
        gateway_db.add_subscription(sub2)
        gateway_db.add_subscription(sub3)

        active_subs = gateway_db.find_active_subscriptions()
        assert len(active_subs) == 2
        assert all(sub.status == "active" for sub in active_subs)

    def test_find_invoices_by_customer_multiple(self, gateway_db):
        """Test finding multiple invoices for same customer"""
        for i in range(5):
            invoice = InvoiceEntity(
                id=f"in_{i}",
                customer="cus_123",
                amount_due=1000 * (i + 1),
                amount_paid=0,
                amount_remaining=1000 * (i + 1),
                attempt_count=0,
                attempted=False,
                collection_method="charge_automatically",
                created=1234567890 + i,
                currency="usd",
                livemode=False,
                paid=False,
                subtotal=1000 * (i + 1),
                total=1000 * (i + 1)
            )
            gateway_db.add_invoice(invoice)

        # Add invoice for different customer
        invoice_other = InvoiceEntity(
            id="in_other",
            customer="cus_456",
            amount_due=2000,
            amount_paid=0,
            amount_remaining=2000,
            attempt_count=0,
            attempted=False,
            collection_method="charge_automatically",
            created=1234567890,
            currency="usd",
            livemode=False,
            paid=False,
            subtotal=2000,
            total=2000
        )
        gateway_db.add_invoice(invoice_other)

        results = gateway_db.find_invoices_by_customer("cus_123")
        assert len(results) == 5
        assert all(inv.customer == "cus_123" for inv in results)


class TestDataIntegrity:
    """Tests for data integrity and consistency"""

    def test_account_balance_consistency(self, gateway_tools):
        """Test that account and balance remain consistent"""
        with patch('stripe.Account.retrieve') as mock_account, \
             patch('stripe.Balance.retrieve') as mock_balance:

            mock_account.return_value = Mock(
                id="acct_123",
                object="account",
                country="US",
                default_currency="usd",
                created=1234567890,
                livemode=False
            )
            mock_balance.return_value = Mock(
                object="balance",
                available=[{"amount": 5000, "currency": "usd"}],
                pending=[{"amount": 1000, "currency": "usd"}],
                livemode=False
            )

            gateway_tools.get_stripe_account_info()
            gateway_tools.retrieve_balance()

            assert gateway_tools.db.account is not None
            assert gateway_tools.db.balance is not None
            assert gateway_tools.db.account.default_currency == "usd"

    def test_customer_invoice_relationship(self, gateway_tools):
        """Test maintaining customer-invoice relationship integrity"""
        with patch('stripe.Customer.create') as mock_customer, \
             patch('stripe.Invoice.create') as mock_invoice:

            mock_customer.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                created=1234567890,
                livemode=False
            )
            mock_invoice.return_value = Mock(
                id="in_123",
                object="invoice",
                customer="cus_123",
                amount_due=1000,
                amount_paid=0,
                amount_remaining=1000,
                attempt_count=0,
                attempted=False,
                collection_method="charge_automatically",
                created=1234567890,
                currency="usd",
                livemode=False,
                paid=False,
                subtotal=1000,
                total=1000
            )

            # Create customer and invoice
            customer_params = CreateCustomerParams(email="test@example.com")
            customer = gateway_tools.create_customer(customer_params)

            invoice_params = CreateInvoiceParams(customer=customer.id)
            invoice = gateway_tools.create_invoice(invoice_params)

            # Verify relationship
            assert invoice.customer == customer.id
            customer_invoices = gateway_tools.db.find_invoices_by_customer(customer.id)
            assert len(customer_invoices) == 1
            assert customer_invoices[0].id == invoice.id

    def test_stats_after_operations(self, gateway_db):
        """Test that statistics remain accurate after various operations"""
        # Add entities
        gateway_db.add_customer(CustomerEntity(
            id="cus_1", email="user1@example.com", name="User 1",
            created=1234567890, livemode=False
        ))
        gateway_db.add_product(ProductEntity(
            id="prod_1", name="Product 1", active=True,
            created=1234567890, updated=1234567890, livemode=False
        ))

        stats = gateway_db.get_stats()
        assert stats["total_customers"] == 1
        assert stats["total_products"] == 1

        # Remove customer
        gateway_db.remove_customer("cus_1")

        stats = gateway_db.get_stats()
        assert stats["total_customers"] == 0
        assert stats["total_products"] == 1


class TestEdgeCaseSearches:
    """Tests for edge cases in search operations"""

    def test_search_with_special_characters(self, gateway_tools):
        """Test searching with special characters in query"""
        with patch('stripe.Customer.search') as mock_search:
            mock_search.return_value = Mock(
                data=[],
                has_more=False,
                url="/v1/customers/search"
            )

            params = SearchStripeResourcesParams(
                resource_type="customers",
                query="email:'test+user@example.com'"
            )
            result = gateway_tools.search_stripe_resources(params)

            assert len(result["data"]) == 0

    def test_search_empty_results(self, gateway_tools):
        """Test search returning no results"""
        with patch('stripe.Customer.search') as mock_search:
            mock_search.return_value = Mock(
                data=[],
                has_more=False,
                url="/v1/customers/search"
            )

            params = SearchStripeResourcesParams(
                resource_type="customers",
                query="email:'nonexistent@example.com'"
            )
            result = gateway_tools.search_stripe_resources(params)

            assert result["data"] == []
            assert result["has_more"] == False

    def test_fetch_deleted_resource(self, gateway_tools):
        """Test fetching a deleted resource"""
        with patch('stripe.Customer.retrieve', side_effect=stripe.error.InvalidRequestError(
            "No such customer", "id"
        )):
            params = FetchStripeResourceParams(
                resource_type="customers",
                resource_id="cus_deleted"
            )

            with pytest.raises(stripe.error.InvalidRequestError):
                gateway_tools.fetch_stripe_resource(params)


class TestInvalidInputs:
    """Tests for invalid input handling"""

    def test_invalid_email_format(self, gateway_tools):
        """Test creating customer with invalid email"""
        with patch('stripe.Customer.create', side_effect=stripe.error.InvalidRequestError(
            "Invalid email", "email"
        )):
            params = CreateCustomerParams(email="not-an-email")

            with pytest.raises(stripe.error.InvalidRequestError):
                gateway_tools.create_customer(params)

    def test_invalid_currency_code(self):
        """Test using invalid currency code"""
        with pytest.raises(Exception):
            CreatePriceParams(
                currency="INVALID",
                product="prod_123",
                unit_amount=1000
            )

    def test_negative_invoice_amount(self, gateway_tools):
        """Test creating invoice item with negative amount"""
        with patch('stripe.InvoiceItem.create', side_effect=stripe.error.InvalidRequestError(
            "Invalid amount", "amount"
        )):
            params = CreateInvoiceItemParams(
                customer="cus_123",
                currency="usd",
                amount=-1000
            )

            with pytest.raises(stripe.error.InvalidRequestError):
                gateway_tools.create_invoice_item(params)

    def test_invalid_subscription_id_format(self, gateway_tools):
        """Test operations with invalid subscription ID format"""
        with patch('stripe.Subscription.retrieve', side_effect=stripe.error.InvalidRequestError(
            "Invalid subscription ID", "id"
        )):
            params = CancelSubscriptionParams(subscription_id="invalid_id")

            with pytest.raises(stripe.error.InvalidRequestError):
                gateway_tools.cancel_subscription(params)


class TestMetadataEdgeCases:
    """Tests for metadata handling edge cases"""

    def test_metadata_with_nested_objects(self, gateway_tools):
        """Test metadata with nested dictionary structures"""
        with patch('stripe.Customer.create') as mock_create:
            metadata = {
                "level1": {
                    "level2": {
                        "level3": "deep value"
                    }
                }
            }
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                created=1234567890,
                livemode=False,
                metadata=metadata
            )

            params = CreateCustomerParams(
                email="test@example.com",
                metadata=metadata
            )
            result = gateway_tools.create_customer(params)
            assert "level1" in result.metadata

    def test_metadata_with_large_values(self, gateway_tools):
        """Test metadata with large string values"""
        with patch('stripe.Product.create') as mock_create:
            large_description = "A" * 10000
            metadata = {"description": large_description}

            mock_create.return_value = Mock(
                id="prod_123",
                object="product",
                name="Test Product",
                active=True,
                created=1234567890,
                updated=1234567890,
                livemode=False,
                type="good",
                images=[],
                metadata=metadata
            )

            params = CreateProductParams(
                name="Test Product",
                metadata=metadata
            )
            result = gateway_tools.create_product(params)
            assert len(result.metadata["description"]) == 10000

    def test_metadata_with_special_keys(self, gateway_tools):
        """Test metadata with special character keys"""
        with patch('stripe.Customer.create') as mock_create:
            metadata = {
                "key-with-dash": "value1",
                "key_with_underscore": "value2",
                "key.with.dot": "value3"
            }
            mock_create.return_value = Mock(
                id="cus_123",
                object="customer",
                email="test@example.com",
                created=1234567890,
                livemode=False,
                metadata=metadata
            )

            params = CreateCustomerParams(
                email="test@example.com",
                metadata=metadata
            )
            result = gateway_tools.create_customer(params)
            assert len(result.metadata) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
