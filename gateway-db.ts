/**
 * GatewayDB - Stripe API Gateway Database Class
 * Encapsulates all Stripe API operations for payment processing and management
 */

import Stripe from 'stripe';

export interface GatewayDBConfig {
  apiKey: string;
  apiVersion?: string;
  timeout?: number;
  maxNetworkRetries?: number;
}

export interface PaginationParams {
  limit?: number;
  starting_after?: string;
  ending_before?: string;
}

export interface DateRangeFilter {
  gt?: number;
  gte?: number;
  lt?: number;
  lte?: number;
}

export interface CreateCouponParams {
  id?: string;
  duration: 'forever' | 'once' | 'repeating';
  amount_off?: number;
  percent_off?: number;
  currency?: string;
  duration_in_months?: number;
  max_redemptions?: number;
  name?: string;
  metadata?: Record<string, string>;
}

export interface CreateCustomerParams {
  email?: string;
  name?: string;
  description?: string;
  phone?: string;
  address?: Stripe.AddressParam;
  payment_method?: string;
  invoice_settings?: Stripe.CustomerCreateParams.InvoiceSettings;
  metadata?: Record<string, string>;
  shipping?: Stripe.CustomerCreateParams.Shipping;
  tax?: Stripe.CustomerCreateParams.Tax;
}

export interface ListCustomersParams extends PaginationParams {
  email?: string;
  created?: DateRangeFilter | number;
}

export interface ListDisputesParams extends PaginationParams {
  charge?: string;
  payment_intent?: string;
  created?: DateRangeFilter | number;
}

export interface UpdateDisputeParams {
  dispute_id: string;
  evidence?: Stripe.DisputeUpdateParams.Evidence;
  metadata?: Record<string, string>;
  submit?: boolean;
}

export interface CreateInvoiceParams {
  customer: string;
  auto_advance?: boolean;
  collection_method?: 'charge_automatically' | 'send_invoice';
  description?: string;
  due_date?: number;
  currency?: string;
  days_until_due?: number;
  metadata?: Record<string, string>;
  subscription?: string;
}

export interface CreateInvoiceItemParams {
  customer: string;
  amount?: number;
  currency: string;
  description?: string;
  invoice?: string;
  price?: string;
  quantity?: number;
  metadata?: Record<string, string>;
  subscription?: string;
}

export interface FinalizeInvoiceParams {
  invoice_id: string;
  auto_advance?: boolean;
}

export interface ListInvoicesParams extends PaginationParams {
  customer?: string;
  subscription?: string;
  status?: 'draft' | 'open' | 'paid' | 'uncollectible' | 'void';
  created?: DateRangeFilter | number;
}

export interface CreatePaymentLinkParams {
  line_items: Array<{
    price: string;
    quantity: number;
  }>;
  after_completion?: Stripe.PaymentLinkCreateParams.AfterCompletion;
  allow_promotion_codes?: boolean;
  application_fee_amount?: number;
  application_fee_percent?: number;
  automatic_tax?: Stripe.PaymentLinkCreateParams.AutomaticTax;
  billing_address_collection?: 'auto' | 'required';
  currency?: string;
  customer_creation?: 'always' | 'if_required';
  metadata?: Record<string, string>;
  payment_method_types?: string[];
  phone_number_collection?: Stripe.PaymentLinkCreateParams.PhoneNumberCollection;
  shipping_address_collection?: Stripe.PaymentLinkCreateParams.ShippingAddressCollection;
  submit_type?: 'auto' | 'book' | 'donate' | 'pay';
}

export interface ListPaymentIntentsParams extends PaginationParams {
  customer?: string;
  created?: DateRangeFilter | number;
}

export interface CreatePriceParams {
  product?: string;
  currency: string;
  unit_amount?: number;
  unit_amount_decimal?: string;
  active?: boolean;
  billing_scheme?: 'per_unit' | 'tiered';
  currency_options?: Record<string, Stripe.PriceCreateParams.CurrencyOptions>;
  custom_unit_amount?: Stripe.PriceCreateParams.CustomUnitAmount;
  lookup_key?: string;
  metadata?: Record<string, string>;
  nickname?: string;
  product_data?: Stripe.PriceCreateParams.ProductData;
  recurring?: Stripe.PriceCreateParams.Recurring;
  tax_behavior?: 'exclusive' | 'inclusive' | 'unspecified';
  tiers?: Stripe.PriceCreateParams.Tier[];
  tiers_mode?: 'graduated' | 'volume';
  transfer_lookup_key?: boolean;
}

export interface ListPricesParams extends PaginationParams {
  product?: string;
  active?: boolean;
  currency?: string;
  type?: 'one_time' | 'recurring';
  created?: DateRangeFilter | number;
}

export interface CreateProductParams {
  name: string;
  active?: boolean;
  description?: string;
  default_price_data?: Stripe.ProductCreateParams.DefaultPriceData;
  features?: Array<{ name: string }>;
  images?: string[];
  metadata?: Record<string, string>;
  package_dimensions?: Stripe.ProductCreateParams.PackageDimensions;
  shippable?: boolean;
  statement_descriptor?: string;
  tax_code?: string;
  unit_label?: string;
  url?: string;
}

export interface ListProductsParams extends PaginationParams {
  active?: boolean;
  ids?: string[];
  shippable?: boolean;
  url?: string;
  created?: DateRangeFilter | number;
}

export interface CreateRefundParams {
  charge?: string;
  payment_intent?: string;
  amount?: number;
  reason?: 'duplicate' | 'fraudulent' | 'requested_by_customer';
  refund_application_fee?: boolean;
  reverse_transfer?: boolean;
  metadata?: Record<string, string>;
}

export interface CancelSubscriptionParams {
  subscription_id: string;
  invoice_now?: boolean;
  prorate?: boolean;
  cancellation_details?: {
    comment?: string;
    feedback?: string;
  };
}

export interface ListSubscriptionsParams extends PaginationParams {
  customer?: string;
  price?: string;
  status?: 'active' | 'past_due' | 'unpaid' | 'canceled' | 'incomplete' | 'incomplete_expired' | 'trialing' | 'all' | 'ended';
  created?: DateRangeFilter | number;
}

export interface UpdateSubscriptionParams {
  subscription_id: string;
  cancel_at_period_end?: boolean;
  default_payment_method?: string;
  items?: Array<{
    id?: string;
    price?: string;
    quantity?: number;
  }>;
  proration_behavior?: 'create_prorations' | 'none' | 'always_invoice';
  proration_date?: number;
  metadata?: Record<string, string>;
  payment_behavior?: 'allow_incomplete' | 'default_incomplete' | 'error_if_incomplete' | 'pending_if_incomplete';
  billing_cycle_anchor?: 'now' | 'unchanged';
  trial_end?: number | 'now';
}

export interface SearchStripeResourcesParams {
  resource_type: 'charges' | 'customers' | 'invoices' | 'payment_intents' | 'prices' | 'products' | 'subscriptions';
  query: string;
  limit?: number;
  page?: string;
}

export interface FetchStripeResourceParams {
  resource_type: 'charges' | 'customers' | 'invoices' | 'payment_intents' | 'prices' | 'products' | 'subscriptions' | 'payment_methods' | 'refunds' | 'disputes' | 'coupons' | 'balances' | 'accounts';
  resource_id: string;
}

export interface SearchStripeDocumentationParams {
  query: string;
  category?: 'api' | 'guides' | 'webhooks' | 'integrations' | 'all';
  limit?: number;
}

/**
 * GatewayDB - Main class for Stripe API operations
 */
export class GatewayDB {
  private stripe: Stripe;
  private config: GatewayDBConfig;

  constructor(config: GatewayDBConfig) {
    this.config = config;
    this.stripe = new Stripe(config.apiKey, {
      apiVersion: '2023-10-16',
      timeout: config.timeout,
      maxNetworkRetries: config.maxNetworkRetries || 3,
    });
  }

  // ==================== Account Operations ====================

  /**
   * Retrieves the details of the Stripe account
   */
  async getStripeAccountInfo(): Promise<Stripe.Account> {
    return await this.stripe.account.retrieve();
  }

  // ==================== Balance Operations ====================

  /**
   * Retrieves the current account balance
   */
  async retrieveBalance(): Promise<Stripe.Balance> {
    return await this.stripe.balance.retrieve();
  }

  // ==================== Coupon Operations ====================

  /**
   * Creates a new coupon object
   */
  async createCoupon(params: CreateCouponParams): Promise<Stripe.Coupon> {
    return await this.stripe.coupons.create(params as Stripe.CouponCreateParams);
  }

  /**
   * Returns a list of your coupons
   */
  async listCoupons(params?: PaginationParams & { created?: DateRangeFilter | number }): Promise<Stripe.ApiList<Stripe.Coupon>> {
    return await this.stripe.coupons.list(params);
  }

  // ==================== Customer Operations ====================

  /**
   * Creates a new customer object
   */
  async createCustomer(params?: CreateCustomerParams): Promise<Stripe.Customer> {
    return await this.stripe.customers.create(params as Stripe.CustomerCreateParams);
  }

  /**
   * Returns a list of your customers
   */
  async listCustomers(params?: ListCustomersParams): Promise<Stripe.ApiList<Stripe.Customer>> {
    return await this.stripe.customers.list(params as Stripe.CustomerListParams);
  }

  // ==================== Dispute Operations ====================

  /**
   * Returns a list of your disputes
   */
  async listDisputes(params?: ListDisputesParams): Promise<Stripe.ApiList<Stripe.Dispute>> {
    return await this.stripe.disputes.list(params as Stripe.DisputeListParams);
  }

  /**
   * Updates a specific dispute
   */
  async updateDispute(params: UpdateDisputeParams): Promise<Stripe.Dispute> {
    const { dispute_id, ...updateParams } = params;
    return await this.stripe.disputes.update(dispute_id, updateParams as Stripe.DisputeUpdateParams);
  }

  // ==================== Invoice Operations ====================

  /**
   * Creates a draft invoice for a given customer
   */
  async createInvoice(params: CreateInvoiceParams): Promise<Stripe.Invoice> {
    return await this.stripe.invoices.create(params as Stripe.InvoiceCreateParams);
  }

  /**
   * Creates an invoice item
   */
  async createInvoiceItem(params: CreateInvoiceItemParams): Promise<Stripe.InvoiceItem> {
    return await this.stripe.invoiceItems.create(params as Stripe.InvoiceItemCreateParams);
  }

  /**
   * Finalizes a draft invoice
   */
  async finalizeInvoice(params: FinalizeInvoiceParams): Promise<Stripe.Invoice> {
    const { invoice_id, auto_advance } = params;
    return await this.stripe.invoices.finalizeInvoice(invoice_id, { auto_advance });
  }

  /**
   * Returns a list of your invoices
   */
  async listInvoices(params?: ListInvoicesParams): Promise<Stripe.ApiList<Stripe.Invoice>> {
    return await this.stripe.invoices.list(params as Stripe.InvoiceListParams);
  }

  // ==================== Payment Link Operations ====================

  /**
   * Creates a payment link
   */
  async createPaymentLink(params: CreatePaymentLinkParams): Promise<Stripe.PaymentLink> {
    return await this.stripe.paymentLinks.create(params as Stripe.PaymentLinkCreateParams);
  }

  // ==================== PaymentIntent Operations ====================

  /**
   * Returns a list of PaymentIntents
   */
  async listPaymentIntents(params?: ListPaymentIntentsParams): Promise<Stripe.ApiList<Stripe.PaymentIntent>> {
    return await this.stripe.paymentIntents.list(params as Stripe.PaymentIntentListParams);
  }

  // ==================== Price Operations ====================

  /**
   * Creates a new price for an existing product
   */
  async createPrice(params: CreatePriceParams): Promise<Stripe.Price> {
    return await this.stripe.prices.create(params as Stripe.PriceCreateParams);
  }

  /**
   * Returns a list of your prices
   */
  async listPrices(params?: ListPricesParams): Promise<Stripe.ApiList<Stripe.Price>> {
    return await this.stripe.prices.list(params as Stripe.PriceListParams);
  }

  // ==================== Product Operations ====================

  /**
   * Creates a new product object
   */
  async createProduct(params: CreateProductParams): Promise<Stripe.Product> {
    return await this.stripe.products.create(params as Stripe.ProductCreateParams);
  }

  /**
   * Returns a list of your products
   */
  async listProducts(params?: ListProductsParams): Promise<Stripe.ApiList<Stripe.Product>> {
    return await this.stripe.products.list(params as Stripe.ProductListParams);
  }

  // ==================== Refund Operations ====================

  /**
   * Creates a refund for a charge
   */
  async createRefund(params: CreateRefundParams): Promise<Stripe.Refund> {
    return await this.stripe.refunds.create(params as Stripe.RefundCreateParams);
  }

  // ==================== Subscription Operations ====================

  /**
   * Cancels a customer's subscription
   */
  async cancelSubscription(params: CancelSubscriptionParams): Promise<Stripe.Subscription> {
    const { subscription_id, ...cancelParams } = params;
    return await this.stripe.subscriptions.cancel(subscription_id, cancelParams as Stripe.SubscriptionCancelParams);
  }

  /**
   * Returns a list of your subscriptions
   */
  async listSubscriptions(params?: ListSubscriptionsParams): Promise<Stripe.ApiList<Stripe.Subscription>> {
    return await this.stripe.subscriptions.list(params as Stripe.SubscriptionListParams);
  }

  /**
   * Updates an existing subscription
   */
  async updateSubscription(params: UpdateSubscriptionParams): Promise<Stripe.Subscription> {
    const { subscription_id, ...updateParams } = params;
    return await this.stripe.subscriptions.update(subscription_id, updateParams as Stripe.SubscriptionUpdateParams);
  }

  // ==================== Search and Utility Operations ====================

  /**
   * Searches across Stripe resources using a query string
   */
  async searchStripeResources(params: SearchStripeResourcesParams): Promise<Stripe.ApiSearchResult<any>> {
    const { resource_type, query, limit, page } = params;

    const searchParams: Stripe.SearchParams = {
      query,
      limit,
      page,
    };

    switch (resource_type) {
      case 'charges':
        return await this.stripe.charges.search(searchParams);
      case 'customers':
        return await this.stripe.customers.search(searchParams);
      case 'invoices':
        return await this.stripe.invoices.search(searchParams);
      case 'payment_intents':
        return await this.stripe.paymentIntents.search(searchParams);
      case 'prices':
        return await this.stripe.prices.search(searchParams);
      case 'products':
        return await this.stripe.products.search(searchParams);
      case 'subscriptions':
        return await this.stripe.subscriptions.search(searchParams);
      default:
        throw new Error(`Unsupported resource type: ${resource_type}`);
    }
  }

  /**
   * Fetches a specific Stripe resource by ID
   */
  async fetchStripeResource(params: FetchStripeResourceParams): Promise<any> {
    const { resource_type, resource_id } = params;

    switch (resource_type) {
      case 'accounts':
        return await this.stripe.accounts.retrieve(resource_id);
      case 'charges':
        return await this.stripe.charges.retrieve(resource_id);
      case 'customers':
        return await this.stripe.customers.retrieve(resource_id);
      case 'invoices':
        return await this.stripe.invoices.retrieve(resource_id);
      case 'payment_intents':
        return await this.stripe.paymentIntents.retrieve(resource_id);
      case 'payment_methods':
        return await this.stripe.paymentMethods.retrieve(resource_id);
      case 'prices':
        return await this.stripe.prices.retrieve(resource_id);
      case 'products':
        return await this.stripe.products.retrieve(resource_id);
      case 'refunds':
        return await this.stripe.refunds.retrieve(resource_id);
      case 'disputes':
        return await this.stripe.disputes.retrieve(resource_id);
      case 'coupons':
        return await this.stripe.coupons.retrieve(resource_id);
      case 'subscriptions':
        return await this.stripe.subscriptions.retrieve(resource_id);
      case 'balances':
        return await this.stripe.balance.retrieve();
      default:
        throw new Error(`Unsupported resource type: ${resource_type}`);
    }
  }

  /**
   * Searches Stripe documentation
   * Note: This would typically integrate with Stripe's documentation API or a custom search service
   */
  async searchStripeDocumentation(params: SearchStripeDocumentationParams): Promise<any> {
    // This is a placeholder implementation
    // In a real implementation, this would query Stripe's documentation API or a search service
    const { query, category = 'all', limit = 10 } = params;

    // Return a structured response indicating this requires external service integration
    return {
      query,
      category,
      limit,
      results: [],
      message: 'Documentation search requires integration with Stripe Docs API or custom search service',
    };
  }

  // ==================== Helper Methods ====================

  /**
   * Gets the Stripe client instance for advanced operations
   */
  getStripeClient(): Stripe {
    return this.stripe;
  }

  /**
   * Tests the API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.stripe.balance.retrieve();
      return true;
    } catch (error) {
      console.error('Stripe connection test failed:', error);
      return false;
    }
  }

  /**
   * Gets API configuration
   */
  getConfig(): GatewayDBConfig {
    return { ...this.config, apiKey: '***REDACTED***' };
  }
}

export default GatewayDB;
