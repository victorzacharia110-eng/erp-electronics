# ERP Electronics — Full Project Documentation

Complete ERP system for selling electronics in Tanzania. Laravel API backend + Vue 3 storefront. UI inspired by bafredoelectronics.co.tz — clean white layout with `#e74c3c` red accents. Features: e-commerce storefront, owner management, employee commissions, inventory tracking, purchase orders, supplier management, double-entry bookkeeping, stock alerts, multi-role authentication, API rate limiting, and automatic session termination (idle timeout).

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Database Schema](#4-database-schema)
5. [Models & Relationships](#5-models--relationships)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [API Routes Reference](#7-api-routes-reference)
8. [Frontend Routes Reference](#8-frontend-routes-reference)
9. [Pinia Stores](#9-pinia-stores)
10. [API Client (Axios)](#10-api-client-axios)
11. [Image Handling](#11-image-handling)
12. [Seeded Data](#12-seeded-data)
13. [Key Features & Business Logic](#13-key-features--business-logic)
14. [Internationalization (i18n)](#14-internationalization-i18n)
15. [Development Commands](#15-development-commands)
16. [Analytics & AI Insights](#16-analytics--ai-insights)
17. [PDF User Manuals](#17-pdf-user-manuals)
18. [System Diagrams](#18-system-diagrams)
19. [Full Business Cycle](#19-full-business-cycle)

---

## 1. Architecture Overview

```
┌──────────────────────┐         ┌──────────────────────────┐
│   Vue 3 Frontend     │  HTTP   │   Laravel API Backend     │
│   localhost:5173     │◄───────►│   localhost:8000/api      │
│                      │         │                           │
│  - Pinia stores      │  Token  │  - Sanctum auth           │
│  - Vue Router        │  Auth   │  - Eloquent ORM           │
│  - Axios client      │         │  - SQLite database        │
│  - Vite bundler      │         │  - Artisan commands       │
│  - vue-i18n          │         │  - Scheduled tasks        │
└──────────────────────┘         └──────────────────────────┘
```

- **Frontend**: Vue 3 SPA served by Vite dev server (port 5173)
- **Backend**: Laravel REST API served by artisan (port 8000)
- **Auth**: Sanctum token-based — `Authorization: Bearer <token>`
- **Rate limiting**: `throttle:api` (120/min) on all API routes; `throttle:login` (5/min) and `throttle:register` (3/min + 10/day) on auth routes
- **Session security**: frontend idle timeout (15 min) + tab-away grace (10 min) force automatic logout
- **Database**: SQLite (file: `database/database.sqlite`)
- **Images**: Stored in `public/products/` on the Laravel server
- **Scheduler**: `php artisan schedule:work` for automated tasks
- **System Name**: ElectroShop (hardcoded in StoreLayout)
- **SaaS Model**: Superadmin registers owners; each owner has their own company, subscription, limits, and branding

---

## 2. Tech Stack

### Frontend (`erp-electronics/`)
| Package | Version | Purpose |
|---|---|---|
| vue | ^3.5.38 | UI framework |
| vue-router | ^5.1.0 | Client-side routing |
| pinia | ^3.0.4 | State management |
| pinia-plugin-persistedstate | ^4.7.1 | Persist auth token to localStorage |
| axios | ^1.18.1 | HTTP client |
| vue-i18n | ^10.0.8 | Internationalization (Swahili/English) |
| @fortawesome/fontawesome-free | ^7.3.0 | Icons (fas fa-*) |
| chart.js + vue-chartjs | ^4.x | Analytics charts |
| vite | ^8.0.16 | Build tool |
| oxlint / oxfmt | ~1.69.0 / ^0.54.0 | Linting & formatting |
| eslint + vue-eslint-parser | ^10.5.0 | Linting |
| vitest / @vue/test-utils | ^4.1.9 / ^2.4.11 | Unit testing |
| playwright | ^1.61.0 | E2E testing |

**Node requirement**: `^22.18.0 || >=24.12.0`

### Backend (`erp-electronics-api/`)
| Package | Purpose |
|---|---|
| Laravel 12 | PHP framework |
| Sanctum | Token-based API auth |
| SQLite | Database |
| Eloquent ORM | Database abstraction |

---

## 3. Project Structure

### Frontend
```
erp-electronics/
├── src/
│   ├── api/
│   │   ├── axios.js              # Axios instance + 401 interceptor
│   │   └── index.js              # All API modules (authApi, cartApi, etc.)
│   ├── components/
│   │   ├── ChangePasswordModal.vue  # Forced password change modal
│   │   ├── SkeletonLoader.vue       # 9 loading skeleton variants
│   │   ├── TablePagination.vue      # Reusable pagination (15/page + View All)
│   │   └── product/
│   │       └── ProductCard.vue   # Reusable product card with add-to-cart
│   ├── composables/
│   │   └── useTablePagination.js # Reusable search + pagination composable
│   ├── layouts/
│   │   ├── StoreLayout.vue       # Main layout: header (ElectroShop logo), nav, footer, cart badge, inbox link
│   │   ├── SuperadminLayout.vue  # Dark sidebar with inbox nav + unread badge polling
│   │   └── StoreFooter.vue       # Footer component
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   └── RegisterPage.vue
│   │   ├── cart/
│   │   │   └── CartPage.vue
│   │   ├── checkout/
│   │   │   └── CheckoutPage.vue  # Delivery options + 5 payment providers
│   │   ├── products/
│   │   │   ├── ProductListPage.vue
│   │   │   ├── ProductDetailPage.vue
│   │   │   └── CategoryPage.vue
│   │   ├── account/
│   │   │   ├── OrdersPage.vue
│   │   │   ├── AccountPage.vue
│   │   │   └── SupportPage.vue   # Customer support messaging
│   │   ├── home/
│   │   │   └── HomePage.vue
│   │   ├── dashboards/
│   │   │   ├── OwnerDashboard.vue
│   │   │   ├── EmployeeDashboard.vue
│   │   │   ├── CustomerDashboard.vue
│   │   │   └── analytics/
│   │   │       ├── SalesCharts.vue       # Chart.js bar/line/doughnut charts
│   │   │       └── AiSuggestions.vue     # Gemini AI business insights
│   │   ├── owner/
│   │   │   ├── EmployeeManagementPage.vue
│   │   │   ├── ProductManagementPage.vue
│   │   │   ├── ProductFormPage.vue
│   │   │   ├── PaymentSettingsPage.vue
│   │   │   ├── ShippingSettingsPage.vue  # Shipping route/rule CRUD
│   │   │   ├── ReportsPage.vue
│   │   │   ├── BranchManagementPage.vue  # Branch CRUD
│   │   │   ├── OwnerInboxPage.vue        # Owner conversations (superadmin + customers)
│   │   │   ├── AccountingDashboardPage.vue  # Accounting summary + quick links
│   │   │   ├── ChartOfAccountsPage.vue      # COA grouped by type, create/edit/delete
│   │   │   ├── JournalEntryListPage.vue     # Paginated journal entries with status filter
│   │   │   ├── JournalEntryCreatePage.vue   # Multi-line entry with balance check
│   │   │   ├── JournalEntryDetailPage.vue   # View + post/void/delete
│   │   │   ├── TrialBalancePage.vue         # Trial balance as of date
│   │   │   ├── ProfitLossPage.vue           # P&L with date range
│   │   │   ├── BalanceSheetPage.vue         # Assets vs liabilities+equity
│   │   │   ├── GeneralLedgerPage.vue        # Account ledger with running balance
│   │   │   ├── CommissionManagementPage.vue # Commission summary + pay/payout
│   │   │   ├── InventoryManagementPage.vue  # Stock dashboard, adjustment, history
│   │   │   ├── PurchaseOrderPage.vue        # PO list, create, receive
│   │   │   ├── SupplierManagementPage.vue   # Supplier CRUD
│   │   │   └── StockAlertsPage.vue          # Low stock alerts
│   │   ├── employee/
│   │   │   ├── CustomerManagementPage.vue
│   │   │   ├── OrderManagementPage.vue   # With branch filter
│   │   │   ├── SupportInboxPage.vue     # Employee support inbox
│   │   │   └── EmployeeEarningsPage.vue  # Employee commission earnings view
│   │   ├── customer/
│   │   │   └── CustomerInboxPage.vue    # Customer→owner conversations
│   │   ├── supplier/
│   │   │   └── SupplierPortalPage.vue   # Supplier portal dashboard
│   │   └── superadmin/
│   │       ├── SuperadminDashboard.vue   # Stats, owners table, create modal
│   │       ├── OwnerManagementPage.vue   # Search, sort, pagination, CRUD
│   │       ├── OwnerDetailPage.vue       # Subscription + limits management
│   │       ├── BrandingPage.vue          # White-label branding per owner
│   │       └── SuperadminInboxPage.vue   # Superadmin↔owner conversations
│   ├── stores/
│   │   ├── auth.js               # Auth state, login/register/logout
│   │   ├── cart.js               # Cart items, totals, CRUD
│   │   └── products.js           # Product listing state
│   ├── utils/
│   │   └── image.js              # imageUrl() — resolves relative paths, adds /products/ prefix
│   ├── locales/
│   │   ├── i18n.js               # vue-i18n config (Swahili default)
│   │   ├── sw.json               # Swahili translations (~500+ keys)
│   │   └── en.json               # English translations (~500+ keys)
│   ├── App.vue
│   └── main.js
├── package.json
├── vite.config.js
├── vitest.config.js
├── generate_manual.py              # PDF user manual generator (EN + SW)
├── favicon.svg                     # Red rounded square with white bolt
└── docs/
    ├── User_Manual_EN.pdf          # English user manual (18 pages)
    ├── User_Manual_SW.pdf          # Swahili user manual (18 pages)
    ├── ERD.drawio                  # Entity Relationship Diagram
    ├── ClassDiagram.drawio         # UML Class Diagram
    ├── UseCase.drawio             # UML Use Case Diagram
    └── SequenceDiagrams.drawio    # UML Sequence Diagrams (3 flows)
```

### Backend
```
erp-electronics-api/
├── app/
│   ├── Console/Commands/
│   │   ├── GenerateDailyReport.php    # report:daily
│   │   ├── CleanupUnpaidOrders.php    # orders:cleanup-unpaid (every 5 min)
│   │   └── ResetSuperadminPassword.php # superadmin:reset-password (auto-reset every 6 months)
│   ├── Http/
│   │   ├── Controllers/Api/
│   │   │   ├── AuthController.php
│   │   │   ├── ProductController.php
│   │   │   ├── CategoryController.php
│   │   │   ├── CartController.php
│   │   │   ├── OrderController.php        # + manage() accepts branch_id filter
│   │   │   ├── PaymentController.php      # Auto-confirms Cash + ClickPesa
│   │   │   ├── PaymentProviderController.php  # CRUD for payment providers
│   │   │   ├── AddressController.php
│   │   │   ├── EmployeeController.php     # + assignBranch()
│   │   │   ├── CustomerController.php
│   │   │   ├── SettingsController.php     # + branding() public endpoint
│   │   │   ├── ReportController.php
│   │   │   ├── ShippingController.php     # Shipping rules CRUD + calculation
│   │   │   ├── SupportMessageController.php  # Customer support messaging
│   │   │   ├── AnalyticsController.php    # Sales analytics + Gemini AI
│   │   │   ├── SuperadminController.php   # Owner CRUD, stats, subscription, limits, branding
│   │   │   ├── ConversationController.php # Conversation CRUD + messaging + unread count
│   │   │   ├── BranchController.php       # Branch CRUD + setDefault
│   │   │   ├── AccountController.php      # Chart of accounts CRUD + balance + tree
│   │   │   ├── JournalEntryController.php # Journal CRUD + post/void + auto-reference
│   │   │   ├── AccountingReportController.php # Trial balance, P&L, balance sheet, general ledger
│   │   │   ├── CommissionController.php   # Commission summary, pay, payAll, employeeEarnings
│   │   │   ├── InventoryController.php    # Inventory index, adjust, transactions, lowStock, dashboard
│   │   │   ├── PurchaseOrderController.php # PO CRUD + receive + supplier portal methods
│   │   │   ├── SupplierController.php     # Supplier CRUD + supplierProfile for portal
│   │   │   ├── StockAlertController.php   # Alerts CRUD + static checkLowStock()
│   │   │   └── NotificationController.php # Notification CRUD + static create()
│   ├── Services/
│   │   └── AccountingReportService.php # Trial balance, P&L, balance sheet, general ledger, monthly/yearly reports
│   │   └── Middleware/
│   │       ├── SuperadminMiddleware.php    # Blocks non-superadmin users
│   │       └── SupplierMiddleware.php      # Allows supplier role + superadmin
│   └── Models/
│       ├── User.php                 # + isSuperadmin(), ownerProfile(), branches()
│       ├── Product.php
│       ├── ProductVariant.php
│       ├── Inventory.php
│       ├── Category.php              # + name_sw, translated_name accessor
│       ├── Order.php                 # + branch_id, branch() relationship
│       ├── OrderItem.php
│       ├── Payment.php
│       ├── PaymentProvider.php
│       ├── ShippingRule.php          # + calculateCost($subtotal)
│       ├── SupportMessage.php
│       ├── Address.php
│       ├── Setting.php
│       ├── DailyReport.php
│       ├── EmployeeProfile.php       # + branch_id, branch() relationship
│       ├── CustomerProfile.php
│       ├── OwnerProfile.php          # subscription, limits, branding
│       ├── Branch.php                # owner, orders, employees
│       ├── Conversation.php          # owner, customer, superadmin, messages
│       ├── ConversationMessage.php   # conversation, sender
│       ├── Account.php               # type, normal_balance, balance accessor
│       ├── JournalEntry.php          # status (draft/posted/voided), generateReference()
│       ├── JournalLine.php           # debit/credit with account relationship
│       ├── Commission.php            # employee/order/rate/amount/status
│       ├── InventoryTransaction.php  # type enum (sale/return/purchase/adjustment/damage/opening)
│       ├── PurchaseOrder.php         # generatePONumber(), supplier relationship
│       ├── PurchaseOrderItem.php     # quantity, unit_cost, quantity_received
│       ├── Supplier.php              # name, contact, products_description
│       ├── StockAlert.php            # type (low_stock/out_of_stock), status
│       ├── AccountingReport.php       # monthly/yearly reports with JSON data + AI suggestions
│       └── Notification.php          # type, title, message, link, read_at
├── bootstrap/
│   └── app.php                       # Registered superadmin + supplier middleware aliases
├── database/
│   ├── migrations/                   # 25+ migration files
│   ├── seeders/
│   │   ├── DatabaseSeeder.php        # Products, images, categories
│   │   ├── SuperadminSeeder.php      # Superadmin user + owner_profile
│   │   └── AccountingSeeder.php      # 22 default chart of accounts + 22 seeded journal entries (May–July 2026)
│   └── database.sqlite
├── public/
│   └── products/                     # Uploaded product images (13 files)
├── routes/
│   ├── api.php                       # All API routes (including branch, conversation, superadmin)
│   └── console.php                   # Scheduled commands
└── .env
```

---

## 4. Database Schema

### users
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | Auto-increment |
| name | string | Full name |
| email | string | Unique |
| phone | string | **Required** |
| password | string | Hashed |
| role | enum | `customer`, `employee`, `owner`, **`superadmin`** |
| is_active | boolean | Default true |
| is_superadmin | boolean | Default false |
| password_changed_at | timestamp | Nullable — triggers force-change if >3 days old |
| remember_token | string | Nullable |
| created_at / updated_at | timestamps | |

### customer_profiles
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | Unique |
| date_of_birth | date | Nullable |
| loyalty_points | integer | Default 0 |

### employee_profiles
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | Unique |
| branch_id | FK → branches | **Nullable** |
| employee_code | string | Unique |
| position | string | Nullable |
| department | string | Nullable |
| hire_date | date | Nullable |
| commission_rate | decimal(5,2) | Commission rate percentage (profit-based) |

### owner_profiles
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | Unique |
| is_active | boolean | Default true |
| subscription_status | enum | `active`, `trial`, `suspended`, `cancelled` |
| subscription_plan | string | Nullable |
| subscription_expires_at | timestamp | Nullable |
| max_products | integer | Default 100 |
| max_employees | integer | Default 10 |
| brand_store_name | string | Nullable — white-label store name |
| brand_tagline | string | Nullable |
| brand_logo_path | string | Nullable |
| brand_color | string | Nullable — hex color |
| brand_color_secondary | string | Nullable |

### categories
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| name | string | English name |
| name_sw | string | Nullable — Swahili name |
| slug | string | Unique, auto-generated |
| description | text | Nullable |
| image | string | Nullable |
| parent_id | FK → categories | Nullable (self-referencing) |
| is_active | boolean | Default true |
| sort_order | integer | Default 0 |
| created_at / updated_at | timestamps | |

**Translated name**: `translated_name` accessor returns `name_sw` when locale is `sw`, otherwise `name`.

### products
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| name | string | |
| slug | string | Unique, auto-generated from name |
| sku | string | Unique |
| description | text | Nullable |
| price | decimal(10,2) | Base price |
| cost_price | decimal(10,2) | Nullable |
| category_id | FK → categories | |
| brand | string | Nullable |
| image | string | Relative path (`products/filename.ext`) or URL |
| images | text | Nullable — JSON array of image paths |
| is_active | boolean | Default true |
| created_at / updated_at | timestamps | |

### product_variants
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| product_id | FK → products | |
| sku | string | Unique |
| color | string | Nullable |
| storage | string | Nullable (e.g. "128GB") |
| price | decimal(10,2) | Variant-specific price |
| cost_price | decimal(10,2) | Nullable |
| is_active | boolean | Default true |
| created_at / updated_at | timestamps | |

### inventory
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| product_variant_id | FK → product_variants | Unique |
| quantity_on_hand | integer | Default 0 |
| reorder_level | integer | Default 10 |
| created_at / updated_at | timestamps | |

### addresses
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | |
| label | string | e.g. "Home", "Office" |
| street | string | |
| city | string | |
| state | string | Nullable |
| postal_code | string | Nullable |
| country | string | Default "Tanzania" |
| is_default | boolean | Default false |
| created_at / updated_at | timestamps | |

### branches
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | Owner who owns the branch |
| name | string | Branch name |
| city | string | |
| address | string | Nullable |
| phone | string | Nullable |
| is_active | boolean | Default true |
| is_default | boolean | Default false |
| created_at / updated_at | timestamps | |

### orders
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | Customer who placed order |
| branch_id | FK → branches | **Nullable** — branch where order was placed |
| handled_by | FK → users | Nullable — employee/owner who processed |
| shipping_address_id | FK → addresses | Nullable |
| order_number | string | Unique, auto-generated (`ORD-XXXXXXXXXX`) |
| status | enum | `pending_payment`, `pending`, `inactive`, `paid`, `processing`, `shipped`, `delivered`, `cancelled` |
| subtotal | decimal(12,2) | |
| shipping_cost | decimal(12,2) | Default 0 |
| total | decimal(12,2) | |
| notes | text | Nullable |
| tracking_number | string | Nullable — set by employee/owner |
| delivery_notes | text | Nullable — set by employee/owner |
| delivery_required | boolean | Default false |
| shipped_at | timestamp | Nullable |
| delivered_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### order_items
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| order_id | FK → orders (ON DELETE CASCADE) | |
| product_variant_id | FK → product_variants | |
| quantity | integer | |
| unit_price | decimal(12,2) | Price at time of order |
| total | decimal(12,2) | quantity × unit_price |
| created_at / updated_at | timestamps | |

### payments
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| order_id | FK → orders (ON DELETE CASCADE) | |
| provider | string | `cash`, `mpesa`, `airtel`, `mixx_by_yas`, `halopesa`, `clickpesa` |
| amount | decimal(12,2) | |
| status | enum | `pending`, `completed`, `failed`, `refunded` |
| provider_reference | string | Nullable |
| metadata | text (JSON) | Nullable |
| created_at / updated_at | timestamps | |

### payment_providers
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| name | string | Display name (e.g. "M-Pesa") |
| slug | string | Unique identifier (e.g. "mpesa") |
| number | string | Nullable — phone number for payments |
| icon | string | FontAwesome class (e.g. "fas fa-mobile-screen") |
| enabled | boolean | Default true |
| sort_order | integer | Default 0 |
| created_at / updated_at | timestamps | |

### shipping_rules
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| name | string | Route name (e.g. "Dar to Arusha") |
| from_city | string | Origin city (`*` for wildcard) |
| to_city | string | Destination city (`*` for wildcard) |
| base_cost | decimal(10,2) | Default shipping cost |
| value_rules | JSON | Nullable — tiered pricing: `[{ min_value, max_value, adjusted_cost }]` |
| enabled | boolean | Default true |
| created_at / updated_at | timestamps | |

### support_messages
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users (ON DELETE CASCADE) | Customer who sent the message |
| order_id | FK → orders (ON DELETE SET NULL) | Nullable — related order |
| subject | string | |
| message | text | |
| category | enum | `payment_issue`, `order_status`, `delivery`, `refund`, `general` |
| status | enum | `open`, `in_progress`, `resolved`, `closed` |
| admin_reply | text | Nullable |
| replied_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### conversations
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | Owner in the conversation |
| customer_id | FK → users | Nullable — customer (for customer_owner type) |
| superadmin_id | FK → users | Nullable — superadmin (for superadmin_owner type) |
| type | enum | `superadmin_owner`, `customer_owner` |
| subject | string | |
| status | enum | `open`, `in_progress`, `resolved`, `closed` |
| last_message_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### conversation_messages
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| conversation_id | FK → conversations (ON DELETE CASCADE) | |
| sender_id | FK → users | Who sent the message |
| message | text | |
| is_read | boolean | Default false |
| created_at / updated_at | timestamps | |

### settings
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| key | string | Unique (e.g. `clickpesa_enabled`) |
| value | string | |
| type | string | `boolean`, `string`, `integer`, `json` |
| created_at / updated_at | timestamps | |

### daily_reports
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| report_date | date | Unique |
| total_orders | integer | |
| total_revenue | decimal(14,2) | |
| total_items_sold | integer | |
| paid_orders | integer | |
| pending_orders | integer | |
| cancelled_orders | integer | |
| employee_stats | json | Array of per-employee stats |
| top_products | json | Array of top-selling products |
| created_at / updated_at | timestamps | |

### accounts
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | Owner who owns this account |
| code | string | Unique per owner (e.g. "1000") |
| name | string | Account name |
| type | enum | `asset`, `liability`, `equity`, `revenue`, `expense` |
| description | text | Nullable |
| is_active | boolean | Default true |
| normal_balance | enum | `debit`, `credit` |
| created_at / updated_at | timestamps | |

### journal_entries
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | Owner who owns this entry |
| reference | string | Unique per owner (e.g. "JE-20260717-001") |
| date | date | Entry date |
| description | text | |
| source_type | string | Nullable — polymorphic (e.g. "App\Models\Order") |
| source_id | bigint | Nullable — polymorphic |
| status | enum | `draft`, `posted`, `voided` |
| posted_at | timestamp | Nullable |
| voided_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### journal_lines
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| journal_entry_id | FK → journal_entries (ON DELETE CASCADE) | |
| account_id | FK → accounts | |
| debit | decimal(12,2) | Default 0 |
| credit | decimal(12,2) | Default 0 |
| description | text | Nullable |
| created_at / updated_at | timestamps | |

### commissions
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | |
| employee_id | FK → users | |
| order_id | FK → orders | Nullable — null when paid out |
| order_amount | decimal(12,2) | Order subtotal (revenue) for reference |
| cost_amount | decimal(12,2) | Total cost of goods for this order |
| profit_amount | decimal(12,2) | order_amount - cost_amount |
| commission_rate | decimal(5,2) | Commission rate percentage |
| commission_amount | decimal(12,2) | profit_amount × (rate / 100) |
| status | enum | `pending`, `paid_out` |
| paid_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### inventory_transactions
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | |
| product_variant_id | FK → product_variants | |
| type | enum | `sale`, `return`, `purchase`, `adjustment`, `damage`, `opening` |
| quantity | integer | Positive = in, negative = out |
| reference_type | string | Nullable — polymorphic (Order, PurchaseOrder, etc.) |
| reference_id | bigint | Nullable — polymorphic |
| notes | text | Nullable |
| created_by | FK → users | Nullable |
| created_at / updated_at | timestamps | |

### purchase_orders
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | |
| supplier_id | FK → suppliers | Nullable |
| po_number | string | Unique per owner (e.g. "PO-20260717-001") |
| status | enum | `draft`, `ordered`, `received` |
| total_cost | decimal(12,2) | |
| expected_date | date | Nullable |
| received_date | date | Nullable |
| notes | text | Nullable |
| created_at / updated_at | timestamps | |

### purchase_order_items
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| purchase_order_id | FK → purchase_orders (ON DELETE CASCADE) | |
| product_variant_id | FK → product_variants | |
| quantity | integer | |
| unit_cost | decimal(12,2) | |
| quantity_received | integer | Default 0 |
| created_at / updated_at | timestamps | |

### suppliers
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | |
| name | string | |
| contact_person | string | Nullable |
| phone | string | Nullable |
| email | string | Nullable |
| address | text | Nullable |
| city | string | Nullable |
| country | string | Default "Tanzania" |
| products_description | text | Nullable |
| notes | text | Nullable |
| is_active | boolean | Default true |
| created_at / updated_at | timestamps | |

### stock_alerts
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | |
| product_variant_id | FK → product_variants | |
| type | enum | `low_stock`, `out_of_stock` |
| status | enum | `active`, `acknowledged`, `resolved` |
| message | text | |
| created_at / updated_at | timestamps | |

### notifications
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| user_id | FK → users | |
| type | string | e.g. "stock_alert" |
| title | string | |
| message | text | |
| link | string | Nullable — frontend route |
| data | json | Nullable |
| read_at | timestamp | Nullable |
| created_at / updated_at | timestamps | |

### accounting_reports
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| owner_id | FK → users | Owner who owns this report |
| type | enum | `monthly`, `yearly` |
| title | string | e.g. "Monthly Report - July 2026" |
| period_start | date | Start of reporting period |
| period_end | date | End of reporting period |
| report_data | json | Full computed report data (trial balance, P&L, balance sheet, general ledger) |
| ai_suggestions | json | Nullable — bilingual AI suggestions array |
| created_at / updated_at | timestamps | |

---

## 5. Models & Relationships

### User
```
role: 'customer' | 'employee' | 'owner' | 'superadmin' | 'supplier'
mustChangePassword() → true if password_changed_at is null or >3 days ago
superadminPasswordExpired() → true if password_changed_at is older than 6 months (superadmin only)
isCustomer() / isEmployee() / isOwner() / isSuperadmin() / isSupplier()

Relationships:
  hasOne(EmployeeProfile)
  hasOne(CustomerProfile)
  hasOne(OwnerProfile)
  hasMany(orders)         // as customer
  hasMany(addresses)
  hasMany(branches)       // as owner
  hasMany(conversations)  // as owner, customer, or superadmin
  hasMany(conversationMessages) // as sender
```

### OwnerProfile
```
subscription_status, subscription_plan, subscription_expires_at
max_products, max_employees (limits)
brand_store_name, brand_tagline, brand_logo_path, brand_color, brand_color_secondary (white-label)

Relationships:
  belongsTo(User)
```

### Branch
```
is_default: toggleable per owner

Relationships:
  belongsTo(User, 'owner_id')
  hasMany(Order)
  hasMany(EmployeeProfile)
```

### Product
```
slug: auto-generated from name (Str::slug)
SKU: auto-generated if not provided

Relationships:
  belongsTo(Category)
  hasMany(ProductVariant)
```

### ProductVariant
```
Relationships:
  belongsTo(Product)
  hasOne(Inventory)
```

### Inventory
```
Relationships:
  belongsTo(ProductVariant)
```

### Category
```
translated_name: accessor → returns name_sw when locale=sw, else name

Relationships:
  hasMany(Product)
  belongsTo(Category, 'parent_id')  // parent
  hasMany(Category, 'parent_id')    // children
```

### Order
```
status flow:
  pending_payment → pending → paid → processing → shipped → delivered
                   ↓                     ↓
                inactive              cancelled
                   ↓
              (auto-deleted after 6h)

Relationships:
  belongsTo(User) as customer
  belongsTo(User, 'handled_by') as handler
  belongsTo(Branch)
  belongsTo(Address, 'shipping_address_id') as shippingAddress
  hasMany(OrderItem)
  hasMany(Payment)
  hasOne(latestPayment) // most recent payment
```

### PaymentProvider
```
5 providers seeded: cash (manual), mpesa, airtel, mixx_by_yas, halopesa
ClickPesa toggleable via settings

Relationships: none (standalone config)
```

### ShippingRule
```
calculateCost($subtotal):
  - Checks value_rules tiers for matching subtotal range
  - Returns adjusted_cost if tier matches, otherwise base_cost
  - Wildcard rules (* for from_city/to_city) match all routes

Seeded tiers:
  ≥ TSh 1,000,000 → TSh 98,000
  TSh 300,000–999,999 → TSh 50,000
  < TSh 300,000 → TSh 25,000

Relationships: none (standalone config)
```

### SupportMessage
```
Statuses: open → in_progress → resolved → closed

Relationships:
  belongsTo(User)
  belongsTo(Order)  // nullable
```

### Conversation
```
Types: superadmin_owner, customer_owner

otherParty($currentUser) → returns the other party's User model

Relationships:
  belongsTo(User, 'owner_id')
  belongsTo(User, 'customer_id')
  belongsTo(User, 'superadmin_id')
  hasMany(ConversationMessage)
  hasOne(lastMessage) // most recent message
```

### ConversationMessage
```
Relationships:
  belongsTo(Conversation)
  belongsTo(User, 'sender_id')
```

### Setting
```
getTypedValue() → casts value based on type field
  boolean: returns true/false
  integer: returns int
  json: returns decoded array
  string: returns as-is
```

### DailyReport
```
employee_stats: JSON array of { user_id, name, orders_handled, revenue }
top_products: JSON array of { product_id, name, quantity_sold, revenue }
total_items_sold, paid_orders, pending_orders, cancelled_orders: integer counters
```

### Account
```
type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
normal_balance: 'debit' | 'credit'
balance: computed accessor — sum of debits minus credits per account

Relationships:
  belongsTo(User, 'owner_id')
  hasMany(JournalLine)
```

### JournalEntry
```
status: 'draft' | 'posted' | 'voided'
generateReference(): JE-YYYYMMDD-XXX (per owner)
isBalanced(): total debits == total credits

Relationships:
  belongsTo(User, 'owner_id')
  hasMany(JournalLine)
  morphTo() // source: Order, PurchaseOrder, etc.
```

### JournalLine
```
debit/credit: decimal(12,2) — exactly one should be non-zero per line

Relationships:
  belongsTo(JournalEntry)
  belongsTo(Account)
```

### Commission
```
status: 'pending' | 'paid_out'
profit_amount = order_amount - cost_amount (total cost of goods)
commission_amount = profit_amount × (rate / 100)
No base salary — purely profit-based earnings

Relationships:
  belongsTo(User, 'owner_id')
  belongsTo(User, 'employee_id')
  belongsTo(Order)
```

### InventoryTransaction
```
type: 'sale' | 'return' | 'purchase' | 'adjustment' | 'damage' | 'opening'
quantity: positive = stock in, negative = stock out

Relationships:
  belongsTo(User, 'owner_id')
  belongsTo(ProductVariant)
  belongsTo(User, 'created_by')
  morphTo() // reference: Order, PurchaseOrder, etc.
```

### PurchaseOrder
```
status: 'draft' | 'ordered' | 'received'
generatePONumber(): PO-YYYYMMDD-XXX (per owner)

Relationships:
  belongsTo(User, 'owner_id')
  belongsTo(Supplier)
  hasMany(PurchaseOrderItem)
```

### PurchaseOrderItem
```
quantity_received: updated when PO is received

Relationships:
  belongsTo(PurchaseOrder)
  belongsTo(ProductVariant)
```

### Supplier
```
Full contact details for vendor management

Relationships:
  belongsTo(User, 'owner_id')
  hasMany(PurchaseOrder)
```

### StockAlert
```
type: 'low_stock' | 'out_of_stock'
status: 'active' | 'acknowledged' | 'resolved'

Relationships:
  belongsTo(User, 'owner_id')
  belongsTo(ProductVariant)
```

### Notification
```
Polymorphic data field, read_at timestamp for read/unread

Relationships:
  belongsTo(User, 'user_id')
```

### AccountingReport
```
type: 'monthly' | 'yearly'
report_data: computed JSON (trial_balance, profit_loss, balance_sheet, general_ledger, summary)
ai_suggestions: nullable JSON array of bilingual suggestions

Relationships:
  belongsTo(User, 'owner_id')
```

---

## 6. Authentication & Authorization

### Token Flow
1. User sends `POST /api/auth/login` with `{ email, password }`
2. Backend validates credentials, returns `{ token, user, must_change_password, owner_profile, superadmin_password_expired }`
3. Frontend stores token in `localStorage` (key: `auth_token`)
4. All authenticated requests include `Authorization: Bearer <token>` header
5. 401 responses trigger automatic logout via Axios interceptor

### Roles & Permissions

| Feature | Customer | Employee | Owner | Superadmin | Supplier |
|---|---|---|---|---|---|
| Browse products | ✅ | ✅ | ✅ | ✅ | ❌ |
| Add to cart / checkout | ✅ | ✅ | ✅ | ✅ | ❌ |
| View own orders | ✅ | ✅ | ✅ | ❌ | ❌ |
| View all orders | ❌ | ✅ | ✅ | ❌ | ❌ |
| Process orders (status updates) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Confirm payments (type name) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Update delivery details | ❌ | ✅ | ✅ | ❌ | ❌ |
| Reply to support messages | ❌ | ✅ | ✅ | ❌ | ❌ |
| View reports | ❌ | ✅ | ✅ | ❌ | ❌ |
| Manage customers | ❌ | ✅ | ✅ | ❌ | ❌ |
| Send support messages | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage employees | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage branches | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage products (CRUD) | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage payment providers | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage shipping rules | ❌ | ❌ | ✅ | ❌ | ❌ |
| View analytics + AI insights | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage accounting | ❌ | ❌ | ✅ | ❌ | ❌ |
| Generate accounting reports | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage commissions | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage inventory | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage purchase orders | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage suppliers | ❌ | ❌ | ✅ | ❌ | ❌ |
| View stock alerts | ❌ | ❌ | ✅ | ❌ | ❌ |
| View own earnings | ❌ | ✅ | ❌ | ❌ | ❌ |
| Edit own profile | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit own password | ✅ | ✅ | ❌ | ❌ | ❌ |
| Reset employee password | ❌ | ❌ | ✅ | ❌ | ❌ |
| Reset owner password | ❌ | ❌ | ❌ | ✅ | ❌ |
| Conversation with owner | ❌ | ❌ | ✅ | ✅ | ❌ |
| Conversation with customer | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage owners (CRUD) | ❌ | ❌ | ❌ | ✅ | ❌ |
| Manage subscriptions | ❌ | ❌ | ❌ | ✅ | ❌ |
| Manage branding (per-owner) | ❌ | ❌ | ❌ | ✅ | ❌ |
| System-wide settings | ❌ | ❌ | ❌ | ✅ | ❌ |
| Auto-reset own password (6mo) | ❌ | ❌ | ❌ | ✅ | ❌ |
| View supplier portal | ❌ | ❌ | ❌ | ❌ | ✅ |
| Update PO status (supplier) | ❌ | ❌ | ❌ | ❌ | ✅ |

### Password Policy
- Minimum 8 characters
- Must include uppercase, lowercase, number, and special character
- Enforced both frontend (real-time rules) and backend (custom Laravel messages)

### Password Expiry
- `password_changed_at` column tracks last change
- `mustChangePassword()` returns true if null or >3 days old
- Modal forces password change on login

### Default Passwords
- **Employees**: `strtoupper(full_name)` — e.g. "MATHEW ZACHARIA"
- **Owners** (created by superadmin): `strtoupper(name)` — `password_changed_at` NOT set → forces change on first login
- **Superadmin**: `SuperAdmin@2026` — auto-resets every 6 months
- Response includes `default_password` field for superadmin to share

### Password Management

#### Owner Resets Employee Password
- Owner can reset any employee's password to the default (`strtoupper(name)`)
- `POST /employees/{user}/reset-password` → `EmployeeController::resetPassword`
- Returns `{ message, default_password: "EMPLOYEE NAME" }`
- Only owner role allowed

#### Superadmin Resets Owner Password
- Superadmin can reset any owner's password to the default (`strtoupper(name)`)
- `POST /superadmin/owners/{id}/reset-password` → `SuperadminController::resetPassword`
- Returns `{ message, default_password: "OWNER NAME" }`
- Sets `password_changed_at` to null → forces change on next login

#### Superadmin Auto-Reset (6 Months)
- Superadmin password auto-resets every 6 months via artisan command
- `php artisan superadmin:reset-password` — checks `superadmin_password_expired` on User model
- `User::superadminPasswordExpired()` checks if `password_changed_at` is older than 6 months
- Scheduled monthly in `routes/console.php` (only triggers when 6 months actually elapsed)
- New superadmin password = `SuperAdmin@2026` with `password_changed_at` set to now
- Login and profile responses include `superadmin_password_expired` boolean for superadmin users

#### Owner Profile Editing
- Owners can edit their own profile (name, phone, branding fields)
- `PUT /auth/profile` — `AuthController::updateProfile` enhanced with role-based logic
- Owners **cannot** change their own password (only superadmin can)
- Fields editable by owner: `name`, `phone`, `brand_store_name`, `brand_tagline`, `brand_color`, `brand_color_secondary`
- Returns updated `owner_profile` in response

#### Employee Profile Editing by Owner
- Owner can update employee profile fields (position, department, commission_rate, branch_id)
- `PATCH /employees/{user}/profile` → `EmployeeController::updateProfile`
- Employees cannot edit their own profile

### Account Lockout
- 5 failed attempts → account locks for 30 minutes (`users.locked_until`)
- API returns HTTP 423 with remaining minutes; login form shows remaining attempts

### Rate Limiting
- `RateLimiter::for('api')` — 120 requests/min keyed by authenticated user id, else IP
- `RateLimiter::for('login')` — 5/min per IP (applied via `throttle:login` on `POST /auth/login`)
- `RateLimiter::for('register')` — 3/min and 10/day per IP (applied via `throttle:register` on `POST /auth/register`)
- Enabled with `$middleware->throttleApi()` in `bootstrap/app.php`
- Exceeding limits returns HTTP 429 with `X-RateLimit-Remaining`/`X-RateLimit-Reset` headers
- Tests: `tests/Feature/RateLimitingTest.php`

### Session Termination (Idle Timeout)
- Implemented client-side in `src/stores/session.js` (frontend)
- 15 minutes of inactivity → automatic logout; warning modal appears in the final 60 seconds
- Switching away (tab hidden) pauses the timer; returning within 10 minutes continues, otherwise logs out
- Persists `session_last_active`; a reload after the idle window forces logout immediately

### Route Guards (Frontend)
- `meta.requiresAuth` — redirects to `/login` if no token
- `meta.role` — redirects to correct dashboard if wrong role
- `meta.guest` — redirects to home if already logged in

---

## 7. API Routes Reference

Base URL: `http://localhost:8000/api`

### Public Routes
| Method | Endpoint | Controller | Description |
|---|---|---|---|
| POST | `/auth/register` | AuthController@register | Register new customer (phone **required**) |
| POST | `/auth/login` | AuthController@login | Login, returns token + owner_profile |
| GET | `/products` | ProductController@index | List products (paginated, filterable) |
| GET | `/products/featured` | ProductController@featured | Featured products |
| GET | `/products/{slug}` | ProductController@show | Single product by slug |
| GET | `/categories` | CategoryController@index | List categories (with `translated_name`) |
| GET | `/categories/{slug}` | CategoryController@show | Single category with products |
| GET | `/payment-providers` | PaymentProviderController@publicIndex | Enabled payment providers |
| POST | `/shipping/calculate` | ShippingController@calculate | Calculate shipping cost |
| POST | `/payments/webhook` | PaymentController@webhook | ClickPesa webhook (no auth) |
| GET | `/settings/payment` | SettingsController@payment | Payment settings (read-only) |
| GET | `/settings/branding` | SettingsController@branding | Public branding (owner's white-label) |

### Authenticated Routes
| Method | Endpoint | Controller | Description |
|---|---|---|---|
| POST | `/auth/logout` | AuthController@logout | Revoke token |
| GET | `/auth/profile` | AuthController@profile | Get current user |
| PUT | `/auth/profile` | AuthController@updateProfile | Update profile |
| POST | `/auth/change-password` | AuthController@changePassword | Change password |
| **Employee Management (owner)** | | | |
| GET | `/employees` | EmployeeController@index | List employees (with branch) |
| POST | `/employees` | EmployeeController@store | Create employee (default password = UPPERCASE NAME) + optional `branch_id` |
| PATCH | `/employees/{user}/toggle-status` | EmployeeController@toggleStatus | Toggle active/inactive |
| DELETE | `/employees/{user}` | EmployeeController@destroy | Delete employee |
| PATCH | `/employees/{user}/assign-branch` | EmployeeController@assignBranch | Assign employee to branch |
| PATCH | `/employees/{user}/reset-password` | EmployeeController@resetPassword | Reset employee password to default (owner only) |
| PATCH | `/employees/{user}/profile` | EmployeeController@updateProfile | Update employee profile (position, department, commission_rate, branch_id) |
| **Customer Management (employee/owner)** | | | |
| GET | `/customers` | CustomerController@index | List customers |
| PATCH | `/customers/{user}/toggle-status` | CustomerController@toggleStatus | Toggle active/inactive |
| DELETE | `/customers/{user}` | CustomerController@destroy | Delete customer |
| **Branch Management (owner)** | | | |
| GET | `/branches` | BranchController@index | List branches |
| GET | `/branches/{id}` | BranchController@show | Get single branch |
| POST | `/branches` | BranchController@store | Create branch |
| PUT | `/branches/{id}` | BranchController@update | Update branch |
| DELETE | `/branches/{id}` | BranchController@destroy | Delete branch |
| PATCH | `/branches/{id}/set-default` | BranchController@setDefault | Set as default branch |
| **Payment Provider Management (owner)** | | | |
| GET | `/payment-providers-manage` | PaymentProviderController@index | List all providers |
| POST | `/payment-providers` | PaymentProviderController@store | Create provider |
| PUT | `/payment-providers/{id}` | PaymentProviderController@update | Update provider |
| DELETE | `/payment-providers/{id}` | PaymentProviderController@destroy | Delete provider |
| **Payment Settings (owner)** | | | |
| PUT | `/settings/payment` | SettingsController@updatePayment | Toggle ClickPesa |
| **Product Management (owner)** | | | |
| GET | `/products-manage` | ProductController@manage | List all products (admin view) |
| POST | `/products` | ProductController@store | Create product (multipart/form-data) |
| PUT | `/products/{id}` | ProductController@update | Update product |
| DELETE | `/products/{id}` | ProductController@destroy | Delete product |
| **Cart** | | | |
| GET | `/cart` | CartController@index | Get user's cart |
| POST | `/cart` | CartController@add | Add item `{ product_variant_id, quantity }` |
| PUT | `/cart/{itemId}` | CartController@update | Update quantity `{ quantity }` |
| DELETE | `/cart/{itemId}` | CartController@remove | Remove item |
| DELETE | `/cart` | CartController@clear | Clear entire cart |
| **Orders** | | | |
| GET | `/orders` | OrderController@index | Customer's own orders |
| POST | `/orders` | OrderController@store | Create order from cart (`delivery_required`, `shipping_cost`, `branch_id`) |
| GET | `/orders/{orderId}` | OrderController@show | Single order detail |
| **Order Management (employee/owner)** | | | |
| GET | `/orders-manage` | OrderController@manage | All orders with filters (accepts `branch_id`) |
| PATCH | `/orders/{orderId}/status` | OrderController@updateStatus | Update status (auto inventory management) |
| PATCH | `/orders/{orderId}/delivery` | OrderController@updateDelivery | Update tracking number + delivery notes |
| **Shipping Rules (owner)** | | | |
| GET | `/shipping-rules` | ShippingController@index | List all shipping rules |
| POST | `/shipping-rules` | ShippingController@store | Create shipping rule |
| PUT | `/shipping-rules/{id}` | ShippingController@update | Update shipping rule |
| DELETE | `/shipping-rules/{id}` | ShippingController@destroy | Delete shipping rule |
| **Support Messages** | | | |
| GET | `/support-messages` | SupportMessageController@index | List messages (customer: own, employee: all) |
| POST | `/support-messages` | SupportMessageController@store | Create support message (customer) |
| GET | `/support-messages/{id}` | SupportMessageController@show | Get single message |
| PATCH | `/support-messages/{id}/reply` | SupportMessageController@reply | Reply to message (employee/owner) |
| PATCH | `/support-messages/{id}/status` | SupportMessageController@updateStatus | Update message status |
| GET | `/support/unread-count` | SupportMessageController@unreadCount | Get unread message count |
| **Conversations** | | | |
| GET | `/conversations` | ConversationController@index | List conversations (filtered by role) |
| POST | `/conversations` | ConversationController@store | Start new conversation |
| GET | `/conversations/{id}` | ConversationController@show | View conversation + messages |
| POST | `/conversations/{id}/messages` | ConversationController@sendMessage | Send message in conversation |
| PATCH | `/conversations/{id}/status` | ConversationController@updateStatus | Update conversation status (active/closed) |
| GET | `/conversations/{id}/owner-details` | ConversationController@ownerDetails | Get owner details for conversation panel |
| GET | `/conversations/{id}/customer-details` | ConversationController@customerDetails | Get customer details for conversation panel |
| GET | `/conversations/unread-count` | ConversationController@unreadCount | Get unread conversation count |
| **Reports (employee/owner)** | | | |
| GET | `/reports/daily` | ReportController@daily | Daily report by date |
| GET | `/reports/summary` | ReportController@summary | Summary stats |
| **Analytics (owner)** | | | |
| GET | `/analytics/sales` | AnalyticsController@sales | Monthly sales data (revenue, profit, items, categories) |
| POST | `/analytics/ai-suggestions` | AnalyticsController@aiSuggestions | AI-powered business suggestions via Gemini |
| **Payments** | | | |
| POST | `/payments/initiate` | PaymentController@initiate | Initiate payment (auto-confirms Cash + ClickPesa) |
| GET | `/orders/{orderId}/payment-status` | PaymentController@status | Check payment status |
| **Addresses** | | | |
| GET | `/addresses` | AddressController@index | List addresses |
| POST | `/addresses` | AddressController@store | Create address |
| PUT | `/addresses/{id}` | AddressController@update | Update address |
| DELETE | `/addresses/{id}` | AddressController@destroy | Delete address |
| **Superadmin** | | | |
| GET | `/superadmin/stats` | SuperadminController@stats | System-wide statistics |
| GET | `/superadmin/owners` | SuperadminController@owners | List all owners |
| POST | `/superadmin/owners` | SuperadminController@store | Create new owner (default password = UPPERCASE NAME) |
| GET | `/superadmin/owners/{id}` | SuperadminController@show | Get owner details |
| PATCH | `/superadmin/owners/{id}/toggle-active` | SuperadminController@toggleActive | Toggle owner active/inactive |
| DELETE | `/superadmin/owners/{id}` | SuperadminController@destroy | Delete owner |
| PUT | `/superadmin/owners/{id}/subscription` | SuperadminController@updateSubscription | Update owner subscription |
| PUT | `/superadmin/owners/{id}/limits` | SuperadminController@updateLimits | Update owner limits |
| PUT | `/superadmin/owners/{id}/branding` | SuperadminController@updateBranding | Update owner branding |
| POST | `/superadmin/owners/{id}/branding-logo` | SuperadminController@updateBrandingLogo | Upload owner logo |
| POST | `/superadmin/owners/{id}/reset-password` | SuperadminController@resetPassword | Reset owner password to default |
| **Accounting (owner)** | | | |
| GET | `/accounts` | AccountController@index | List all accounts |
| GET | `/accounts/tree` | AccountController@tree | Accounts grouped by type |
| GET | `/accounts/{id}` | AccountController@show | Get single account |
| POST | `/accounts` | AccountController@store | Create account |
| PUT | `/accounts/{id}` | AccountController@update | Update account |
| DELETE | `/accounts/{id}` | AccountController@destroy | Delete account |
| GET | `/accounts/{id}/balance` | AccountController@balance | Get account balance |
| GET | `/journal-entries` | JournalEntryController@index | List journal entries |
| GET | `/journal-entries/{id}` | JournalEntryController@show | Get single entry |
| POST | `/journal-entries` | JournalEntryController@store | Create journal entry |
| PATCH | `/journal-entries/{id}/post` | JournalEntryController@post | Post journal entry |
| PATCH | `/journal-entries/{id}/void` | JournalEntryController@void | Void journal entry |
| DELETE | `/journal-entries/{id}` | JournalEntryController@destroy | Delete draft entry |
| GET | `/accounting/trial-balance` | AccountingReportController@trialBalance | Trial balance as of date |
| GET | `/accounting/profit-loss` | AccountingReportController@profitLoss | P&L with date range |
| GET | `/accounting/balance-sheet` | AccountingReportController@balanceSheet | Balance sheet |
| GET | `/accounting/general-ledger` | AccountingReportController@generalLedger | Account ledger |
| POST | `/reports/generate-monthly` | AccountingReportController@generateMonthlyReport | Generate monthly accounting report |
| POST | `/reports/generate-yearly` | AccountingReportController@generateYearlyReport | Generate yearly accounting report |
| GET | `/reports/list` | AccountingReportController@listReports | List all saved accounting reports |
| GET | `/reports/{id}` | AccountingReportController@getReport | Get single accounting report with data |
| POST | `/reports/ai-suggestions` | AccountingReportController@aiSuggestions | Get bilingual (Swahili/English) AI suggestions for accounting report |
| **Commissions (owner)** | | | |
| GET | `/commissions` | CommissionController@index | Commission summary |
| POST | `/commissions/{id}/pay` | CommissionController@pay | Pay single commission |
| POST | `/commissions/pay-all` | CommissionController@payAll | Pay all commissions |
| GET | `/commissions/employee/{userId}` | CommissionController@employeeEarnings | Employee earnings |
| **Inventory (owner)** | | | |
| GET | `/inventory` | InventoryController@index | Inventory list (search, low_stock filter) |
| POST | `/inventory/adjust` | InventoryController@adjust | Stock adjustment |
| GET | `/inventory/transactions` | InventoryController@transactions | Transaction history |
| GET | `/inventory/low-stock` | InventoryController@lowStock | Low stock items |
| GET | `/inventory/dashboard` | InventoryController@dashboard | Inventory stats |
| **Purchase Orders (owner)** | | | |
| GET | `/purchase-orders` | PurchaseOrderController@index | List POs |
| GET | `/purchase-orders/{id}` | PurchaseOrderController@show | Get single PO |
| POST | `/purchase-orders` | PurchaseOrderController@store | Create PO |
| POST | `/purchase-orders/{id}/receive` | PurchaseOrderController@receive | Receive PO (auto inventory + journal) |
| DELETE | `/purchase-orders/{id}` | PurchaseOrderController@destroy | Delete draft PO |
| **Suppliers (owner)** | | | |
| GET | `/suppliers` | SupplierController@index | List suppliers |
| GET | `/suppliers/all` | SupplierController@all | All active suppliers |
| GET | `/suppliers/{id}` | SupplierController@show | Get single supplier |
| POST | `/suppliers` | SupplierController@store | Create supplier |
| PUT | `/suppliers/{id}` | SupplierController@update | Update supplier |
| DELETE | `/suppliers/{id}` | SupplierController@destroy | Delete supplier |
| **Stock Alerts (owner)** | | | |
| GET | `/stock-alerts` | StockAlertController@index | List alerts |
| GET | `/stock-alerts/count` | StockAlertController@count | Active alert count |
| POST | `/stock-alerts/{id}/acknowledge` | StockAlertController@acknowledge | Acknowledge alert |
| POST | `/stock-alerts/{id}/resolve` | StockAlertController@resolve | Resolve alert |
| **Notifications (owner)** | | | |
| GET | `/notifications` | NotificationController@index | List notifications |
| GET | `/notifications/count` | NotificationController@count | Unread count |
| POST | `/notifications/{id}/read` | NotificationController@markRead | Mark as read |
| POST | `/notifications/read-all` | NotificationController@markAllRead | Mark all read |
| **Supplier Portal (supplier role)** | | | |
| GET | `/supplier-portal/profile` | SupplierController@supplierProfile | Supplier profile |
| GET | `/supplier-portal/purchase-orders` | PurchaseOrderController@supplierOrders | Supplier's POs |
| GET | `/supplier-portal/purchase-orders/{id}` | PurchaseOrderController@supplierShow | Supplier's PO detail |
| POST | `/supplier-portal/purchase-orders/{id}/update-status` | PurchaseOrderController@supplierUpdateStatus | Update PO status |

---

## 8. Frontend Routes Reference

| Path | Name | Component | Access |
|---|---|---|---|
| `/` | home | HomePage.vue | Public |
| `/products` | products | ProductListPage.vue | Public |
| `/products/:slug` | product-detail | ProductDetailPage.vue | Public |
| `/category/:slug` | category | CategoryPage.vue | Public |
| `/cart` | cart | CartPage.vue | Auth required |
| `/checkout` | checkout | CheckoutPage.vue | Auth required |
| `/orders` | orders | OrdersPage.vue | Auth required |
| `/account` | account | AccountPage.vue | Auth required |
| `/support` | support | SupportPage.vue | Customer |
| `/customer/inbox` | customer-inbox | CustomerInboxPage.vue | Customer |
| `/owner` | owner-dashboard | OwnerDashboard.vue | Owner |
| `/owner/employees` | owner-employees | EmployeeManagementPage.vue | Owner |
| `/owner/products` | owner-products | ProductManagementPage.vue | Owner |
| `/owner/products/new` | owner-product-new | ProductFormPage.vue | Owner |
| `/owner/products/:id/edit` | owner-product-edit | ProductFormPage.vue | Owner |
| `/owner/payment-settings` | owner-payment-settings | PaymentSettingsPage.vue | Owner |
| `/owner/shipping` | owner-shipping | ShippingSettingsPage.vue | Owner |
| `/owner/reports` | owner-reports | ReportsPage.vue | Owner |
| `/owner/branches` | owner-branches | BranchManagementPage.vue | Owner |
| `/owner/inbox` | owner-inbox | OwnerInboxPage.vue | Owner |
| `/owner/accounting` | owner-accounting | AccountingDashboardPage.vue | Owner |
| `/owner/accounting/chart-of-accounts` | owner-chart-of-accounts | ChartOfAccountsPage.vue | Owner |
| `/owner/accounting/journal-entries` | owner-journal-entries | JournalEntryListPage.vue | Owner |
| `/owner/accounting/journal-entries/new` | owner-journal-entry-new | JournalEntryCreatePage.vue | Owner |
| `/owner/accounting/journal-entries/:id` | owner-journal-entry-detail | JournalEntryDetailPage.vue | Owner |
| `/owner/accounting/trial-balance` | owner-trial-balance | TrialBalancePage.vue | Owner |
| `/owner/accounting/profit-loss` | owner-profit-loss | ProfitLossPage.vue | Owner |
| `/owner/accounting/balance-sheet` | owner-balance-sheet | BalanceSheetPage.vue | Owner |
| `/owner/accounting/general-ledger` | owner-general-ledger | GeneralLedgerPage.vue | Owner |
| `/owner/commissions` | owner-commissions | CommissionManagementPage.vue | Owner |
| `/owner/inventory` | owner-inventory | InventoryManagementPage.vue | Owner |
| `/owner/purchase-orders` | owner-purchase-orders | PurchaseOrderPage.vue | Owner |
| `/owner/suppliers` | owner-suppliers | SupplierManagementPage.vue | Owner |
| `/owner/stock-alerts` | owner-stock-alerts | StockAlertsPage.vue | Owner |
| `/employee` | employee-dashboard | EmployeeDashboard.vue | Employee |
| `/employee/clients` | employee-clients | CustomerManagementPage.vue | Employee |
| `/employee/orders` | employee-orders | OrderManagementPage.vue | Employee |
| `/employee/support` | employee-support | SupportInboxPage.vue | Employee |
| `/employee/earnings` | employee-earnings | EmployeeEarningsPage.vue | Employee |
| `/customer` | customer-dashboard | CustomerDashboard.vue | Customer |
| `/login` | login | LoginPage.vue | Guest only |
| `/register` | register | RegisterPage.vue | Guest only |
| `/superadmin` | superadmin-dashboard | SuperadminDashboard.vue | Superadmin |
| `/superadmin/owners` | superadmin-owners | OwnerManagementPage.vue | Superadmin |
| `/superadmin/owners/:id` | superadmin-owner-detail | OwnerDetailPage.vue | Superadmin |
| `/superadmin/branding/:id` | superadmin-branding | BrandingPage.vue | Superadmin |
| `/superadmin/inbox` | superadmin-inbox | SuperadminInboxPage.vue | Superadmin |
| `/supplier` | supplier-dashboard | SupplierPortalPage.vue | Supplier |

---

## 9. Pinia Stores

### auth (`stores/auth.js`)
**State**: `user`, `token`, `loading`, `mustChangePassword`
**Computed**: `isAuthenticated`, `isCustomer`, `isEmployee`, `isOwner`, `isSuperadmin`
**Actions**: `register(data)`, `login(data)`, `logout()`, `fetchProfile()`, `updateProfile(data)`, `changePassword(data)`
**Persistence**: token persisted to localStorage via pinia-plugin-persistedstate

### cart (`stores/cart.js`)
**State**: `items`, `loading`
**Computed**: `itemCount`, `subtotal`, `total`
**Actions**: `fetchCart()`, `addItem(variantId, qty)`, `updateItem(itemId, qty)`, `removeItem(itemId)`, `clearCart()`, `$reset()`

### products (`stores/products.js`)
**State**: product listing data, featured products, categories
**Actions**: `fetchProducts(params)`, `fetchFeatured()`, `fetchProduct(slug)`, `fetchCategories()`, `fetchCategory(slug)`

### session (`stores/session.js`)
**State**: `remaining` (seconds until logout), `showWarning`, `warningSeconds` (60 s countdown)
**Actions**: `start()`, `stop()`, `activity()`
**Behavior**: 15-minute inactivity timer with a 60-second warning modal; activity (mouse/keyboard/touch/scroll/click) resets the timer; tab-away longer than 10 minutes signs the user out on return; `session_last_active` persisted to localStorage so a closed tab opened after the idle window forces logout. Wired globally in `App.vue`; logout revokes the Sanctum token.

---

## 10. API Client (Axios)

File: `src/api/axios.js`
- Base URL: `VITE_API_URL` env var or `http://localhost:8000/api`
- 401 interceptor: clears token + redirects to `/login`
- Token attached via `Authorization: Bearer <token>` header

### API Modules (`src/api/index.js`)

| Module | Methods |
|---|---|
| `authApi` | `register`, `login`, `logout`, `getProfile`, `updateProfile`, `changePassword` |
| `employeeApi` | `getAll`, `create`, `toggleStatus`, `delete`, `assignBranch`, `resetPassword`, `updateProfile` |
| `customerApi` | `getAll`, `toggleStatus`, `delete` |
| `productApi` | `getAll(params)`, `getFeatured`, `getBySlug(slug)` |
| `productManageApi` | `getAll(params)`, `getById(id)`, `create(data)`, `update(id, data)`, `delete(id)` |
| `categoryApi` | `getAll`, `getBySlug(slug)` |
| `cartApi` | `get`, `add(data)`, `update(itemId, data)`, `remove(itemId)`, `clear()` |
| `orderApi` | `getAll(params)`, `create(data)`, `getById(id)` |
| `orderManageApi` | `getAll(params)`, `updateStatus(orderId, status)`, `updateDelivery(orderId, data)` |
| `reportApi` | `getDaily(date)`, `getSummary(params)` |
| `paymentApi` | `initiate(data)`, `getStatus(orderId)` |
| `addressApi` | `getAll`, `create(data)`, `update(id, data)`, `delete(id)` |
| `settingsApi` | `getPayment()`, `updatePayment(data)`, `getBranding()` |
| `paymentProviderApi` | `getAll`, `getEnabled`, `manage`, `create(data)`, `update(id, data)`, `delete(id)` |
| `shippingRuleApi` | `getAll`, `calculate(data)`, `create(data)`, `update(id, data)`, `delete(id)` |
| `supportApi` | `getAll(params)`, `create(data)`, `getById(id)`, `reply(id, data)`, `updateStatus(id, data)`, `getUnreadCount()` |
| `analyticsApi` | `getSales(months)`, `getAiSuggestions(data)` |
| `conversationApi` | `getAll(params)`, `create(data)`, `getById(id)`, `sendMessage(id, data)`, `updateStatus(id, data)`, `getOwnerDetails(id)`, `getCustomerDetails(id)`, `getUnreadCount()` |
| `branchApi` | `getAll`, `create(data)`, `update(id, data)`, `delete(id)`, `setDefault(id)` |
| `superadminApi` | `getStats`, `getOwners`, `createOwner`, `getOwner`, `updateOwner`, `deleteOwner`, `updateSubscription`, `updateLimits`, `updateBranding`, `uploadLogo`, `resetOwnerPassword` |
| `accountApi` | `getAll`, `getTree`, `getOne(id)`, `create(data)`, `update(id, data)`, `delete(id)`, `getBalance(id)` |
| `journalApi` | `getAll(params)`, `getOne(id)`, `create(data)`, `post(id)`, `void(id)`, `delete(id)` |
| `accountingReportApi` | `getTrialBalance(params)`, `getProfitLoss(params)`, `getBalanceSheet()`, `getGeneralLedger(params)`, `generateMonthly(data)`, `generateYearly(data)`, `listReports()`, `getReport(id)`, `getAiSuggestions(data)` |
| `commissionApi` | `getSummary(params)`, `pay(id)`, `payAll(data)`, `employeeEarnings(userId)` |
| `inventoryApi` | `getAll(params)`, `adjust(data)`, `getTransactions(params)`, `getLowStock()`, `getDashboard()` |
| `purchaseOrderApi` | `getAll(params)`, `getOne(id)`, `create(data)`, `receive(id)`, `delete(id)` |
| `employeeProfileApi` | `updateProfile(userId, data)` |
| `supplierApi` | `getAll(params)`, `getActive()`, `create(data)`, `getOne(id)`, `update(id, data)`, `delete(id)` |
| `stockAlertApi` | `getAll(params)`, `getCount()`, `acknowledge(id)`, `resolve(id)` |
| `notificationApi` | `getAll()`, `getCount()`, `markRead(id)`, `markAllRead()` |
| `supplierPortalApi` | `getProfile()`, `getOrders(params)`, `getOrder(id)`, `updateOrderStatus(id, data)` |

---

## 11. Image Handling

### Upload Flow
1. Owner uploads image via ProductFormPage (drag-drop or file picker)
2. Frontend sends `FormData` with `Content-Type: multipart/form-data`
3. Backend `ProductController@handleImage()`:
   - Generates unique filename: `time() + '_' + original_name`
   - Moves to `public/products/`
   - Returns relative path: `products/filename.ext`
4. Path stored in `products.image` column

### Display Flow
- Images are served from Laravel's public directory
- Frontend uses `imageUrl()` utility (`src/utils/image.js`) to resolve relative paths:
  ```js
  // Bare filename → auto-prepends /products/
  imageUrl('1784131294_shopping.webp')
  // → 'http://localhost:8000/products/1784131294_shopping.webp'

  // Path already with /products/ → passes through
  imageUrl('products/1784131294_shopping.webp')
  // → 'http://localhost:8000/products/1784131294_shopping.webp'

  // Full URL → passes through unchanged
  imageUrl('https://example.com/image.jpg')
  // → 'https://example.com/image.jpg'
  ```
- Bare filenames (without `/products/` prefix) get `/products/` prepended automatically
- Full URLs (`https://...`) pass through unchanged
- Fallback: `/placeholder.svg` if no image

---

## 12. Seeded Data

### Users
| Name | Email | Password | Role |
|---|---|---|---|
| Victor Zacharia | victorzacharia110@gmail.com | `P@ssword@electroshop` | owner |
| Mathew Zacharia | mathewzacharia@gmail.com | `MATHEW ZACHARIA` | employee |
| Zacharia Kinyula | zachariakinyula@gmail.com | `Password` | customer |
| Super Admin | superadmin@erp-electronics.com | `SuperAdmin@2026` | superadmin |

**Note**: Employee/Owner default password = `strtoupper(name)`. `password_changed_at` is null → forces password change on first login.

### Categories (4)
| English | Swahili | Slug |
|---|---|---|
| Phones | Simu | phones |
| Accessories | Vifaa | accessories |
| Audio | Sauti | audio |
| Wearables | Vifaa vya Kuvaa | wearables |

### Products (13 with images)
| Product | Brand | Category | Base Price (TSh) | Variants |
|---|---|---|---|---|
| Samsung Galaxy A15 | Samsung | Phones | 450,000 | 2 (Black/Blue 128GB) |
| iPhone 15 | Apple | Phones | 1,800,000 | 2 (Black 128GB, White 256GB) |
| Tecno Spark 20 Pro | Tecno | Phones | 350,000 | 1 (Green 256GB) |
| Xiaomi Redmi Note 13 | Xiaomi | Phones | 420,000 | 2 (Black 128GB, Blue 256GB) |
| Fast Charger 25W | Generic | Accessories | 35,000 | 2 (White/Black) |
| Silicone Phone Case | Generic | Accessories | 15,000 | 3 (Black/Blue/Red) |
| Tempered Glass Screen Protector | Generic | Accessories | 10,000 | 1 (Clear) |
| USB-C Cable 2m | Generic | Accessories | 12,000 | 1 (Black) |
| Wireless Earbuds Pro | Generic | Audio | 65,000 | 2 (White/Black) |
| Bluetooth Speaker Mini | Generic | Audio | 45,000 | 1 (Black) |
| Smart Watch S8 | Generic | Wearables | 85,000 | 2 (Black/Silver) |

### Payment Providers (5)
| Provider | Slug | Phone Number | Icon |
|---|---|---|---|
| M-Pesa | mpesa | 0794770268 | fas fa-mobile-screen |
| Airtel Money | airtel | 0683870268 | fas fa-signal |
| Mixx by Yas | mixx_by_yas | 0703870268 | fas fa-water |
| Halopesa | halopesa | 0632870268 | fas fa-bolt |
| Cash | cash | — | fas fa-money-bill-wave |

### Settings
| Key | Value | Type |
|---|---|---|
| `clickpesa_enabled` | `false` | boolean |

### Seeded Journal Entries (22 entries across May–July 2026)
All entries are posted for owner_id=1 (Victor Zacharia). Demonstrates full double-entry bookkeeping cycle.

| Month | Reference | Description | Debit (TSh) | Credit (TSh) |
|---|---|---|---|---|
| May | JE-20260501-001 | Capital investment — owner invests in business | Cash: 5,000,000 | Owner's Equity: 5,000,000 |
| May | JE-20260505-002 | Inventory purchase — Samsung Galaxy A15 | Inventory: 1,200,000 | Accounts Payable: 1,200,000 |
| May | JE-20260510-003 | Sale — Samsung Galaxy A15 | Accounts Receivable: 450,000 | Sales Revenue: 450,000 |
| May | JE-20260510-004 | COGS — Samsung Galaxy A15 | Cost of Goods Sold: 300,000 | Inventory: 300,000 |
| May | JE-20260512-005 | Sale — iPhone 15 | Accounts Receivable: 1,800,000 | Sales Revenue: 1,800,000 |
| May | JE-20260512-006 | COGS — iPhone 15 | Cost of Goods Sold: 1,200,000 | Inventory: 1,200,000 |
| May | JE-20260515-007 | Rent — May shop rent | Rent Expense: 500,000 | Cash: 500,000 |
| May | JE-20260520-008 | Utilities — electricity | Utilities Expense: 80,000 | Cash: 80,000 |
| May | JE-20260525-009 | Sale — Tecno Spark 20 Pro | Accounts Receivable: 350,000 | Sales Revenue: 350,000 |
| May | JE-20260525-010 | COGS — Tecno Spark 20 Pro | Cost of Goods Sold: 200,000 | Inventory: 200,000 |
| June | JE-20260601-011 | Rent — June shop rent | Rent Expense: 500,000 | Cash: 500,000 |
| June | JE-20260605-012 | Inventory purchase — accessories restock | Inventory: 800,000 | Accounts Payable: 800,000 |
| June | JE-20260610-013 | Sale — Xiaomi Redmi Note 13 | Accounts Receivable: 420,000 | Sales Revenue: 420,000 |
| June | JE-20260610-014 | COGS — Xiaomi Redmi Note 13 | Cost of Goods Sold: 280,000 | Inventory: 280,000 |
| June | JE-20260615-015 | Employee salaries — June | Salaries Expense: 600,000 | Cash: 600,000 |
| June | JE-20260620-016 | Marketing — social media ads | Marketing Expense: 150,000 | Cash: 150,000 |
| June | JE-20260625-017 | Sale — Wireless Earbuds Pro | Accounts Receivable: 65,000 | Sales Revenue: 65,000 |
| June | JE-20260625-018 | COGS — Wireless Earbuds Pro | Cost of Goods Sold: 40,000 | Inventory: 40,000 |
| July | JE-20260701-019 | Rent — July shop rent | Rent Expense: 500,000 | Cash: 500,000 |
| July | JE-20260705-020 | Bank charges — monthly fees | Bank Charges: 25,000 | Cash: 25,000 |
| July | JE-20260710-021 | Supplier payment — partial AP settle | Accounts Payable: 1,000,000 | Cash: 1,000,000 |
| July | JE-20260715-022 | Sale — Smart Watch S8 | Accounts Receivable: 85,000 | Sales Revenue: 85,000 |
| July | JE-20260715-023 | COGS — Smart Watch S8 | Cost of Goods Sold: 55,000 | Inventory: 55,000 |

**Summary**: Total Revenue TSh 3,920,000 | Total COGS TSh 2,355,000 | Gross Profit TSh 1,565,000 | Total Expenses TSh 1,905,000

### Shipping Rules (3 wildcard tiers)
| Name | From | To | Base Cost | Value Tiers |
|---|---|---|---|---|
| Nationwide ≥1M | * | * | 98,000 | ≥TSh 1M → 98,000 |
| Nationwide 300K-999K | * | * | 50,000 | 300K–999K → 50,000 |
| Nationwide <300K | * | * | 25,000 | <TSh 300K → 25,000 |

---

## 13. Key Features & Business Logic

### Order Status Flow
```
pending_payment (cart) → pending (order placed) → paid → processing → shipped → delivered
                             ↓                       ↓
                          inactive              cancelled
                             ↓
                     (auto-deleted after 6h)
```

- **pending_payment**: Cart state — order exists but not yet checked out
- **pending**: Order placed, awaiting payment confirmation
- **inactive**: Unpaid order older than 3 hours (auto-set by scheduler)
- **paid**: Payment confirmed (employee or auto for Cash/ClickPesa)
- **processing**: Order being prepared
- **shipped**: Order shipped with tracking number
- **delivered**: Order delivered to customer
- **cancelled**: Order cancelled (inventory restored from paid/processing)

### Auto-Cancel & Auto-Delete Unpaid Orders
- **Scheduler**: `orders:cleanup-unpaid` runs every 5 minutes
- After **3 hours** unpaid: status → `inactive` (grey badge)
- After **6 hours** total: order **deleted** from database
- Registered in `routes/console.php`

### Order Placement Flow
1. Customer adds items to cart → proceeds to checkout
2. Selects delivery address
3. Chooses delivery option: **Pickup** (free) or **Home Delivery** (dynamic cost)
4. Selects payment provider (Cash, M-Pesa, Airtel, Mixx by Yas, Halopesa, ClickPesa)
5. `POST /orders` creates order with status `pending`
6. Payment initiated via `POST /payments/initiate`
7. **Cash**: Auto-confirmed immediately (employee receives cash at counter)
8. **ClickPesa**: Auto-confirmed immediately (gateway handles verification)
9. **Mobile Money**: Goes to `pending` → employee confirms via modal (types customer name IN CAPS)
10. On payment success → status becomes `paid` → **inventory auto-decremented**
11. Employee/owner processes order → `processing` → `shipped` → `delivered`
12. Can cancel from `paid` or `processing` → **inventory auto-restored**

### Inventory Management
- Each `ProductVariant` has one `Inventory` record
- `quantity_on_hand` decremented when order status → `paid`
- `quantity_on_hand` restored when order cancelled from `paid`/`processing`
- `reorder_level` field exists (default 10) — future low-stock alerts

### Payment Confirmation (Employee)
- OrderManagementPage shows pending orders with yellow alert
- Employee clicks "Confirm Payment" → modal shows order details + provider + phone
- Employee types customer name **IN CAPS** to verify
- `handled_by` tracks which employee confirmed

### Delivery System
- Checkout offers **Pickup** (free) vs **Home Delivery** (dynamic cost)
- Owner manages shipping rules via `/owner/shipping`:
  - Routes: from_city → to_city with base cost
  - Wildcard rules (`*`) apply to all routes
  - Value-based tiers: orders above certain amount get different rates
- Shipping cost calculated dynamically based on destination city + cart subtotal
- Employee/owner can add tracking number and delivery notes after shipping

### Branch System
- `branches` table with owner_id, name, city, address, phone, is_active, is_default
- Nullable `branch_id` on `orders` and `employee_profiles`
- Everything works without branches — scalable to multi-branch later
- Owner CRUD via `/owner/branches`
- Branch filter on employee management and order management
- Branch assignment for employees (`PATCH /employees/{user}/branch`)

### Support Messaging
- Customers send messages about payment issues, order status, delivery, refunds
- Employees/owner reply via support inbox (`/employee/support`)
- Categories: payment_issue, order_status, delivery, refund, general
- Statuses: open → in_progress → resolved → closed
- Employee dashboard shows unread message count with alert banner
- Unread count badge on support inbox link

### Accounting System (Double-Entry Bookkeeping)
- Full double-entry bookkeeping with chart of accounts, journal entries, and financial reports
- **Chart of Accounts**: 22 default accounts seeded (assets, liabilities, equity, revenue, expenses)
- **Journal Entries**: Auto-generated for order payment, cancellation, PO receive, salary payout, commission payout
- **Auto-Journal Chain** (on order payment):
  - DR: Accounts Receivable, CR: Sales Revenue
  - DR: Cost of Goods Sold, CR: Inventory
- **Cancellation Reversal**: All original entries reversed, inventory restored, commission deleted
- **Financial Reports**: Trial Balance, Profit & Loss, Balance Sheet, General Ledger
- **Report Generation**: Monthly/yearly reports stored in `accounting_reports` table with full JSON data
  - `POST /reports/generate-monthly` — generate report for specific month
  - `POST /reports/generate-yearly` — generate report for specific year
  - Reports include trial balance, P&L, balance sheet, general ledger, and summary
- **Bilingual AI Suggestions**: AI analyzes accounting data and returns Swahili + English suggestions
  - `POST /reports/ai-suggestions` — generates prioritized actionable insights
  - Returns `{ title_sw, title_en, description_sw, description_en, priority, category, impact }`
- **Manual Entries**: Owner can create journal entries with multiple debit/credit lines
- Reference numbers auto-generated (JE-YYYYMMDD-XXX, PO-YYYYMMDD-XXX)
- Status flow: Draft → Posted → Voided
- **Employee Access**: Employees can access accounting reports through `resolveOwner()` via branch relationship
- **Seeded Data**: 22 journal entries across May–July 2026 demonstrating full business cycle

### Commission System
- Employee commission rate configurable per employee (e.g., 5% of profit)
- **Profit-based**: Commission is calculated on profit (selling price - cost price), not revenue
- Auto-calculated when order status changes to `paid` and handler is employee with commission_rate > 0
- Formula: `commission = (order subtotal - total cost) × (commission_rate / 100)`
- Commission status: `pending` → `paid_out` (when owner pays out)
- Owner can pay individual commission or pay all at once
- Each pay-out creates journal entry: DR Commission Expense, CR Cash
- Employee sees own earnings at `/employee/earnings` — shows total profit generated, pending/paid commissions

### Inventory Management
- Every stock change creates an `inventory_transactions` row
- Transaction types: `sale`, `return`, `purchase`, `adjustment`, `damage`, `opening`
- Auto-creates transactions on order payment (sale) and cancellation (return)
- Stock adjustment modal: select variant → type → quantity → notes
- Transaction history with search, date range, and type filter
- Low stock detection: checks reorder_level after every stock change

### Purchase Orders
- Full PO lifecycle: `draft` → `ordered` → `received`
- Auto-generated PO numbers (PO-YYYYMMDD-XXX)
- Line items: product variant, quantity, unit cost
- **Receive PO**: auto-updates inventory + creates journal entries (DR Inventory, CR Accounts Payable)
- Supplier linking for vendor tracking

### Supplier Management
- Full CRUD: name, contact person, phone, email, address, city, country, products description, notes
- Supplier portal: suppliers log in with `supplier` role to view their POs and update status
- Search and filter by any field

### Stock Alerts
- Auto-created when inventory drops to/below reorder_level
- Types: `low_stock` (quantity > 0 but ≤ reorder_level), `out_of_stock` (quantity = 0)
- Triggered from: order payment, PO receive, stock adjustment
- Owner can Acknowledge → Resolve alerts
- Badge count on OwnerDashboard tile

### Notifications
- In-app notification system for stock alerts and other events
- Mark read / mark all read
- Notification bell component (planned)

### Conversations System
- **Types**: `superadmin_owner` (superadmin↔owner), `customer_owner` (customer↔owner)
- Bidirectional messaging within each conversation
- Unread badge polling (15 seconds) on all layouts
- Detail panels: owner details (company, plan, branch, phone, location), customer details (email, phone, location)
- Conversation locking when closed (read-only mode)

### Category Translation
- Categories have `name` (English) and `name_sw` (Swahili) columns
- `translated_name` accessor on Category model returns correct name based on request locale
- API returns `translated_name` field for frontend to display
- Seeded: Phones/Simu, Accessories/Vifaa, Audio/Sauti, Wearables/Vifaa vya Kuvaa

### Daily Reports
- Auto-generated via `report:daily` artisan command (scheduled at 00:10)
- Stored in `daily_reports` table
- Includes: total orders, revenue, customer count, per-employee stats, top products
- Employee stats track `handled_by` field (who confirmed sales)
- Owner can view by date with print support at `/owner/reports`

### Password Expiry
- Employees created with default password = `strtoupper(name)`
- `password_changed_at` set to null → `mustChangePassword()` returns true
- Frontend shows modal forcing password change
- Also triggers if password hasn't been changed in 3+ days

### Password Management
- **Owner → Employee**: Owner can reset any employee password to default (`strtoupper(name)`) via modal on EmployeeManagementPage
- **Superadmin → Owner**: Superadmin can reset any owner password to default (`strtoupper(name)`) via OwnerDetailPage
- **Superadmin Auto-Reset**: Every 6 months, superadmin password auto-resets to `SuperAdmin@2026` via `php artisan superadmin:reset-password`
  - Scheduled monthly but only triggers when 6-month threshold is reached
  - `User::superadminPasswordExpired()` checks `password_changed_at` age
  - Login/profile responses return `superadmin_password_expired` boolean for superadmin users
- **Owner Profile**: Owners can edit name, phone, and branding fields but NOT their own password (superadmin-only)

### Accounting Report Generation
- **Monthly Reports**: `POST /reports/generate-monthly` with `month` and `year` params
- **Yearly Reports**: `POST /reports/generate-yearly` with `year` param
- Reports stored in `accounting_reports` table with full JSON data (trial balance, P&L, balance sheet, general ledger)
- `AccountingReportService` computes all financial data from posted journal entries
- Trial balance response uses nested `account` object format: `{ account: { id, code, name, type }, debit, credit }`
- Owner can list, view, and generate AI suggestions for any saved report
- Employee accounting access resolved through `resolveOwner()` method (via branch relationship)

### Bilingual AI Suggestions
- All AI suggestion endpoints return both Swahili and English fields:
  ```json
  {
    "title_sw": "Ongeza Bei ya Bidhaa",
    "title_en": "Increase Product Pricing",
    "description_sw": "Bei yako ni chini ya soko...",
    "description_en": "Your pricing is below market...",
    "priority": "high",
    "category": "pricing",
    "impact": "Potential 15% revenue increase"
  }
  ```
- Swahili is default display language; English toggled via language switcher
- Applied to both `AnalyticsController::aiSuggestions` and `AccountingReportController::aiSuggestions`
- Backend strips backtick characters from Gemini responses using manual char-by-char loop (PHP 8.4 backtick parsing workaround)

### Product Management (Owner)
- Add/edit/delete products with image upload
- Support multiple variants per product (color, storage, SKU, price, cost_price)
- Each variant has its own inventory count
- Image stored in `public/products/`
- Product slugs auto-generated from name

### Employee Management (Owner)
- Owner adds employees via form — default password = UPPERCASE FULL NAME
- Registration form: full name, email, phone, **NIDA or Voting ID number**, branch, position, department, commission rate (0–100)
- **Wadhamini (Guarantors)**: at least one guarantor required — name, phone, relationship, address
- **Attachments**: contract, background check, and other documents (PDF/JPG/PNG/DOC/DOCX, ≤ 20 MB) stored on the filesystem disk
- **Edit employee**: pencil icon opens a pre-filled form — name, email, phone, identification, branch, position, department, commission rate, and guarantor replacement
- List all employees with status + branch
- Toggle active/inactive status
- Assign employees to branches
- **Reset employee password** to default via modal (returns default password for owner to share)
- Delete employees

### Customer Management (Employee)
- Employees can list all customers
- Toggle customer active/inactive status
- Delete customers

### Payment Provider Management (Owner)
- Full CRUD for payment providers at `/owner/payment-settings`
- Add/edit/delete providers with name, slug, phone number, icon
- Enable/disable individual providers
- 4 default mobile money providers always shown at checkout
- ClickPesa toggleable separately via settings

### Sales Analytics (Owner Dashboard)
- Monthly data aggregation from paid orders (revenue, profit, cost, items sold)
- Revenue vs Profit bar chart, Orders Trend line chart, Items Sold bar chart, Category Revenue doughnut chart
- Period selector: 6 or 12 months
- Summary cards: Total Revenue, Total Profit, Total Orders, Profit Margin, Revenue Growth
- Data includes cancelled order tracking and lost revenue

### AI Business Insights (Owner Dashboard)
- Backend proxy to Google Gemini 2.0 Flash API
- Sends sales summary, monthly trends, category breakdown, and top products to Gemini
- Gemini returns 5–7 prioritized actionable suggestions (inventory, pricing, marketing, growth, operations)
- Fallback suggestions generated when Gemini API fails (margin analysis, growth trends, seasonal prompts)
- Suggestions displayed with priority badges (high/medium/low) and category icons
- Refresh button to regenerate insights on demand

### Superadmin Dashboard
- System-wide statistics: total owners, total customers, total orders, total revenue
- Owner management: CRUD with subscription and limits
- White-label branding per owner: store name, tagline, logo, colors
- Owner default password = `strtoupper(name)`; `password_changed_at` NOT set → forces change on first login
- Response returns `default_password` for superadmin to share
- **Reset owner password**: Superadmin can reset any owner's password to default from OwnerDetailPage
- Conversation with owners via inbox
- **Superadmin password auto-resets** every 6 months via `php artisan superadmin:reset-password`

### PDF User Manuals
- English (`docs/User_Manual_EN.pdf`) and Swahili (`docs/User_Manual_SW.pdf`) versions
- 18-page comprehensive manuals covering all three roles (Owner, Employee, Customer)
- Generated via `generate_manual.py` using ReportLab with DejaVu font for Swahili support
- Chapters: Getting Started, Dashboard, Employee/Product/Payment/Shipping Management, Reports, Orders, Support, Shopping, Checkout, Account, Language, Password Policy

---

## 14. Internationalization (i18n)

### Setup
- **Library**: `vue-i18n` v10
- **Default language**: Swahili (`sw`)
- **Fallback language**: English (`en`)
- **Config**: `src/locales/i18n.js`
- **Translation files**: `src/locales/sw.json`, `src/locales/en.json` (~900+ keys each)
- **Persistence**: Language choice saved to `localStorage` (key: `locale`)

### How It Works
- In templates: `{{ $t('key') }}` or `{{ $t('key', { param: value }) }}`
- In script: `const { t } = useI18n()` then `t('key')`
- Language switcher in the header toggles between SW/EN
- Default locale is Swahili — the site loads in Swahili first
- `@` character in translations must be escaped: `{'@'}` (vue-i18n linked message syntax)

### Translation Structure
```
src/locales/
├── i18n.js          # createI18n config, imports sw.json + en.json
├── sw.json          # Swahili translations (default)
└── en.json          # English translations (fallback)
```

### Key Namespaces
| Namespace | Purpose |
|---|---|
| `common` | Shared labels: loading, save, cancel, delete, currency, etc. |
| `nav` | Navigation: Home, Products, Cart, Dashboard, Login, Logout, Register, Inbox |
| `topBar` | Top bar contact info + language switcher tooltips |
| `footer` | Footer text and links |
| `search` | Search bar placeholder and empty states |
| `home` | Homepage: hero, features, categories, promo, CTA |
| `auth` | Login/Register: labels, placeholders, validation, errors |
| `cart` | Cart page: title, summary, buttons |
| `product` | Product: brand, variants, stock, buttons |
| `checkout` | Checkout: address, payment, delivery options, summary |
| `orders` | Customer orders page |
| `account` | Account/profile page |
| `support` | Customer support messaging |
| `inbox` | Conversation inbox (superadmin↔owner, customer↔owner) |
| `branches` | Branch management (CRUD, set default) |
| `dashboards.owner` | Owner dashboard: stats, quick actions, alerts |
| `dashboards.employee` | Employee dashboard: stats, alerts, quick actions |
| `dashboards.customer` | Customer dashboard: stats, account reminder |
| `employees` | Employee management: list, add modal, delete, branch assignment |
| `customers` | Customer management: list, columns, actions |
| `ordersManage` | Order management: filters, confirm payment, delivery, status actions |
| `reports` | Daily reports: stats, employee performance, top products |
| `productsManage` | Product management: grid, search, delete |
| `productForm` | Product add/edit form: fields, variants, image upload |
| `paymentSettings` | Payment settings: ClickPesa toggle, provider CRUD |
| `shippingSettings` | Shipping settings: routes, value rules, CRUD |
| `changePassword` | Password change modal |
| `superadmin` | Superadmin dashboard, owner management, branding, inbox |
| `ownerInbox` | Owner inbox: conversations with superadmin + customers |
| `customerInbox` | Customer inbox: conversations with owner |
| `accounting` | Accounting: chart of accounts, journal entries, reports |
| `commissions` | Commission management: summary, pay, employee earnings |
| `inventory` | Inventory: stock dashboard, adjustments, transaction history |
| `purchaseOrders` | Purchase orders: list, create, receive |
| `suppliers` | Supplier management: CRUD, portal |
| `stockAlerts` | Stock alerts: low stock, out of stock, acknowledge/resolve |
| `supplierPortal` | Supplier portal: PO list, details, status update |
| `notifications` | Notifications: bell, mark read |

### Files Updated
All 45+ Vue components use `$t()` / `t()` instead of hardcoded English text:
- StoreLayout (top bar, nav, footer), SuperadminLayout, ChangePasswordModal
- HomePage, LoginPage, RegisterPage
- CartPage, CheckoutPage (including delivery options)
- ProductDetailPage, ProductListPage, CategoryPage
- OrdersPage, AccountPage, SupportPage
- OwnerDashboard, EmployeeDashboard, CustomerDashboard
- EmployeeManagementPage, CustomerManagementPage, OrderManagementPage
- ReportsPage, ProductManagementPage, ProductFormPage
- PaymentSettingsPage, ShippingSettingsPage, SupportInboxPage
- BranchManagementPage, OwnerInboxPage, CustomerInboxPage
- SuperadminDashboard, OwnerManagementPage, OwnerDetailPage, BrandingPage, SuperadminInboxPage
- AccountingDashboardPage, ChartOfAccountsPage, JournalEntryListPage, JournalEntryCreatePage, JournalEntryDetailPage
- TrialBalancePage, ProfitLossPage, BalanceSheetPage, GeneralLedgerPage
- CommissionManagementPage, InventoryManagementPage, PurchaseOrderPage
- EmployeeEarningsPage, SupplierManagementPage, StockAlertsPage, SupplierPortalPage

### Adding a New Language
1. Create `src/locales/xx.json` with all translation keys
2. Import it in `src/locales/i18n.js` and add to `messages`
3. Add a case in the `toggleLocale` function in `StoreLayout.vue`

---

## 15. Development Commands

### Frontend
```bash
cd erp-electronics/
npm run dev          # Start Vite dev server (port 5173)
npm run build        # Production build
npm run lint         # Run oxlint + eslint
npm run format       # Format with oxfmt
npm run test:unit    # Run vitest
npm run test:e2e     # Run playwright
```

### Backend
```bash
cd erp-electronics-api/
php artisan serve                    # Start dev server (port 8000)
php artisan migrate                  # Run migrations
php artisan migrate:fresh --seed     # Reset database + re-seed
php artisan db:seed                  # Seed database
php artisan report:daily             # Generate daily report
php artisan orders:cleanup-unpaid    # Manually run unpaid order cleanup
php artisan superadmin:reset-password # Auto-reset superadmin password (if 6 months elapsed)
php artisan schedule:work            # Start scheduler (run in separate terminal)
php artisan schedule:list            # View scheduled tasks
php artisan route:list               # List all routes
```

### Environment Variables
```env
# Frontend (.env)
VITE_API_URL=http://localhost:8000/api

# Backend (.env)
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
GEMINI_API_KEY=your-gemini-api-key
```

---

## 16. Analytics & AI Insights

### Backend
- **Controller**: `app/Http/Controllers/Api/AnalyticsController.php`
- **Routes**: `GET /analytics/sales`, `POST /analytics/ai-suggestions` (owner-only)
- **Config**: `config/services.php` → `gemini.key` (from `GEMINI_API_KEY` env)

#### `sales()` Method
- Accepts `?months=12` query parameter (default 12)
- Queries 4 data sets in parallel: monthly sales, monthly items, monthly profit, monthly cancelled
- Generates complete month list from start to end date (no gaps)
- Returns: `monthly[]`, `category_breakdown[]`, `top_products[]`, `summary{}`
- Summary includes: total_revenue, total_profit, total_orders, total_items_sold, avg_order_value, profit_margin, revenue_growth, order_growth

#### `aiSuggestions()` Method
- Accepts `{ analytics: {...} }` POST body (the full sales data)
- Builds detailed prompt with Tanzania-specific business context
- Calls Gemini 2.0 Flash API with temperature=0.7, maxOutputTokens=2048
- Parses JSON response or falls back to rule-based suggestions
- Returns: `suggestions[]` with bilingual fields:
  - `title_sw` / `title_en` — Swahili and English titles
  - `description_sw` / `description_en` — Swahili and English descriptions
  - `priority` — high/medium/low
  - `category` — inventory/pricing/marketing/growth/operations
  - `impact` — expected business impact
- `source` field: "ai" or "fallback"
- Backtick characters stripped from Gemini responses (PHP 8.4 workaround)

### Frontend
- **Components**: `src/pages/dashboards/analytics/SalesCharts.vue`, `AiSuggestions.vue`
- **API**: `analyticsApi.getSales(months)`, `analyticsApi.getAiSuggestions(data)` in `src/api/index.js`
- **Dependencies**: `chart.js` + `vue-chartjs`
- **Integration**: Both components embedded in `OwnerDashboard.vue`

---

## 17. PDF Documentation

### Files
| File | Language | Pages |
|---|---|---|
| `docs/User_Manual_EN.pdf` | English | 29 |
| `docs/User_Manual_SW.pdf` | Swahili | 30 |
| `docs/Developer_Documentation.pdf` | English (developers) | 22 |

### Generator Scripts
- `generate_manual.py` — Python script using ReportLab for the user manuals (EN + SW)
- `generate_dev_doc.py` — Python script using ReportLab for the developer documentation
- DejaVu Sans font for full Swahili character support
- Styled PDFs with cover page, table of contents, numbered steps, info tables, code blocks, brand color swatches, and notes

### User Manual Chapters (v3.0)
1. Getting Started (login, default credentials)
2. Owner Dashboard (stats, charts, AI insights)
3. Employee Management (registration with NIDA/voting ID, branch, position, commission rate, Wadhamini guarantors, attachments; editing employees)
4. Product Management (CRUD, variants, image upload)
5. Payment Settings (ClickPesa toggle, mobile money providers)
6. Shipping Settings (routes, value-based pricing)
7. Reports & Analytics (daily reports, sales charts, AI insights)
8. Employee Dashboard (overview, alerts, quick actions)
9. Order Management (filtering, payment confirmation, status updates, branch filter)
10. Customer Management (list, add, toggle, delete)
11. Support Inbox (view messages, reply)
12. Customer Shopping (browse, cart)
13. Checkout & Payment (delivery options, payment methods)
14. My Account (orders, support, addresses)
15. Language Settings (English/Swahili toggle)
16. Password Policy (requirements, forced change, default passwords)
17. Session & Security (idle timeout, leaving the dashboard, login security)

**Note**: The superadmin dashboard is deliberately excluded from the user manuals — it is covered in the developer documentation instead.

### Developer Documentation Chapters (v1.0)
Document control, system overview & architecture, technology stack, brand identity & visual guidelines (logo, color palette, white-label colors, typography), roles & permissions, database schema & models, authentication & authorization, API reference (with rate limits), superadmin module (full), security measures, analytics & AI, documentation & diagrams, development commands & environment, deployment, and the full business cycle.

---

## 18. System Diagrams

All diagrams are in `.drawio` format — openable at https://app.diagrams.net (no desktop install needed).

### Files
| File | Description | Contents |
|---|---|---|
| `docs/ERD.drawio` | Entity Relationship Diagram | 28 tables, 35+ relationships, crow's foot notation |
| `docs/ClassDiagram.drawio` | UML Class Diagram | 28 model classes with attributes, methods, and relationships |
| `docs/UseCase.drawio` | UML Use Case Diagram | 6 actors, 45+ use cases, include/extend relationships |
| `docs/SequenceDiagrams.drawio` | UML Sequence Diagrams | 7 flows: Customer Checkout, Employee Order Processing, Owner Branch+Employee Management, Accounting Flow, Commission Flow, Inventory Flow, Purchase Order Flow |

### ERD Tables
users, customer_profiles, employee_profiles, owner_profiles, categories, products, product_variants, inventory, addresses, branches, orders, order_items, payments, payment_providers, shipping_rules, support_messages, conversations, conversation_messages, accounts, journal_entries, journal_lines, commissions, inventory_transactions, purchase_orders, purchase_order_items, suppliers, stock_alerts, notifications, accounting_reports

### Sequence Diagram Flows
1. **Customer Checkout** — Cart → Address → Delivery → Payment → Inventory → Confirmation
2. **Employee Order Processing** — Login → Order List → Confirm Payment (type name) → Ship
3. **Owner Branch+Employee Management** — Login → Branch CRUD → Employee CRUD with branch assignment
4. **Accounting Flow** — Order Paid → Auto-Journal (Revenue + COGS) → Reports
5. **Commission Flow** — Employee Handles Order → Commission Created → Owner Pays Out
6. **Inventory Flow** — Stock Change → Transaction Logged → Low Stock Check → Alert Created
7. **Purchase Order Flow** — Create PO → Supplier Confirms → Receive → Stock Updated + Journal Created

---

*Last updated: July 31, 2026*

---

## 19. Full Business Cycle

### Customer Journey
1. **Browse** → Store homepage, product list, category pages, search
2. **Add to Cart** → Select variant (color/storage), quantity
3. **Checkout** → Login/register, select delivery (Pickup free / Home Delivery TSh 25K–98K), select payment (Cash/M-Pesa/Airtel/Mixx/Halopesa)
4. **Order Created** → Status: `pending_payment`
5. **Payment** → Cash/ClickPesa auto-confirmed; Mobile Money → employee confirms
6. **On Paid** → Revenue journal + COGS journal + inventory decremented + stock alerts checked + commission calculated
7. **Processing** → Employee/owner prepares order
8. **Shipped** → Tracking number assigned
9. **Delivered** → Order complete
10. **Cancel** (any stage) → Reversal journals + inventory restocked + commission deleted

### Employee Flow
1. **Login** → Employee Dashboard with stats and quick actions
2. **Confirm Payment** → Open pending order → Confirm payment → Order goes to `paid`
3. **Process Order** → Update status: paid → processing → shipped → delivered
4. **View Earnings** → See commission summary at `/employee/earnings`
5. **Stock Alerts** → View alerts from inventory changes

### Owner Flow
1. **Dashboard** → Revenue, orders, products, employees, stock alerts badge
2. **Product Management** → CRUD products + variants + images
3. **Employee Management** → Add employees with commission_rate, assign branches
4. **Order Management** → All orders, filters, status updates, payment confirmation
5. **Inventory Management** → Stock dashboard, adjustments, transaction history
6. **Supplier Management** → CRUD suppliers, link to POs
7. **Purchase Orders** → Create POs, receive (auto stock + journal)
8. **Commissions** → View summary, pay individual or all
9. **Accounting** → Chart of accounts, journal entries, trial balance, P&L, balance sheet, general ledger
10. **Stock Alerts** → View, acknowledge, resolve low stock alerts
11. **Branch Management** → Multi-branch support
12. **Reports** → Daily reports, sales analytics, AI insights
13. **Support** → Customer conversations

### Supplier Flow
1. **Login** → Supplier Portal with company name
2. **View POs** → See all purchase orders from this owner
3. **PO Details** → View items, quantities, costs
4. **Update Status** → Mark as received when delivery arrives

### Auto-Journal Chain
```
Customer pays TSh 500,000
  → DR: Accounts Receivable 500,000
  → CR: Sales Revenue 500,000
  → DR: Cost of Goods Sold 300,000
  → CR: Inventory 300,000
  → Inventory transactions created
  → Stock alerts checked
  → Commission calculated: profit = 200,000 × 5% = TSh 10,000

Order cancelled
  → DR: Sales Revenue 500,000
  → CR: Accounts Receivable 500,000
  → DR: Inventory 300,000
  → CR: Cost of Goods Sold 300,000
  → Stock restored
  → Commission deleted

Owner pays commission
  → DR: Commission Expense 25,000
  → CR: Cash 25,000
```

---

## 20. Changelog

### 2026-08-03 — Product form translations fixed
- **Issue**: The owner product edit/create route (`/owner/products/:id/edit` and `/owner/products/new`) referenced `productForm.updateProduct`, `createProduct`, `updatedSuccessfully` and `createdSuccessfully` keys that were **missing from both `src/locales/en.json` and `src/locales/sw.json`**. vue-i18n rendered the raw key (e.g. `productForm.updateProduct`) on the submit button and success toast.
- **Fix**: Added all four keys to both locale files. The Swahili submit label uses **"Sahihisha Bidhaa"** ("correct product") instead of the previously used wording, and the success toast uses **"Bidhaa imesahihishwa!"**.
- **Files**: `src/locales/en.json`, `src/locales/sw.json`

### 2026-08-03 — DB-driven home content (superadmin Home Content editor)
- **What**: The storefront (`HomePage.vue`) and directory (`DirectoryPage.vue`) copy was previously hardcoded in `src/locales/*.json` under the `home.*` and `directory.*` keys. It is now stored in the DB as a single `home_content` setting (type `json`) holding `en` and `sw` objects — 44 keys (36 storefront + 8 directory prefixed `dir*`).
- **Backend** (`erp-electronics-api`): `SettingsController` gained `homeContent()` (public GET, returns stored values merged over seeded defaults so no key is ever empty) and `updateHomeContent()` (superadmin PUT, whitelist-sanitized). Routes: `GET /api/settings/home-content`, `PUT /api/superadmin/settings/home-content`. Migration `2026_08_03_000001_seed_home_content_setting.php` seeds the EN/SW defaults. Tests in `tests/Feature/HomeContentTest.php` (4 tests).
- **Frontend**: New `src/pages/superadmin/HomeContentPage.vue` (route `/superadmin/home-content`, nav "Home Content" in `SuperadminLayout.vue`) with 8 grouped sections, EN+SW inputs per field and Save All. `settingsApi.getHomeContent()` + `superadminApi.updateHomeContent()` in `src/api/index.js`. `HomePage.vue`/`DirectoryPage.vue` load DB content on mount via `hc()`/`dc()` helpers with i18n fallback.
- **`{count}` placeholders**: Fields like `productsCount`, `dirProductsCount`, `dirNewArrivals` contain `{count}`, substituted at render time with the real product/new-item count (`productsCountLabel()`, `dirProductsCountLabel()`, `dirNewArrivalsLabel()`). The literal `{count}` shown in the admin editor inputs is intentional — visitors always see the number. A helper hint under those fields explains this.
- **Notes**: Home content is a **superadmin-only** feature — it must NOT be documented in the user/supplier manuals. Local dev stores under slug `electroshop`; public GET verified live returning 44 keys.

### 2026-08-03 — Conversation & message deletion
- **Backend** (`erp-electronics-api`): `DELETE /api/conversations/{conversation}` (remove a whole chat thread) and `DELETE /api/conversations/{conversation}/messages/{messageId}` (remove a single message), scoped to participants.
- **Frontend**: inbox pages expose delete actions for the whole conversation and individual messages.
- **API route count**: revised from 175 to 179 in the developer documentation.

### 2026-08-04 — Per-store WhatsApp, contact & social fields
- **Backend** (`erp-electronics-api`): migration `2026_08_04_000004_add_store_contact_social_to_businesses.php` added `whatsapp_number`, `whatsapp_default_message`, `contact_phone`, `contact_email`, `address`, `facebook_url`, `instagram_url`, `twitter_url`, `tiktok_url`, `youtube_url` to `businesses`. `BusinessController` gained `update()` (`PUT /api/businesses/{business}`). `present()` now resolves the storefront WhatsApp number via the chain **business.whatsapp_number → first employee phone (branch-scoped) → owner_profiles.whatsapp_number → owner phone**, and the message via **business.whatsapp_default_message → owner_profiles.whatsapp_default_message → "Hello {store}! I would like to know more about your products."**. Migration `2026_08_04_000007_add_whatsapp_to_owner_profiles.php` added the per-owner WhatsApp fields; `2026_08_04_000002_backfill_missing_businesses.php` and `2026_08_04_000003_ensure_employee_branch_attribution.php` fix historical data. Employee routes were also strictly scoped to the owner's branches (commit `7437207`).
- **Frontend**: new `src/pages/owner/StoreSettingsPage.vue` (route `owner/store-settings`, nav "Store Settings") edits WhatsApp number/message, contact phone/email, address, and the social links, saving via `businessApi.update()`. New `src/components/PhoneInput.vue` (country code dropdown, 19 countries, default +255 Tanzania, live per-country masking) replaces raw phone fields across checkout, register, account, branch, employee, supplier, winga, payment-provider and superadmin forms. `StoreLayout.vue` renders a floating WhatsApp button + footer "Chat on WhatsApp" link as `https://wa.me/{digits}?text={encodeURIComponent(message)}`, and the footer falls back to `contact_phone`. `AccountPage.vue` gains the owner-level WhatsApp number/message fields.
- **Business store sync**: after saving WhatsApp/contact on Store Settings, `syncBusiness()` refreshes the current business so the storefront chat links use the latest message without a reload (commit `e2ab35f`).

### 2026-08-04 — Trial lifecycle & subscription scoping
- **Auto-deactivation**: owners whose subscription is a trial and whose `subscription_expires_at` has passed are auto-deactivated (commit `a389eea`). Superadmin gains `POST /api/superadmin/owners/{id}/extend-trial` to add trial days; the frontend superadmin dashboard shows a trial-ended alert with an extend-trial action.
- **Per-owner scoping**: storefront products/categories isolated per business owner (`0b78cb6`), payment providers + ClickPesa setting scoped per owner and exposed by business slug (`5d010ad`), superadmin owner stats scoped to the owner (`9ed2197`), public `Business` record synced when superadmin updates owner branding (`9782bc2`).
- **Owner billing**: owner subscription billing UI added (`e36f660`, frontend `dfe83bd`); new-owner creation auto-creates a Business row and sends the default password.

### 2026-08-05 — Platform info & login forms
- **Public platform-info**: `GET /api/settings/platform-info` returns the superadmin name/phone/email for the directory top bar/footer (`2cfaab3`). Frontend shows it on the directory and uses the owner/employee WhatsApp on stores (`18b5ff7`).
- **Login/register forms**: card box removed, fields placed directly on the background (`5c638e3`).
- **API route count**: revised from 179 to **190** in the developer documentation (16 public, 174 authenticated; 38 owner, 23 superadmin, 4 supplier middleware). Developer docs updated with the WhatsApp resolution chain, new Store Settings page, PhoneInput component, and v2.4 revision.
