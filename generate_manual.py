#!/usr/bin/env python3
"""Generate PDF User Manuals for ERP Electronics Store (English + Swahili)."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Register fonts ──────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBd', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

# ── Colors ──────────────────────────────────────────────────────────────────
RED = HexColor('#e74c3c')
DARK = HexColor('#2c3e50')
LIGHT_GRAY = HexColor('#f5f5f5')
GRAY = HexColor('#888888')
BLUE = HexColor('#2980b9')
GREEN = HexColor('#27ae60')

# ── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kwargs):
    base = styles[parent] if parent in styles else styles['Normal']
    if 'fontName' not in kwargs:
        kwargs['fontName'] = 'DejaVu'
    return ParagraphStyle(name, parent=base, **kwargs)

sTitle = make_style('sTitle', fontSize=28, fontName='DejaVuBd', textColor=white, alignment=TA_CENTER, leading=34)
sSubtitle = make_style('sSubtitle', fontSize=14, textColor=HexColor('#dddddd'), alignment=TA_CENTER, leading=18)
sChapter = make_style('sChapter', fontSize=20, fontName='DejaVuBd', textColor=DARK, spaceAfter=8, spaceBefore=16, leading=26)
sSection = make_style('sSection', fontSize=14, fontName='DejaVuBd', textColor=RED, spaceAfter=6, spaceBefore=12, leading=18)
sBody = make_style('sBody', fontSize=10, textColor=HexColor('#333333'), alignment=TA_JUSTIFY, leading=15, spaceAfter=6)
sBold = make_style('sBold', fontSize=10, fontName='DejaVuBd', textColor=HexColor('#333333'), leading=15, spaceAfter=4)
sBullet = make_style('sBullet', fontSize=10, textColor=HexColor('#333333'), leading=14, leftIndent=20, spaceAfter=3)
sNote = make_style('sNote', fontSize=9, textColor=GRAY, leading=13, spaceAfter=4, leftIndent=10)
sTocEntry = make_style('sTocEntry', fontSize=11, textColor=DARK, leading=16, spaceAfter=4, leftIndent=10)
sTocSub = make_style('sTocSub', fontSize=10, textColor=HexColor('#555555'), leading=14, spaceAfter=3, leftIndent=25)
sFooter = make_style('sFooter', fontSize=8, textColor=GRAY, alignment=TA_CENTER)
sTableHeader = make_style('sTableHeader', fontSize=9, fontName='DejaVuBd', textColor=white, leading=12)
sTableCell = make_style('sTableCell', fontSize=9, textColor=HexColor('#333333'), leading=12)


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd'), spaceAfter=8, spaceBefore=8)

def bullet_list(items):
    return [Paragraph(f'• {item}', sBullet) for item in items]

def note(text):
    return Paragraph(f'💡 <i>{text}</i>', sNote)

def body(text):
    return Paragraph(text, sBody)

def bold(text):
    return Paragraph(text, sBold)

def section(text):
    return Paragraph(text, sSection)

def chapter(text):
    return Paragraph(text, sChapter)

def spacer(h=6):
    return Spacer(1, h)

def info_table(rows, col_widths=None):
    """rows = [[label, value], ...]"""
    if col_widths is None:
        col_widths = [140, 330]
    data = []
    for row in rows:
        data.append([
            Paragraph(f'<b>{row[0]}</b>', sTableCell),
            Paragraph(str(row[1]), sTableCell)
        ])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ]))
    return t

def steps_table(steps):
    """steps = ['Step 1 text', 'Step 2 text', ...]"""
    data = [[Paragraph('<b>#</b>', sTableHeader), Paragraph('<b>Action</b>', sTableHeader)]]
    for i, step in enumerate(steps, 1):
        data.append([
            Paragraph(str(i), sTableCell),
            Paragraph(step, sTableCell)
        ])
    t = Table(data, colWidths=[30, 440])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ]))
    return t

def cover_page(title, subtitle, version, date_str):
    """Build cover page elements."""
    elements = []
    cover_data = [['']]
    cover_table = Table(cover_data, colWidths=[480], rowHeights=[300])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(Spacer(1, 60))
    elements.append(cover_table)

    # Overlay text via another table on top
    overlay_data = [
        [Paragraph(title, sTitle)],
        [Spacer(1, 12)],
        [Paragraph(subtitle, sSubtitle)],
        [Spacer(1, 30)],
        [Paragraph(f'{version}  |  {date_str}', make_style('cv', fontSize=10, textColor=HexColor('#999999'), alignment=TA_CENTER))],
    ]
    overlay = Table(overlay_data, colWidths=[480])
    overlay.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.pop()  # remove plain cover_table
    elements.append(overlay)
    elements.append(PageBreak())
    return elements

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 20 * mm, f'Page {doc.page}')
    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
#  ENGLISH MANUAL CONTENT
# ══════════════════════════════════════════════════════════════════════════════

def build_en():
    el = []

    # ── Cover ──
    el += cover_page(
        'ERP Electronics Store',
        'User Manual',
        'Version 3.0',
        'July 2026'
    )

    # ── Table of Contents ──
    el.append(chapter('Table of Contents'))
    el.append(hr())
    toc = [
        ('1.', 'Getting Started'),
        ('2.', 'Owner Dashboard'),
        ('3.', 'Employee Management'),
        ('4.', 'Branch Management'),
        ('5.', 'Product Management'),
        ('6.', 'Payment Settings'),
        ('7.', 'Shipping Settings'),
        ('8.', 'Reports & Analytics'),
        ('9.', 'Employee Dashboard'),
        ('10.', 'Order Management'),
        ('11.', 'Customer Management'),
        ('12.', 'Support Inbox'),
        ('13.', 'Messaging (Owner & Employee Inbox)'),
        ('14.', 'Accounting System'),
        ('15.', 'Commissions, Earnings & Wingas'),
        ('16.', 'Inventory Management'),
        ('17.', 'Purchase Orders & Suppliers'),
        ('18.', 'Stock Alerts'),
        ('19.', 'Customer Shopping'),
        ('20.', 'Checkout & Payment'),
        ('21.', 'My Account (Customer)'),
        ('22.', 'Language Settings'),
        ('23.', 'Password Policy'),
        ('24.', 'Session & Security'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    # ── Chapter 1: Getting Started ──
    el.append(chapter('1. Getting Started'))
    el.append(hr())
    el.append(section('System Overview'))
    el.append(body('ERP Electronics Store is a complete point-of-sale and e-commerce system for managing your electronics retail business. It supports three user roles: <b>Owner</b> (full admin), <b>Employee</b> (operations), and <b>Customer</b> (shopping).'))
    el.append(spacer())

    el.append(section('Logging In'))
    el.append(steps_table([
        'Open the store website in your browser.',
        'Click <b>"Login"</b> in the top navigation bar.',
        'Enter your email address and password.',
        'Click <b>"Sign In"</b> to access your dashboard.',
    ]))
    el.append(spacer())
    el.append(note('If this is your first login, you may be prompted to change your password. See Chapter 23 for details.'))
    el.append(spacer())

    el.append(section('Default Login Credentials'))
    el.append(info_table([
        ['Owner', 'victorzacharia110@gmail.com'],
        ['Employee', 'mathewzacharia@gmail.com'],
        ['Customer', 'zachariakinyula@gmail.com'],
    ]))
    el.append(PageBreak())

    # ── Chapter 2: Owner Dashboard ──
    el.append(chapter('2. Owner Dashboard'))
    el.append(hr())
    el.append(body('The Owner Dashboard is your central hub. After logging in as owner, you see:'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>Summary Statistics</b> — Total Revenue, Total Orders, Total Products, and Total Employees at a glance.',
        '<b>Sales Analytics Charts</b> — Interactive bar and line charts showing Revenue vs Profit, Orders Trend, Items Sold, and Revenue by Category. Use the period selector to toggle between 6 and 12 months.',
        '<b>AI Business Insights</b> — AI-powered suggestions from Google Gemini analyzing your business data. Suggestions are categorized by priority (High/Medium/Low) and type (Inventory, Pricing, Marketing, Growth, Operations). Click "Refresh" to regenerate insights.',
        '<b>Recent Orders</b> — Quick view of the latest orders with status badges. Click "View All" to go to full Order Management.',
        '<b>Quick Actions</b> — Tiles to jump to Employees, Products, Orders, Reports, Inventory, Payment Settings, and Shipping Settings.',
        '<b>Products Overview</b> — Top products listed by name, brand, and price. Click "View All" for full product management.',
    ]))
    el.append(PageBreak())

    # ── Chapter 3: Employee Management ──
    el.append(chapter('3. Employee Management (Owner)'))
    el.append(hr())
    el.append(body('As the owner, you can manage your store employees from <b>Owner → Employees</b>. Employees help run your store — managing orders, inventory, customers, and support.'))
    el.append(spacer())
    el.append(section('Viewing Employees'))
    el.append(body('The employee list shows all registered employees with their name, email, branch, position, and status. Use the search bar to find specific employees, or click "View All" to see the full list.'))
    el.append(spacer())
    el.append(section('Adding a New Employee'))
    el.append(body('Click <b>"Add Employee"</b> and complete the registration form:'))
    el.extend(bullet_list([
        '<b>Full Name</b>, <b>Email</b>, and <b>Phone number</b> (required).',
        '<b>Identification</b> — provide either the <b>NIDA number</b> or the <b>Voting ID card number</b>.',
        '<b>Branch</b> — assign the employee to one of your branches (optional if no branches exist).',
        '<b>Position</b> and <b>Department</b> — e.g. Cashier / Sales, or Warehouse.',
        '<b>Commission Rate (%)</b> — the percentage the employee earns on sales (0–100).',
    ]))
    el.append(spacer())
    el.append(section('Wadhamini (Guarantors)'))
    el.append(body('Add at least one guarantor (Wadhamini) by clicking <b>"Fill Wadhamini Form"</b>. Enter each guarantor\'s full name, phone, relationship, and address, then click <b>"Add Guarantor"</b>. Guarantors vouch for the employee and can be edited later.'))
    el.append(spacer())
    el.append(section('Attachments'))
    el.append(body('You can attach the employee\'s <b>contract</b>, ID scans, and <b>background check</b> documents. Click <b>"Choose Files"</b>, then set the type for each file (Contract, Background Check, or Other).'))
    el.append(spacer())
    el.append(steps_table([
        'Click <b>"Create Employee"</b> to finish.',
        'The employee account is created with a <b>default password = FULL NAME IN CAPITALS</b> (e.g., "MATHEW ZACHARIA").',
        'Share these credentials with the employee securely.',
    ]))
    el.append(spacer())
    el.append(note('Employees will be prompted to change their password on first login if it has been more than 3 days since creation.'))
    el.append(spacer())
    el.append(section('Editing an Employee'))
    el.append(body('Click the <b>pencil (edit)</b> icon on an employee\'s card to open the edit form. You can update their name, email, phone, identification, branch, position, department, commission rate, and their guarantors. Click <b>"Save Changes"</b> when done.'))
    el.append(PageBreak())

    # ── Chapter 4: Branch Management ──
    el.append(chapter('4. Branch Management (Owner)'))
    el.append(hr())
    el.append(body('If your business has multiple locations, you can manage branches from <b>Owner → Branches</b>. Branches are optional — the system works without them.'))
    el.append(spacer())
    el.append(section('Viewing Branches'))
    el.extend(bullet_list([
        'All branches are displayed as cards with name, city, address, and phone.',
        'The default branch is marked with a badge.',
        'Use the search bar to find branches by name or city.',
    ]))
    el.append(spacer())
    el.append(section('Adding a Branch'))
    el.append(steps_table([
        'Navigate to <b>Owner → Branches</b>.',
        'Click <b>"Add Branch"</b>.',
        'Enter: <b>Branch Name</b>, <b>City</b>, <b>Address</b>, <b>Phone</b>.',
        'Click <b>"Save"</b>.',
    ]))
    el.append(spacer())
    el.append(section('Assigning Employees to Branches'))
    el.append(body('When creating or editing an employee, you can assign them to a branch. This links the employee to a specific location. Employees can also be reassigned at any time.'))
    el.append(spacer())
    el.append(section('Setting a Default Branch'))
    el.append(body('Click the star icon on any branch card to set it as the default. The default branch is pre-selected when creating new orders.'))
    el.append(PageBreak())

    # ── Chapter 5: Product Management ──
    el.append(chapter('5. Product Management (Owner)'))
    el.append(hr())
    el.append(body('Manage your entire product catalog from <b>Owner → Products</b>.'))
    el.append(spacer())
    el.append(section('Product List'))
    el.extend(bullet_list([
        'All products are displayed with name, brand, category, and price.',
        'Use the search bar to filter products by name or brand.',
        'Pagination shows 15 products per page by default. Click "View All" to see everything.',
    ]))
    el.append(spacer())
    el.append(section('Adding a Product'))
    el.append(steps_table([
        'Click <b>"Add Product"</b> on the products page.',
        'Fill in: <b>Name</b>, <b>Brand</b>, <b>Description</b>, <b>Category</b> (dropdown).',
        'Upload a <b>Product Image</b> (max 5MB, JPG/PNG).',
        'Add <b>Product Variants</b> — each variant needs: SKU, Color/Storage, Selling Price (TSh), Cost Price (TSh), and Stock quantity.',
        'Click <b>"Save"</b> to create the product.',
    ]))
    el.append(spacer())
    el.append(note('Cost price is used for profit calculations in analytics. Always enter accurate cost prices.'))
    el.append(spacer())
    el.append(section('Editing a Product'))
    el.append(body('Click the edit icon on any product row. Modify any field and click <b>"Save"</b>. You can also add or remove variants during editing.'))
    el.append(spacer())
    el.append(section('Deleting a Product'))
    el.append(body('Click the delete icon on any product row. Confirm the deletion when prompted. Note: Products with existing orders cannot be deleted.'))
    el.append(PageBreak())

    # ── Chapter 6: Payment Settings ──
    el.append(chapter('6. Payment Settings (Owner)'))
    el.append(hr())
    el.append(body('Configure payment methods from <b>Owner → Payment Settings</b>.'))
    el.append(spacer())
    el.append(section('ClickPesa Integration'))
    el.append(body('Toggle ClickPesa online payments on or off. When enabled, customers see ClickPesa as a payment option at checkout. When disabled, a "Coming Soon" message is shown.'))
    el.append(spacer())
    el.append(section('Mobile Money Providers'))
    el.append(body('Manage the payment numbers displayed to customers during checkout. You can:'))
    el.extend(bullet_list([
        '<b>Add</b> a new provider (e.g., M-Pesa, Airtel Money, Halopesa).',
        '<b>Edit</b> the phone number or icon class for existing providers.',
        '<b>Toggle</b> providers enabled/disabled.',
        '<b>Delete</b> a provider you no longer accept.',
    ]))
    el.append(PageBreak())

    # ── Chapter 7: Shipping Settings ──
    el.append(chapter('7. Shipping Settings (Owner)'))
    el.append(hr())
    el.append(body('Configure shipping costs from <b>Owner → Shipping</b>.'))
    el.append(spacer())
    el.append(section('Delivery Routes'))
    el.append(body('Define routes between cities (e.g., Dar es Salaam → Arusha). Each route has:'))
    el.extend(bullet_list([
        '<b>Route Name</b> — descriptive label.',
        '<b>From City</b> and <b>To City</b> — the origin and destination.',
        '<b>Base Cost</b> — minimum shipping fee in TSh.',
    ]))
    el.append(spacer())
    el.append(section('Value-Based Pricing Rules'))
    el.append(body('For each route, you can add pricing rules based on order value:'))
    el.extend(bullet_list([
        '<b>Min Value</b> and <b>Max Value</b> — order value range in TSh.',
        '<b>Shipping Cost</b> — the fee for orders in this range.',
    ]))
    el.append(note('Leave Max Value empty for "no upper limit". The system automatically calculates shipping at checkout based on these rules.'))
    el.append(PageBreak())

    # ── Chapter 8: Reports & Analytics ──
    el.append(chapter('8. Reports & Analytics (Owner)'))
    el.append(hr())
    el.append(section('Daily Reports'))
    el.append(body('Navigate to <b>Owner → Reports</b> to view daily sales reports. Reports are auto-generated at midnight each day.'))
    el.extend(bullet_list([
        'Select a date using the date picker.',
        'View: Total Orders, Total Revenue, Items Sold, Paid Orders, Pending Orders, Cancelled Orders.',
        'See Employee Performance stats and Top Products for the day.',
        'Click <b>"Print"</b> to print the report.',
    ]))
    el.append(spacer())
    el.append(section('Sales Analytics (Dashboard)'))
    el.append(body('The Owner Dashboard includes rich analytics:'))
    el.extend(bullet_list([
        '<b>Revenue vs Profit</b> — Bar chart comparing monthly revenue and profit.',
        '<b>Orders Trend</b> — Line chart of orders placed vs cancelled over time.',
        '<b>Items Sold</b> — Monthly items sold volume.',
        '<b>Revenue by Category</b> — Doughnut chart showing category distribution.',
        '<b>Summary Cards</b> — Total Revenue, Total Profit, Total Orders, Profit Margin, Revenue Growth.',
    ]))
    el.append(spacer())
    el.append(section('AI Business Insights'))
    el.append(body('The system uses Google Gemini AI to analyze your sales data and provide actionable business suggestions. Suggestions cover inventory, pricing, marketing, growth, and operations. Each suggestion is tagged with a priority level (High, Medium, Low).'))
    el.append(PageBreak())

    # ── Chapter 9: Employee Dashboard ──
    el.append(chapter('9. Employee Dashboard'))
    el.append(hr())
    el.append(body('When an employee logs in, they see their own dashboard with:'))
    el.extend(bullet_list([
        '<b>Summary Stats</b> — Pending Orders, Processing, Shipped Today, Total Products, Total Customers.',
        '<b>Alert Banners</b> — If there are orders awaiting payment confirmation or unread support messages.',
        '<b>Recent Orders</b> — Latest orders with status and amount. Click "View All" for full list.',
        '<b>Quick Actions</b> — Manage Orders, View Products, My Profile, Support Inbox.',
    ]))
    el.append(PageBreak())

    # ── Chapter 10: Order Management ──
    el.append(chapter('10. Order Management (Employee)'))
    el.append(hr())
    el.append(body('Employees manage orders from <b>Employee → Orders</b>.'))
    el.append(spacer())
    el.append(section('Viewing & Filtering Orders'))
    el.extend(bullet_list([
        'Filter by status tabs: All, Pending Payment, Pending, Inactive, Paid, Processing, Shipped, Delivered, Cancelled.',
        'Search by order number or customer name.',
        'Click "View All" to expand beyond the default 15 per page.',
    ]))
    el.append(spacer())
    el.append(section('Confirming Payments'))
    el.append(body('When a customer pays via mobile money (M-Pesa, Airtel, etc.):'))
    el.append(steps_table([
        'The order appears with status "Pending" and a confirmation panel.',
        'Verify the payment on your mobile money account.',
        'Type the customer\'s <b>full name IN CAPITAL LETTERS</b> as shown in the prompt.',
        'Click <b>"Confirm Payment"</b>.',
        'Order moves to "Paid" status and inventory is deducted.',
    ]))
    el.append(note('Cash payments and ClickPesa payments are confirmed automatically. Only mobile money payments require manual confirmation.'))
    el.append(spacer())
    el.append(section('Updating Order Status'))
    el.append(body('Use the action buttons to progress orders:'))
    el.extend(bullet_list([
        '<b>Mark Processing</b> — Order is being prepared.',
        '<b>Mark Shipped</b> — Add tracking number and delivery notes, then mark as shipped.',
        '<b>Mark Delivered</b> — Confirm successful delivery.',
        '<b>Cancel</b> — Cancel the order (restores inventory).',
    ]))
    el.append(PageBreak())

    # ── Chapter 11: Customer Management ──
    el.append(chapter('11. Customer Management (Employee)'))
    el.append(hr())
    el.append(body('Employees can manage customers from <b>Employee → Customers</b>.'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>View</b> all registered customers with name, email, and status.',
        '<b>Search</b> by name or email.',
        '<b>Add</b> new customers with name, email, and a default password (same as their full name in capitals).',
        '<b>Toggle Status</b> — Enable or disable a customer account.',
        '<b>Delete</b> a customer (only if they have no orders).',
    ]))
    el.append(PageBreak())

    # ── Chapter 12: Support Inbox ──
    el.append(chapter('12. Support Inbox (Employee)'))
    el.append(hr())
    el.append(body('Handle customer support messages from <b>Employee → Support</b>. This is the channel for customer service: customers raise issues here and employees reply. For conversations with your store owner, use <b>Employee → Inbox</b> (see Chapter 13).'))
    el.append(spacer())
    el.append(section('Viewing Messages'))
    el.extend(bullet_list([
        'Messages are listed with customer name, subject, category, and status.',
        'Filter by status: All, Open, In Progress, Resolved, Closed.',
        'Click a message to view the full conversation.',
    ]))
    el.append(spacer())
    el.append(section('Replying to Customers'))
    el.append(steps_table([
        'Open the support message.',
        'Read the customer\'s issue.',
        'Type your reply in the text box.',
        'Click <b>"Send Reply"</b>.',
        'The customer receives your response in their account.',
    ]))
    el.append(PageBreak())

    # ── Chapter 13: Messaging (Owner & Employee Inbox) ──
    el.append(chapter('13. Messaging (Owner & Employee Inbox)'))
    el.append(hr())
    el.append(body('The Inbox is the platform-wide messaging system. Conversations exist between these roles only:'))
    el.extend(bullet_list([
        '<b>Owner ↔ Superadmin</b> — Communicate with the system administrator for account issues, subscription questions, or technical support.',
        '<b>Owner ↔ Customer</b> — Customers can start conversations with you about orders, products, or general inquiries.',
        '<b>Owner ↔ Employee</b> — Staff and owners can message each other about daily operations, shift notes, or approvals.',
    ]))
    el.append(note('Customers cannot message the Superadmin directly, and Employees do not see Superadmin conversations. Customers reach the store through <b>Support</b> messages.'))
    el.append(spacer())
    el.append(section('Owner Inbox'))
    el.append(body('Open the Inbox from <b>Owner → Inbox</b>. Conversations are grouped into tabs: <b>"All"</b>, <b>"Customers"</b>, <b>"Staff"</b>, and <b>"Admin"</b>. Unread conversations show a red badge.'))
    el.append(spacer())
    el.append(body('To start a new conversation, click the <b>"+"</b> button. You can pick a customer who ordered from your store or any of your staff members.'))
    el.append(spacer())
    el.append(section('Employee Inbox'))
    el.append(body('Employees can message their store owner from <b>Employee → Inbox</b> (next to the Support inbox). The conversation list shows threads with your owner, and the <b>"+"</b> button lets you start a new conversation with your owner directly.'))
    el.append(spacer())
    el.append(section('Replying to Messages'))
    el.append(steps_table([
        'Click on a conversation to open it.',
        'Read the message history.',
        'Type your reply in the text box at the bottom.',
        'Click <b>"Send"</b>.',
    ]))
    el.append(spacer())
    el.append(note('Re-sending a message to the same person reuses the existing conversation thread instead of creating duplicates.'))
    el.append(spacer())
    el.append(section('Message Read Status (Ticks)'))
    el.append(body('Messages you send show a WhatsApp-style read indicator next to the time stamp. A <b>grey double tick</b> means your message was delivered; it turns <b>blue</b> when the other person opens the conversation and reads it. The status refreshes automatically every few seconds while the Inbox is open.'))
    el.append(spacer())
    el.append(section('Deleting Conversations and Messages'))
    el.extend(bullet_list([
        '<b>Delete a message</b> — hover over one of your own sent messages and click the trash icon that appears. Confirm the deletion; only your own messages can be removed.',
        '<b>Delete a conversation</b> — click the trash icon at the top of an open conversation. Confirm to remove the whole chat thread for both sides.',
    ]))
    el.append(note('Deleting a conversation removes the entire thread. Deleting a single message removes just that message from the thread; the rest of the conversation stays intact.'))
    el.append(PageBreak())

    # ── Chapter 14: Accounting System ──
    el.append(chapter('14. Accounting System'))
    el.append(hr())
    el.append(body('The Accounting System provides full double-entry bookkeeping for your business. Access it from <b>Owner → Accounting</b>.'))
    el.append(spacer())
    el.append(section('Chart of Accounts'))
    el.append(body('The system comes with 22 pre-configured default accounts organized into five categories:'))
    el.extend(bullet_list([
        '<b>Assets (5 accounts)</b> — Cash, Bank Account, Accounts Receivable, Inventory, Fixed Assets.',
        '<b>Liabilities (4 accounts)</b> — Accounts Payable, Loans Payable, Tax Payable, Accrued Expenses.',
        '<b>Equity (4 accounts)</b> — Owner\'s Equity, Retained Earnings, Capital, Drawings.',
        '<b>Revenue (4 accounts)</b> — Sales Revenue, Service Revenue, Other Income, Discount Allowed.',
        '<b>Expenses (5 accounts)</b> — Cost of Goods Sold, Rent, Salaries, Utilities, Office Supplies.',
    ]))
    el.append(spacer())
    el.append(body('Manage the chart of accounts at <b>/owner/accounting/chart-of-accounts</b>. You can:'))
    el.extend(bullet_list([
        '<b>Add</b> new accounts with code, name, type, and optional description.',
        '<b>Edit</b> existing account details.',
        '<b>Delete</b> accounts that have no transactions.',
    ]))
    el.append(spacer())
    el.append(section('Journal Entries'))
    el.append(body('Every financial transaction is recorded as a journal entry with a unique reference number in the format <b>JE-YYYYMMDD-XXX</b>.'))
    el.append(spacer())
    el.append(body('Journal entries are automatically created for:'))
    el.extend(bullet_list([
        '<b>Order Payment</b> — Debits Cash/Bank, Credits Sales Revenue (and Cost of Goods Sold for inventory).',
        '<b>Order Cancellation</b> — Reverses the original payment entry.',
        '<b>Purchase Order Receive</b> — Debits Inventory, Credits Accounts Payable.',
    ]))
    el.append(spacer())
    el.append(body('You can also create <b>manual journal entries</b> for adjustments, corrections, or any other financial transaction. Each entry requires at least two line items (debit and credit) that must balance.'))
    el.append(spacer())
    el.append(body('Journal entries follow a three-stage status workflow:'))
    el.extend(bullet_list([
        '<b>Draft</b> — Entry is saved but not yet posted to the ledger. Can be edited or deleted.',
        '<b>Posted</b> — Entry is finalized and reflected in financial reports. Cannot be edited.',
        '<b>Voided</b> — Entry is cancelled. The original entry remains in the system for audit purposes, but its financial effect is reversed.',
    ]))
    el.append(spacer())
    el.append(section('Financial Reports'))
    el.append(body('Generate financial reports from <b>/owner/accounting</b>:'))
    el.extend(bullet_list([
        '<b>Trial Balance</b> — Lists all accounts with their debit or credit balances. Used to verify that total debits equal total credits.',
        '<b>Profit & Loss</b> — Shows revenue minus expenses over a period. Displays net profit or loss.',
        '<b>Balance Sheet</b> — A snapshot of assets, liabilities, and equity at a point in time. Must balance (Assets = Liabilities + Equity).',
        '<b>General Ledger</b> — Detailed view of all transactions for any account. Filter by account and date range.',
    ]))
    el.append(PageBreak())

    # ── Chapter 15: Commissions & Earnings ──
    el.append(chapter('15. Commissions & Earnings'))
    el.append(hr())
    el.append(section('Commission System'))
    el.append(body('The commission system rewards employees based on the <b>profit</b> they generate, not just revenue. Each employee has a commission rate set by the owner.'))
    el.append(spacer())
    el.append(body('How commissions work:'))
    el.extend(bullet_list([
        'When an order is marked as <b>Paid</b>, the system calculates profit (Selling Price - Cost Price) for each item.',
        'Commission = Total Profit × Employee Commission Rate (e.g., 5% of TSh 200,000 profit = TSh 10,000).',
        'If the order has zero or negative profit, no commission is generated.',
        'Commissions are tracked per-employee and accumulated until paid out.',
    ]))
    el.append(spacer())
    el.append(body('The owner can manage commissions from <b>Owner → Commissions</b>:'))
    el.extend(bullet_list([
        '<b>View</b> pending commissions for each employee with profit details.',
        '<b>Pay Out</b> individual commissions to mark them as paid.',
        '<b>Pay All</b> to settle all pending commissions at once.',
    ]))
    el.append(spacer())
    el.append(section('Employee Earnings'))
    el.append(body('Employees can view their own earnings at <b>/employee/earnings</b>. The earnings dashboard displays:'))
    el.extend(bullet_list([
        '<b>Total Profit Generated</b> — Total profit from all orders handled by this employee.',
        '<b>Total Orders</b> — Number of orders with commissions.',
        '<b>Pending Commission</b> — Commission amount awaiting payout.',
        '<b>Paid Commission</b> — Total amount that has been paid to the employee.',
    ]))
    el.append(note('Commissions are purely profit-based with no base salary. This incentivizes employees to focus on selling higher-margin products.'))
    el.append(spacer())
    el.append(section('Winga (Street Promoters)'))
    el.append(body('A <b>Winga</b> is a street promoter who brings customers into your shop. You can register wingas for your business (optionally per branch) and pay them a commission for the customers they bring. Wingas are managed from <b>Owner → Wingas</b>; employees can also view and manage them.'))
    el.append(spacer())
    el.append(section('How Winga Commissions Work'))
    el.append(body('When an order is placed with a winga attached, the winga\'s commission rate is added as a <b>percentage increase on the product price</b>. This "winga fee" is included in the customer\'s total and funds the winga\'s commission. For example, a 10% winga rate on a TSh 100,000 order adds TSh 10,000 to the total, which becomes the winga\'s commission.'))
    el.append(spacer())
    el.append(body('Registering a winga:'))
    el.extend(bullet_list([
        'Navigate to <b>Owner → Wingas</b> and click <b>"Add Winga"</b>.',
        'Enter the <b>name</b> and <b>phone number</b>.',
        'Enter the winga\'s <b>TIN number</b> (TRA Taxpayer Identification Number) and <b>NIDA number</b> for tax compliance.',
        'Set the <b>commission rate (%)</b> — the percentage added to the sale.',
        'Optionally assign the winga to a <b>branch</b>.',
        'Click <b>"Save"</b>.',
    ]))
    el.append(spacer())
    el.append(section('Withholding Tax (TDS)'))
    el.append(body('Tanzania requires a <b>5% withholding tax (TDS)</b> to be deducted from commission payments. When you pay a winga, the system automatically deducts 5% from the gross commission and records it as <b>Withholding Tax Payable</b> to be remitted to TRA.'))
    el.append(spacer())
    el.append(body('Example: A winga with a TSh 10,000 commission receives <b>TSh 9,500</b>, and <b>TSh 500</b> is withheld for TRA. The journal entries are posted automatically (debit Winga Commission Payable, credit Cash and Withholding Tax Payable).'))
    el.append(spacer())
    el.append(section('Paying Winga Commissions'))
    el.append(body('From the winga commissions view, you can:'))
    el.extend(bullet_list([
        '<b>View</b> pending commissions per winga with gross, tax (TDS), and net amounts.',
        '<b>Pay</b> a single commission — the net amount is paid out and the withholding tax is recorded.',
        '<b>Pay All</b> — settle every pending commission in one action.',
    ]))
    el.append(spacer())
    el.append(note('Commissions are created automatically when an order with a winga is marked as paid. Cancelling an order or returning items reverses the commission proportionally.'))
    el.append(PageBreak())

    # ── Chapter 16: Inventory Management ──
    el.append(chapter('16. Inventory Management'))
    el.append(hr())
    el.append(body('Track and manage your stock levels from <b>Owner → Inventory</b>.'))
    el.append(spacer())
    el.append(section('Stock Dashboard'))
    el.append(body('The inventory dashboard gives you an at-a-glance overview of your stock:'))
    el.extend(bullet_list([
        '<b>Total Variants</b> — The total number of product variants in your catalog.',
        '<b>Low Stock Count</b> — Number of variants where stock is at or below the reorder level.',
        '<b>Total Stock Value</b> — Combined value of all inventory based on cost prices.',
        '<b>Out of Stock Count</b> — Number of variants with zero stock.',
    ]))
    el.append(spacer())
    el.append(section('Stock Adjustments'))
    el.append(body('Make manual stock adjustments via the adjustment modal:'))
    el.append(steps_table([
        'Click <b>"Adjust Stock"</b> on the inventory page.',
        'Select the <b>product variant</b> to adjust.',
        'Choose the <b>adjustment type</b>:',
        '    — <b>Adjustment</b>: General correction to stock levels.',
        '    — <b>Damage</b>: Record damaged or spoiled goods.',
        '    — <b>Opening</b>: Initial stock entry for new products.',
        'Enter the <b>quantity</b> (positive to add, negative to reduce).',
        'Add <b>notes</b> explaining the reason for adjustment.',
        'Click <b>"Save"</b> to record the adjustment.',
    ]))
    el.append(spacer())
    el.append(section('Transaction History'))
    el.append(body('Every stock change is logged in the transaction history. Each entry shows:'))
    el.extend(bullet_list([
        '<b>Type</b> — The reason for the stock change (Sale, Cancellation, Adjustment, Damage, Opening, Purchase Order, etc.).',
        '<b>Product</b> — The variant that was affected.',
        '<b>Quantity</b> — The amount added (+) or removed (-).',
        '<b>Running Balance</b> — The stock level after this transaction.',
    ]))
    el.append(note('Stock is automatically deducted when orders are paid and restored when orders are cancelled. Purchase order receiving also adds stock automatically.'))
    el.append(PageBreak())

    # ── Chapter 17: Purchase Orders & Suppliers ──
    el.append(chapter('17. Purchase Orders & Suppliers'))
    el.append(hr())
    el.append(section('Suppliers'))
    el.append(body('Manage your suppliers from <b>Owner → Suppliers</b>. Each supplier record includes:'))
    el.extend(bullet_list([
        '<b>Supplier Name</b> — Company or individual name.',
        '<b>Contact Person</b> — Primary contact at the supplier.',
        '<b>Email</b> — Supplier email address.',
        '<b>Phone</b> — Supplier phone number.',
        '<b>Address</b> — Physical address.',
    ]))
    el.append(spacer())
    el.append(body('You can add, edit, and delete suppliers. Use the search bar to find suppliers by any field (name, contact, email, phone, or address).'))
    el.append(spacer())
    el.append(section('Purchase Orders'))
    el.append(body('Create and manage purchase orders from <b>Owner → Purchase Orders</b> to restock inventory from suppliers.'))
    el.append(spacer())
    el.append(body('Creating a Purchase Order:'))
    el.append(steps_table([
        'Click <b>"Create Purchase Order"</b>.',
        'Select a <b>supplier</b> from the dropdown.',
        'Add <b>line items</b> — for each item, select a product variant, enter quantity and unit cost.',
        'Review the total cost.',
        'Click <b>"Save"</b> to create the PO in Draft status.',
    ]))
    el.append(spacer())
    el.append(body('Purchase Order status flow:'))
    el.extend(bullet_list([
        '<b>Draft</b> — PO is created but not yet sent to the supplier. Can be edited.',
        '<b>Ordered</b> — PO has been sent to the supplier. Awaiting delivery.',
        '<b>Received</b> — Goods have been received. Inventory is automatically updated and journal entries are created (debit Inventory, credit Accounts Payable).',
    ]))
    el.append(spacer())
    el.append(section('Supplier Portal'))
    el.append(body('Suppliers have their own login portal to view purchase orders addressed to them. From the supplier portal, suppliers can:'))
    el.extend(bullet_list([
        '<b>View</b> all their purchase orders and current status.',
        '<b>Update Status</b> — Mark orders as dispatched or delivered.',
        '<b>View Details</b> — See line items, quantities, and costs.',
    ]))
    el.append(note('The supplier portal streamlines communication between your business and suppliers, reducing the need for phone calls or emails to track orders.'))
    el.append(PageBreak())

    # ── Chapter 18: Stock Alerts ──
    el.append(chapter('18. Stock Alerts'))
    el.append(hr())
    el.append(section('Low Stock Detection'))
    el.append(body('The system automatically monitors inventory levels and creates stock alerts when thresholds are breached. Alerts are generated based on the <b>reorder level</b> set for each product variant.'))
    el.append(spacer())
    el.append(body('Two types of alerts are created:'))
    el.extend(bullet_list([
        '<b>Low Stock</b> — Created when a variant\'s quantity is at or below its reorder level but still above zero. Indicates that stock needs to be replenished soon.',
        '<b>Out of Stock</b> — Created when a variant\'s quantity reaches zero. Indicates an urgent need to restock.',
    ]))
    el.append(spacer())
    el.append(body('Alerts are checked and created automatically whenever inventory changes (e.g., when an order is paid, a stock adjustment is made, or a purchase order is received).'))
    el.append(spacer())
    el.append(section('Managing Alerts'))
    el.append(body('View and manage stock alerts from <b>Owner → Stock Alerts</b>.'))
    el.append(spacer())
    el.append(body('Filter alerts by status:'))
    el.extend(bullet_list([
        '<b>All</b> — Shows all alerts regardless of status.',
        '<b>Active</b> — Shows only unresolved alerts that need attention.',
        '<b>Acknowledged</b> — Alerts that have been seen but not yet resolved.',
        '<b>Resolved</b> — Alerts that have been addressed (stock replenished).',
    ]))
    el.append(spacer())
    el.append(body('Available actions on alerts:'))
    el.extend(bullet_list([
        '<b>Acknowledge</b> — Mark an alert as seen. This moves it from Active to Acknowledged status, indicating you are aware of the issue.',
        '<b>Resolve</b> — Mark an alert as resolved. This should be done after the stock has been replenished or the issue has been addressed.',
    ]))
    el.append(note('Setting appropriate reorder levels for each product variant ensures you receive timely low stock alerts before running out of popular items.'))
    el.append(PageBreak())

    # ── Chapter 19: Customer Shopping ──
    el.append(chapter('19. Customer Shopping Experience'))
    el.append(hr())
    el.append(body('Customers can browse and buy products from the storefront.'))
    el.append(spacer())
    el.append(section('Browsing Products'))
    el.extend(bullet_list([
        'The home page shows featured products and categories.',
        'Use the <b>category navigation</b> to filter by type.',
        'Click any product to see its full details, variants, and pricing.',
    ]))
    el.append(spacer())
    el.append(section('Adding to Cart'))
    el.append(steps_table([
        'Select a product variant (color/storage) if applicable.',
        'Choose the quantity.',
        'Click <b>"Add to Cart"</b>.',
        'The cart icon in the header updates with the item count.',
    ]))
    el.append(PageBreak())

    # ── Chapter 20: Checkout & Payment ──
    el.append(chapter('20. Checkout & Payment'))
    el.append(hr())
    el.append(steps_table([
        'Click the <b>Cart</b> icon and review your items.',
        'Click <b>"Proceed to Checkout"</b>.',
        'Select or add a <b>delivery address</b>.',
        'Choose <b>delivery option</b>: Pickup (free) or Home Delivery (shipping fee calculated automatically based on your city).',
        'Select a <b>payment method</b>: Cash, M-Pesa, Airtel Money, Mixx by Yas, or Halopesa.',
        'If paying via mobile money, enter your phone number.',
        'Click <b>"Place Order"</b>.',
        'For <b>Cash</b>: Your order is confirmed immediately. Collect at the shop.',
        'For <b>Mobile Money</b>: Send payment to the displayed number. Your order will be confirmed by staff.',
    ]))
    el.append(PageBreak())

    # ── Chapter 21: My Account ──
    el.append(chapter('21. My Account (Customer)'))
    el.append(hr())
    el.append(body('Customers can manage their account from <b>My Account</b>.'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>Dashboard</b> — See order stats: Total Orders, In Progress, Delivered.',
        '<b>Order History</b> — View all past orders with status and details.',
        '<b>Support</b> — Send messages about payment issues, order status, delivery, or refund requests. View replies from staff.',
        '<b>Inbox</b> — Chat with the store owner about your orders. You can delete one of your own sent messages (trash icon on the message) or the entire conversation (trash icon at the top of the chat).',
        '<b>Profile</b> — Update name and personal information.',
        '<b>Password</b> — Change your password (must meet security requirements).',
        '<b>Addresses</b> — Manage saved delivery addresses.',
    ]))
    el.append(PageBreak())

    # ── Chapter 22: Language Settings ──
    el.append(chapter('22. Language Settings'))
    el.append(hr())
    el.append(body('The system supports two languages: <b>English</b> and <b>Kiswahili</b>.'))
    el.append(spacer())
    el.append(steps_table([
        'Click the language toggle in the top navigation bar.',
        'Select <b>English</b> or <b>Kiswahili</b>.',
        'The entire interface switches instantly — no page reload needed.',
    ]))
    el.append(note('Your language preference is saved and persists across sessions.'))
    el.append(PageBreak())

    # ── Chapter 23: Password Policy ──
    el.append(chapter('23. Password Policy'))
    el.append(hr())
    el.append(body('All passwords must meet the following requirements:'))
    el.append(spacer())
    el.extend(bullet_list([
        'At least <b>8 characters</b> long.',
        'At least one <b>uppercase letter</b> (A-Z).',
        'At least one <b>lowercase letter</b> (a-z).',
        'At least one <b>number</b> (0-9).',
        'At least one <b>special character</b> (!@#$%...).',
    ]))
    el.append(spacer())
    el.append(section('Forced Password Change'))
    el.append(body('If your password has never been changed or was last changed more than 3 days ago, a mandatory password change modal will appear on login. You must set a new password before accessing the system.'))
    el.append(spacer())
    el.append(section('Employee Default Password'))
    el.append(body('When the owner creates a new employee account, the default password is the employee\'s <b>full name in capital letters</b> (e.g., "MATHEW ZACHARIA"). Employees should change this immediately on first login.'))
    el.append(spacer())
    el.append(section('Owner Default Password'))
    el.append(body('When a new owner account is created by the system administrator, the default password is the owner\'s <b>full name in capital letters</b> (e.g., "JOHN DOE"). The administrator shares this password securely with the owner.'))
    el.append(PageBreak())

    # ── Chapter 24: Session & Security ──
    el.append(chapter('24. Session & Security'))
    el.append(hr())
    el.append(section('Automatic Logout (Inactivity)'))
    el.append(body('For your security, the system automatically signs you out after <b>15 minutes of inactivity</b>. Moving the mouse, clicking, or typing resets the timer.'))
    el.append(spacer())
    el.append(body('When you have been inactive for 14 minutes, a warning appears with a <b>60-second countdown</b>. Any mouse or keyboard activity dismisses the warning and keeps you signed in. When the countdown reaches zero, you are signed out and returned to the login page.'))
    el.append(spacer())
    el.append(section('Leaving the Dashboard'))
    el.append(body('If you switch to another tab or application, the timer pauses. When you return within <b>10 minutes</b>, your session continues. If you are away for <b>longer than 10 minutes</b>, the system signs you out to protect your account.'))
    el.append(spacer())
    el.append(section('Login Security'))
    el.append(body('To protect your account against unauthorized access:'))
    el.extend(bullet_list([
        'Login attempts are limited to <b>5 per minute</b> per IP address.',
        'After <b>5 failed attempts</b>, the account locks automatically for <b>30 minutes</b>.',
        'New account registrations are limited to <b>3 per minute</b> and <b>10 per day</b> per IP address.',
    ]))
    el.append(spacer())
    el.append(note('If your account becomes locked, wait 30 minutes and try again, or contact your system administrator for assistance.'))
    el.append(spacer())
    el.append(spacer())
    el.append(hr())
    el.append(Paragraph('<b>ERP Electronics Store</b> — User Manual v3.0 — July 2026', sFooter))
    el.append(Paragraph('For technical support, contact your system administrator.', sFooter))

    return el


# ══════════════════════════════════════════════════════════════════════════════
#  SWAHILI MANUAL CONTENT
# ══════════════════════════════════════════════════════════════════════════════

def build_sw():
    el = []

    # ── Cover ──
    el += cover_page(
        'Duka la Elektroniki ERP',
        'Manual ya Mtumiaji',
        'Toleo 3.0',
        'Julai 2026'
    )

    # ── Yaliyomo ──
    el.append(chapter('Yaliyomo'))
    el.append(hr())
    toc = [
        ('1.', 'Kuanza'),
        ('2.', 'Dashibodi ya Mmiliki'),
        ('3.', 'Usimamizi wa Wafanyakazi'),
        ('4.', 'Usimamizi wa Matawi'),
        ('5.', 'Usimamizi wa Bidhaa'),
        ('6.', 'Mipangilio ya Malipo'),
        ('7.', 'Mipangilio ya Usafirishaji'),
        ('8.', 'Ripoti na Uchambuzi'),
        ('9.', 'Dashibodi ya Mfanyakazi'),
        ('10.', 'Usimamizi wa Oda'),
        ('11.', 'Usimamizi wa Wateja'),
        ('12.', 'Kikasha cha Msaada'),
        ('13.', 'Kikasha cha Mmiliki (Mazungumzo)'),
        ('14.', 'Mfumo wa Uhasibu'),
        ('15.', 'Kamisheni, Mapato na Winga'),
        ('16.', 'Usimamizi wa Hifadhi'),
        ('17.', 'Oda za Ununuzi na Wachuuzi'),
        ('18.', 'Tahadhari za Hisa'),
        ('19.', 'Ununuzi kwa Mteja'),
        ('20.', 'Malipo na Uthibitishaji'),
        ('21.', 'Akaunti Yangu (Mteja)'),
        ('22.', 'Mipangilio ya Lugha'),
        ('23.', 'Sera ya Nenosiri'),
        ('24.', 'Kipindi na Usalama'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    # ── Sura ya 1: Kuanza ──
    el.append(chapter('1. Kuanza'))
    el.append(hr())
    el.append(section('Muhtasari wa Mfumo'))
    el.append(body('ERP Duka la Elektroniki ni mfumo kamili wa kuuza na biashara ya mtandaoni kwa kusimamia biashara yako ya vifaa vya elektroniki. Inasaidia mitindo mitatu ya watumiaji: <b>Mmiliki</b> (usimamizi kamili), <b>Mfanyakazi</b> (uendeshaji), na <b>Mteja</b> (ununuzi).'))
    el.append(spacer())

    el.append(section('Kuingia'))
    el.append(steps_table([
        'Fungua tovuti ya duka kwenye kivinjari chako.',
        'Bofya <b>"Ingia"</b> kwenye upau wa urambazaji wa juu.',
        'Weka anwani yako ya barua pepe na nenosiri.',
        'Bofya <b>"Ingia"</b> ili kufikia dashibodi yako.',
    ]))
    el.append(spacer())
    el.append(note('Ikiwa hii ni mara ya kwanza ya kuingia, mtapokea ombi la kubadilisha nenosiri. Sura ya 23 inaeleza zaidi.'))
    el.append(spacer())

    el.append(section('Taarifa za Kuingia Chaguo-msingi'))
    el.append(info_table([
        ['Mmiliki', 'victorzacharia110@gmail.com'],
        ['Mfanyakazi', 'mathewzacharia@gmail.com'],
        ['Mteja', 'zachariakinyula@gmail.com'],
    ]))
    el.append(PageBreak())

    # ── Sura ya 2: Dashibodi ya Mmiliki ──
    el.append(chapter('2. Dashibodi ya Mmiliki'))
    el.append(hr())
    el.append(body('Dashibodi ya Mmiliki ni kituo chako kikuu. Baada ya kuingia kama mmiliki, unaona:'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>Takwimu za Muhtasari</b> — Mapato Jumla, Oda Jumla, Bidhaa Jumla, na Wafanyakazi Jumla kwa macho.',
        '<b>Chati za Uchambuzi wa Mauzo</b> — Chati za bar na mstari zinaonyesha Mapato dhidi ya Faida, Mwenendo wa Oda, Bidhaa Zilizouzwa, na Mapato kwa Kategoria. Tumia kichaguzi cha kipindi kubadilisha kati ya miezi 6 na 12.',
        '<b>Maarifa ya Biashara ya AI</b> — Mapendekezo ya AI kutoka Google Gemini yanayochambua data ya biashara yako. Mapendekezo yamegawanywa kwa kipaumbele (Juu/Wastani/Chini) na aina (Hifadhi, Bei, Matangazo, Ukuaji, Uendeshaji). Bofya "Sahihisha" ili kujenga upya.',
        '<b>Oda za Hivi Karibuni</b> — Mtazamo wa haraka wa oda za mwisho kwa vigezo vya hali. Bofya "Angalia Zote" kwenda kwenye Usimamizi kamili wa Oda.',
        '<b>Hatua za Haraka</b> — Tiles za kufikia Wafanyakazi, Bidhaa, Oda, Ripoti, Hifadhi, Mipangilio ya Malipo, na Mipangilio ya Usafirishaji.',
        '<b>Muhtasari wa Bidhaa</b> — Bidhaa bora kwa jina, chapa, na bei. Bofya "Angalia Zote" kwa usimamizi kamili.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 3: Usimamizi wa Wafanyakazi ──
    el.append(chapter('3. Usimamizi wa Wafanyakazi (Mmiliki)'))
    el.append(hr())
    el.append(body('Kama mmiliki, unaweza kusimamia wafanyakazi wako kutoka <b>Mmiliki → Wafanyakazi</b>. Wafanyakazi husaidia kuendesha duka lako — kusimamia oda, hifadhi, wateja, na msaada.'))
    el.append(spacer())
    el.append(section('Kuona Wafanyakazi'))
    el.append(body('Orodha ya wafanyakazi inaonyesha wafanyakazi wote waliojisajili kwa majina, barua pepe, tawi, cheo, na hali. Tumia upau wa utafutaji kupata wafanyakazi maalum, au bofya "Angalia Zote" kuona orodha kamili.'))
    el.append(spacer())
    el.append(section('Kuongeza Mfanyakazi Mpya'))
    el.append(body('Bofya <b>"Ongeza Mfanyakazi"</b> na ukamilishe fomu ya usajili:'))
    el.extend(bullet_list([
        '<b>Jina Kamili</b>, <b>Barua Pepe</b> na <b>Nambari ya Simu</b> (lazima).',
        '<b>Utambulisho</b> — toa aidha <b>nambari ya NIDA</b> au <b>nambari ya kitambulisho cha mpiga kura</b>.',
        '<b>Tawi</b> — mpe mfanyakazi moja ya matawi yako (hiari ikiwa hakuna matawi).',
        '<b>Cheo</b> na <b>Idara</b> — mfano Mhazini / Mauzo, au Ghala.',
        '<b>Kiwango cha Kamisheni (%)</b> — asilimia anayopata mfanyakazi kwenye mauzo (0–100).',
    ]))
    el.append(spacer())
    el.append(section('Wadhamini'))
    el.append(body('Ongeza angalau mdhamini mmoja (Wadhamini) kwa kubofya <b>"Jaza Fomu ya Wadhamini"</b>. Weka jina kamili, simu, uhusiano, na anwani ya kila mdhamini, kisha bofya <b>"Ongeza Mdhamini"</b>. Wadhamini humthibitishia mfanyakazi na wanaweza kuhaririwa baadaye.'))
    el.append(spacer())
    el.append(section('Viambatisho'))
    el.append(body('Unaweza kuambatanisha <b>mkataba</b> wa mfanyakazi, skani za kitambulisho, na nyaraka za <b>uchunguzi wa msingi</b>. Bofya <b>"Chagua Faili"</b>, kisha weka aina ya kila faili (Mkataba, Uchunguzi wa Msingi, au Nyingine).'))
    el.append(spacer())
    el.append(steps_table([
        'Bofya <b>"Unda Mfanyakazi"</b> kumaliza.',
        'Akaunti ya mfanyakazi inaundwa na <b>nenosiri chaguo-msingi = JINA KAMILI KWA HERUFI KUBWA</b> (mfano, "MATHEW ZACHARIA").',
        'Shiriki sifa hizi na mfanyakazi kwa usalama.',
    ]))
    el.append(spacer())
    el.append(note('Wafanyakazi wataombwa kubadilisha nenosiri lao mara ya kwanza ya kuingia ikiwa zimepita zaidi ya siku 3 tangu kuundwa.'))
    el.append(spacer())
    el.append(section('Kuhariri Mfanyakazi'))
    el.append(body('Bofya ikoni ya <b>kalamu (hariri)</b> kwenye kadi ya mfanyakazi kufungua fomu ya kuhariri. Unaweza kusahihisha jina, barua pepe, simu, utambulisho, tawi, cheo, idara, kiwango cha kamisheni, na wadhamini wake. Bofya <b>"Hifadhi Mabadiliko"</b> umalize.'))
    el.append(PageBreak())

    # ── Sura ya 4: Usimamizi wa Matawi ──
    el.append(chapter('4. Usimamizi wa Matawi (Mmiliki)'))
    el.append(hr())
    el.append(body('Ikiwa biashara yako na maeneo mengi, unaweza kusimamia matawi kutoka <b>Mmiliki → Matawi</b>. Matawi si lazima — mfumo unafanya kazi bila yao.'))
    el.append(spacer())
    el.append(section('Kuona Matawi'))
    el.extend(bullet_list([
        'Matawi yote yanaonyeshwa kama kadi kwa jina, jiji, anwani, na simu.',
        'Tawi la msingi linaonyeshwa na beji.',
        'Tumia upau wa utafutaji kupata matawi kwa jina au jiji.',
    ]))
    el.append(spacer())
    el.append(section('Kuongeza Tawi'))
    el.append(steps_table([
        'Nenda kwenye <b>Mmiliki → Matawi</b>.',
        'Bofya <b>"Ongeza Tawi"</b>.',
        'Weka: <b>Jina la Tawi</b>, <b>Jiji</b>, <b>Anwani</b>, <b>Simu</b>.',
        'Bofya <b>"Hifadhi"</b>.',
    ]))
    el.append(spacer())
    el.append(section('Kuunganisha Wafanyakazi na Matawi'))
    el.append(body('Unapounda au kuhariri mfanyakazi, unaweza kumuunganisha na tawi. Hii inamuunganisha mfanyakazi na eneo maalum. Wafanyakazi wanaweza pia kubadilishwa wakati wowote.'))
    el.append(PageBreak())

    # ── Sura ya 5: Usimamizi wa Bidhaa ──
    el.append(chapter('5. Usimamizi wa Bidhaa (Mmiliki)'))
    el.append(hr())
    el.append(body('Simamia katalogi yako yote ya bidhaa kutoka <b>Mmiliki → Bidhaa</b>.'))
    el.append(spacer())
    el.append(section('Orodha ya Bidhaa'))
    el.extend(bullet_list([
        'Bidhaa zote zinaonyeshwa kwa jina, chapa, kategoria, na bei.',
        'Tumia upau wa utafutaji kuchuja bidhaa kwa jina au chapa.',
        'Ugawaji wa kurasa unaonyesha bidhaa 15 kwa ukurasa. Bofya "Angalia Zote" kuona kila kitu.',
    ]))
    el.append(spacer())
    el.append(section('Kuongeza Bidhaa'))
    el.append(steps_table([
        'Bofya <b>"Ongeza Bidhaa"</b> kwenye ukurasa wa bidhaa.',
        'Jaza: <b>Jina</b>, <b>Chapa</b>, <b>Maelezo</b>, <b>Kategoria</b> (kunja chini).',
        'Pakia <b>Picha ya Bidhaa</b> (max 5MB, JPG/PNG).',
        'Ongeza <b>Aina za Bidhaa</b> — kila aina inahitaji: SKU, Rangi/uhifadhi, Bei ya Kuuza (TSh), Bei ya Gharama (TSh), na Kiasi cha Hisa.',
        'Bofya <b>"Hifadhi"</b> ili kuunda bidhaa.',
    ]))
    el.append(spacer())
    el.append(note('Bei ya gharama inatumika kwa hesabu ya faida katika uchambuzi. Weka bei sahihi za gharama daima.'))
    el.append(spacer())
    el.append(section('Kuhariri Bidhaa'))
    el.append(body('Bofya ikoni ya kuhariri kwenye safu yoyote ya bidhaa. Badilisha sehemu yoyote na bofya <b>"Hifadhi"</b>. Unaweza pia kuongeza au kuondoa aina wakati wa kuhariri.'))
    el.append(spacer())
    el.append(section('Kufuta Bidhaa'))
    el.append(body('Bofya ikoni ya kufuta kwenye safu yoyote ya bidhaa. Thibitisha ufungaji uliokizwa. Tahadhari: Bidhaa zenye oda zilizopo hazifutwi.'))
    el.append(PageBreak())

    # ── Sura ya 6: Mipangilio ya Malipo ──
    el.append(chapter('6. Mipangilio ya Malipo (Mmiliki)'))
    el.append(hr())
    el.append(body('Sanidi njia za malipo kutoka <b>Mmiliki → Mipangilio ya Malipo</b>.'))
    el.append(spacer())
    el.append(section('Uunganisho wa ClickPesa'))
    el.append(body('Washa au zima malipo ya mtandaoni ya ClickPesa. Ikishawashwa, wateja wanaona ClickPesa kama chaguo la malipo wakati wa kulipia. Ikiwa imezimwa, ujumbe wa "Inakuja Hivi Karibuni" unaonyeshwa.'))
    el.append(spacer())
    el.append(section('Watoa Huduma wa Pesa za Simu'))
    el.append(body('Simamia nambari za malipo zinazoonyeshwa kwa wateja wakati wa kulipia. Unaweza:'))
    el.extend(bullet_list([
        '<b>Ongeza</b> mtoa huduma mpya (mfano, M-Pesa, Airtel Money, Halopesa).',
        '<b>Sahihisha</b> nambari ya simu au aina ya icon ya yaliyopo.',
        '<b>Washa/Zima</b> watoa huduma.',
        '<b>Futa</b> mtoa huduma ambaye huna tena.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 7: Mipangilio ya Usafirishaji ──
    el.append(chapter('7. Mipangilio ya Usafirishaji (Mmiliki)'))
    el.append(hr())
    el.append(body('Sanidi ada za usafirishaji kutoka <b>Mmiliki → Usafirishaji</b>.'))
    el.append(spacer())
    el.append(section('Njia za Usafirishaji'))
    el.append(body('Faini njia kati ya miji (mfano, Dar es Salaam → Arusha). Kila njia ina:'))
    el.extend(bullet_list([
        '<b>Jina la Njia</b> — lebo inayoelezea.',
        '<b>Jiji la Kutoka</b> na <b>Jiji la Kufika</b> — chanzo na lengo.',
        '<b>Ada ya Msingi</b> — ada ya chini ya usafirishaji kwa TSh.',
    ]))
    el.append(spacer())
    el.append(section('Sheria za Bei Kulingana na Thamani'))
    el.append(body('Kwa kila njia, unaweza kuongeza sheria za bei kulingana na thamani ya oda:'))
    el.extend(bullet_list([
        '<b>Thamani ya Chini</b> na <b>Thamani ya Juu</b> — masafa ya thamani ya oda kwa TSh.',
        '<b>Ada ya Usafirishaji</b> — ada kwa oda katika masafa haya.',
    ]))
    el.append(note('Acha Thamani ya Juu tupu kwa "hakuna kikomo". Mfumo unakokotoa ada ya usafirishaji kiotomatiki kulingana na sheria hizi.'))
    el.append(PageBreak())

    # ── Sura ya 8: Ripoti na Uchambuzi ──
    el.append(chapter('8. Ripoti na Uchambuzi (Mmiliki)'))
    el.append(hr())
    el.append(section('Ripoti za Kila Siku'))
    el.append(body('Nenda kwenye <b>Mmiliki → Ripoti</b> kuona ripoti za mauzo ya kila siku. Ripoti zinajengwa kiotomatiki saa 12:00 usiku kila siku.'))
    el.extend(bullet_list([
        'Chagua tarehe kwa kutumia kichaguzi cha tarehe.',
        'Ona: Oda Jumla, Mapato Jumla, Bidhaa Zilizouzwa, Oda Zilizolipwa, Zinazosubiri, Zilizoghairiwa.',
        'Ona takwimu za Utendaji wa Wafanyakazi na Bidhaa Bora za siku hiyo.',
        'Bofya <b>"Chapisha"</b> ili kuchapisha ripoti.',
    ]))
    el.append(spacer())
    el.append(section('Uchambuzi wa Mauzo (Dashibodi)'))
    el.append(body('Dashibodi ya Mmiliki inajumuisha uchambuzi tajiri:'))
    el.extend(bullet_list([
        '<b>Mapato dhidi ya Faida</b> — Chati ya bar inayolinganisha mapato na faida ya kila mwezi.',
        '<b>Mwenendo wa Oda</b> — Chati ya mstari ya oda zilizowekwa dhidi ya zilizoghairiwa.',
        '<b>Bidhaa Zilizouzwa</b> — Kiasi cha bidhaa kilichouzwa kwa mwezi.',
        '<b>Mapato kwa Kategoria</b> — Chati ya kanyunyuzi inayoonyesha usambazaji wa kategoria.',
        '<b>Kadi za Muhtasari</b> — Mapato Jumla, Faida Jumla, Oda Jumla, Pembetatu ya Faida, Ukuaji wa Mapato.',
    ]))
    el.append(spacer())
    el.append(section('Maarifa ya Biashara ya AI'))
    el.append(body('Mfumo unatumia AI ya Google Gemini kuchambua data yako ya mauzo na kutoa mapendekezo ya biashara. Mapendekezo yamegawanywa kwa kipaumbele (Juu, Wastani, Chini) na aina (Hifadhi, Bei, Matangazo, Ukuaji, Uendeshaji).'))
    el.append(PageBreak())

    # ── Sura ya 9: Dashibodi ya Mfanyakazi ──
    el.append(chapter('9. Dashibodi ya Mfanyakazi'))
    el.append(hr())
    el.append(body('Mfanyakazi anapoingia, anaona dashibodi yake mwenyewe na:'))
    el.extend(bullet_list([
        '<b>Takwimu za Muhtasari</b> — Oda Zinazosubiri, Inachakatwa, Imesafirishwa Leo, Bidhaa Jumla, Wateja Jumla.',
        '<b>Banner za Tahadhari</b> — Ikiwa kuna oda zinazosubiri uthibitisho wa malipo au ujumbe wa msaada usiosomwa.',
        '<b>Oda za Hivi Karibuni</b> — Oda za mwisho kwa hali na kiasi. Bofya "Angalia Zote" kwa orodha kamili.',
        '<b>Hatua za Haraka</b> — Simamia Oda, Angalia Bidhaa, Wasifu Wangu, Kikasha cha Msaada.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 10: Usimamizi wa Oda ──
    el.append(chapter('10. Usimamizi wa Oda (Mfanyakazi)'))
    el.append(hr())
    el.append(body('Wafanyakazi wanasimamia oda kutoka <b>Mfanyakazi → Oda</b>.'))
    el.append(spacer())
    el.append(section('Kuona na Kuchuja Oda'))
    el.extend(bullet_list([
        'Chuja kwa vigezo: Zote, Inasubiri Malipo, Zinazosubiri, Haijatumika, Imelipwa, Inachakatwa, Imesafirishwa, Imefikishwa, Imeghairiwa.',
        'Tafuta kwa nambari ya oda au jina la mteja.',
        'Bofya "Angalia Zote" ili kupanua zaidi ya chaguo-msingi 15 kwa ukurasa.',
    ]))
    el.append(spacer())
    el.append(section('Kuthibitisha Malipo'))
    el.append(body('Mteja anapolipia kupitia pesa za simu (M-Pesa, Airtel, n.k.):'))
    el.append(steps_table([
        'Oda inaonekana na hali "Inasubiri" na paneli ya uthibitisho.',
        'Thibitisha malipo kwenye akaunti yako ya pesa za simu.',
        'Andika <b>jina kamili la mteja kwa HERUFI KUBWA</b> kama linaloonyeshwa kwenye kuchochea.',
        'Bofya <b>"Thibishisha Malipo"</b>.',
        'Oda inahamia hali ya "Imelipwa" na hisa huondolewa.',
    ]))
    el.append(note('Malipo ya pesa taslimu na ClickPesa yanathibitishwa kiotomatiki. Malipo ya pesa za simu pekee yanahitaji uthibitisho wa mkono.'))
    el.append(spacer())
    el.append(section('Kusahihisha Hali ya Oda'))
    el.append(body('Tumia vifungo vya kitendo kusonga oda:'))
    el.extend(bullet_list([
        '<b>Weka Inachakatwa</b> — Oda inaandaliwa.',
        '<b>Weka Imesafirishwa</b> — Ongeza nambari ya ufuatiliaji na maelezo ya usafirishaji, kisha weka kama imesafirishwa.',
        '<b>Weka Imefikishwa</b> — Thibitisha usafirishaji wa mafanikio.',
        '<b>Ghairi</b> — Ghairi oda (inarudisha hisa).',
    ]))
    el.append(PageBreak())

    # ── Sura ya 11: Usimamizi wa Wateja ──
    el.append(chapter('11. Usimamizi wa Wateja (Mfanyakazi)'))
    el.append(hr())
    el.append(body('Wafanyakazi wanaweza kusimamia wateja kutoka <b>Mfanyakazi → Wateja</b>.'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>Ona</b> wateja wote waliojisajili kwa majina, barua pepe, na hali.',
        '<b>Tafuta</b> kwa jina au barua pepe.',
        '<b>Ongeza</b> wateja wapya kwa jina, barua pepe, na nenosiri chaguo-msingi (sawa na jina lao kamili kwa herufi kubwa).',
        '<b>Washa/Zima Hali</b> — Washa au zima akaunti ya mteja.',
        '<b>Futa</b> mteja (tu kama hana oda).',
    ]))
    el.append(PageBreak())

    # ── Sura ya 12: Kikasha cha Msaada ──
    el.append(chapter('12. Kikasha cha Msaada (Mfanyakazi)'))
    el.append(hr())
    el.append(body('Shughulikia ujumbe wa msaada wa wateja kutoka <b>Mfanyakazi → Msaada</b>. Hii ndiyo njia ya huduma kwa wateja: wateja hupeleka masuala hapa na wafanyakazi hujibu. Kwa mazungumzo na mmiliki wa duka, tumia <b>Mfanyakazi → Kikasha</b> (ona Sura ya 13).'))
    el.append(spacer())
    el.append(section('Kuona Ujumbe'))
    el.extend(bullet_list([
        'Ujumbe unaonyeshwa kwa jina la mteja, mada, kategoria, na hali.',
        'Chuja kwa hali: Zote, Fungua, Inachakatwa, Imetatuliwa, Imefungwa.',
        'Bofya ujumbe kuona mazungumzo kamili.',
    ]))
    el.append(spacer())
    el.append(section('Kujibu Wateja'))
    el.append(steps_table([
        'Fungua ujumbe wa msaada.',
        'Soma tatizo la mteja.',
        'Andika jibu lako kwenye kisanduku.',
        'Bofya <b>"Tuma Jibu"</b>.',
        'Mteja anapokea majibu yako kwenye akaunti yake.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 13: Kikasha cha Mmiliki (Mazungumzo) ──
    el.append(chapter('13. Mazungumzo (Kikasha cha Mmiliki na Mfanyakazi)'))
    el.append(hr())
    el.append(body('Kikasha cha Mazungumzo ni mifumo ya ujumbe kwa mazungumzo kati ya majukumu yafuatayo pekee:'))
    el.extend(bullet_list([
        '<b>Mmiliki ↔ Msimamizi Mkuu</b> — Wasiliana na msimamizi wa mfumo kwa masuala ya akaunti, maswali ya usajili, au msaada wa kiufundi.',
        '<b>Mmiliki ↔ Mteja</b> — Wateja wanaweza kuanzisha mazungumzo nawe kuhusu oda, bidhaa, au maswali ya jumla.',
        '<b>Mmiliki ↔ Mfanyakazi</b> — Wafanyakazi na wamiliki wanaweza kuwasiliana kuhusu uendeshaji wa kila siku, maelezo ya zamu, au idhini.',
    ]))
    el.append(spacer())
    el.append(note('Wateja hawawezi kupeleka ujumbe kwa Msimamizi Mkuu moja kwa moja, na Wafanyakazi hawaoni mazungumzo ya Msimamizi Mkuu. Wateja wanafikia duka kupitia ujumbe wa <b>Msaada</b>.'))
    el.append(spacer())
    el.append(section('Kikasha cha Mmiliki'))
    el.append(body('Fungua Kikasha kutoka <b>Mmiliki → Kikasha</b>. Mazungumzo yamegawanywa katika vichupo: <b>"Zote"</b>, <b>"Wateja"</b>, <b>"Wafanyakazi"</b>, na <b>"Msimamizi"</b>. Mazungumzo yasiyosomwa yanaonyeshwa na beji nyekundu.'))
    el.append(spacer())
    el.append(body('Kuanzisha mazungumzo mpya, bofya kitufe cha <b>"+"</b>. Unaweza kuchagua mteja aliyenunua dukani kwako au mfanyakazi wako yeyote.'))
    el.append(spacer())
    el.append(section('Kikasha cha Mfanyakazi'))
    el.append(body('Wafanyakazi wanaweza kupeleka ujumbe kwa mmiliki wao kutoka <b>Mfanyakazi → Kikasha</b> (karibu na kikasha cha Msaada). Orodha inaonyesha mazungumzo na mmiliki wako, na kitufe cha <b>"+"</b> kinakuwezesha kuanzisha mazungumzo mapya na mmiliki wako moja kwa moja.'))
    el.append(spacer())
    el.append(section('Kujibu Ujumbe'))
    el.append(steps_table([
        'Bofya mazungumzo kuyafungua.',
        'Soma historia ya ujumbe.',
        'Andika jibu lako kwenye kisanduku chini.',
        'Bofya <b>"Tuma"</b>.',
    ]))
    el.append(spacer())
    el.append(note('Kutuma ujumbe kwa mtu yuleyule kunatumia mazungumzo yaliyopo badala ya kuunda ya mara kwa mara.'))
    el.append(spacer())
    el.append(section('Hali ya Ujumbe (Tiki)'))
    el.append(body('Ujumbe unaotuma unaonyesha alama ya usomaji kama WhatsApp karibu na muda. <b>Tiki mbili za kijivu</b> zinamaanisha ujumbe wako umefikishwa; hubadilika kuwa <b>buluu</b> wakati mtu mwingine anafungua mazungumzo na kuisoma. Hali inasasishwa kiotomatiki kila sekunde chache wakati Kikasha kimefunguliwa.'))
    el.append(spacer())
    el.append(section('Kufuta Mazungumzo na Ujumbe'))
    el.extend(bullet_list([
        '<b>Kufuta ujumbe</b> — weka kielekezi juu ya ujumbe wako uliotumwa na ubofye aikoni ya takataka inayoonekana. Thibitisha kufutwa; ni ujumbe wako mwenyewe pekee unaoweza kuondolewa.',
        '<b>Kufuta mazungumzo</b> — bofya aikoni ya takataka juu ya mazungumzo yaliyofunguliwa. Thibitisha ili kuondoa mazungumzo yote kwa pande zote mbili.',
    ]))
    el.append(note('Kufuta mazungumzo kunaondoa mazungumzo yote. Kufuta ujumbe mmoja kunaondoa ujumbe huo tu kwenye mazungumzo; yaliyosalia yanabaki.'))
    el.append(PageBreak())

    # ── Sura ya 14: Mfumo wa Uhasibu ──
    el.append(chapter('14. Mfumo wa Uhasibu'))
    el.append(hr())
    el.append(body('Mfumo wa Uhasibu unatoa uhasibu kamili wa kitabu cha mgawanyiko kwa biashara yako. Fikia kupitia <b>Mmiliki → Uhasibu</b>.'))
    el.append(spacer())
    el.append(section('Jedwali la Akaunti'))
    el.append(body('Mfumo una akaunti 22 zilizosanidiwa chaguo-msingi zilizogawanywa katika makundi matano:'))
    el.extend(bullet_list([
        '<b>Asseti (5 akaunti)</b> — Fedha Taslimu, Akaunti ya Benki, Akaunti zinazodaiwa, Hifadhi, Pesa za Uthabiti.',
        '<b>Deni (4 akaunti)</b> — Akaunti zinazolipwa, Mikopo Inayolipwa, Kodi Inayolipwa, Gharama zilizojijengea.',
        '<b>Maji (4 akaunti)</b> — Mtaji wa Mmiliki, Faida iliyochomwa, Mtaji, Kuchukua Fedha.',
        '<b>Mapato (4 akaunti)</b> — Mapato ya Mauzo, Mapato ya Huduma, Mapato Mengine, Punguzo Zilizotolewa.',
        '<b>Gharama (5 akaunti)</b> — Gharama ya Bidhaa Zilizouzwa, Kukodi, Mishahara, Umeme, Vifaa Ofisini.',
    ]))
    el.append(spacer())
    el.append(body('Simamia jedwali la akaunti katika <b>/owner/accounting/chart-of-accounts</b>. Unaweza:'))
    el.extend(bullet_list([
        '<b>Ongeza</b> akaunti mpya kwa msimbo, jina, aina, na maelezo ya hiari.',
        '<b>Sahihisha</b> maelezo ya akaunti zilizopo.',
        '<b>Futa</b> akaunti ambazo hazina shughuli.',
    ]))
    el.append(spacer())
    el.append(section('Kuingiza Jumla ya Fedha'))
    el.append(body('Kila muamala wa fedha unarekodiwa kama jedwali la fedha na nambari ya kitambulisho ya kipekee katika muundo wa <b>JE-YYYYMMDD-XXX</b>.'))
    el.append(spacer())
    el.append(body('Jumla za fedha zinaundwa kiotomatiki kwa:'))
    el.extend(bullet_list([
        '<b>Malipo ya Oda</b> — Debiti Fedha/Benki, Mkopo Mapato ya Mauzo (na Gharama ya Bidhaa za Hifadhi).',
        '<b>Kughairi Oda</b> — Inarejesha jedwali la awali la malipo.',
        '<b>Pokea Oda ya Ununuzi</b> — Debiti Hifadhi, Mkopo Akaunti zinazolipwa.',
    ]))
    el.append(spacer())
    el.append(body('Unaweza pia kuunda <b>jumla za fedha kwa mkono</b> kwa marekebisho, kurekebisha, au muamala mwingine wowote wa fedha. Kila jedwali linahitaji angalau vipengele viwili vya mstari (debiti na mkopo) ambavyo lazima vilanishwe.'))
    el.append(spacer())
    el.append(body('Jumla za fedha zinafuata mtindo wa hatua tatu wa hali:'))
    el.extend(bullet_list([
        '<b>Muhtasari</b> — Jedwali limehifadhiwa bado halijawekwa kwenye daftari. Inaweza kuhaririwa au kufutwa.',
        '<b>Imewekwa</b> — Jedwali limetiwa siku na linaonekana katika ripoti za fedha. Halihitaji kuhaririwa.',
        '<b>Limetendwa</b> — Jedwali limeghairiwa. Jedwali la awali linaendelea kwenye mfumo kwa madhumuni ya ukaguzi, athari yake ya fedha imerejeshwa.',
    ]))
    el.append(spacer())
    el.append(section('Ripoti za Fedha'))
    el.append(body('Tengeneza ripoti za fedha kutoka <b>/owner/accounting</b>:'))
    el.extend(bullet_list([
        '<b>Majaribio ya Majaribio</b> — Orodha ya akaunti zote na mizani yao ya debiti au mkopo. Inatumika kuthibitisha kuwa debiti jumla ni sawa na mikopo jumla.',
        '<b>Mapato na Gharama</b> — Inaonyesha mapato minus gharama kwa kipindi. Inaonyesha faida au hasara halisi.',
        '<b>Mizani</b> — Mtazamo wa asseti, deni, na maji wakati wa wakati. Lazima isawazishwe (Asseti = Deni + Maji).',
        '<b>Daftari Kuu</b> — Mtazamo wa kina wa shughuli zote kwa akaunti yoyote. Chuja kwa akaunti na kipindi.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 15: Kamisheni na Mapato ya Wafanyakazi ──
    el.append(chapter('15. Kamisheni na Mapato ya Wafanyakazi'))
    el.append(hr())
    el.append(section('Mfumo wa Kamisheni'))
    el.append(body('Mfumo wa kamisheni unawahimiza wafanyakazi kulingana na <b>faida</b> wanayoiunda, si mapato tu. Kila mfanyakazi ana kiwango cha kamisheni kilichowekwa na mmiliki.'))
    el.append(spacer())
    el.append(body('Kamisheni inafanya kazi hivi:'))
    el.extend(bullet_list([
        'Oda ikipewa hali ya <b>Imelipwa</b>, mfumo unakokotoa faida (Bei ya Kuuza - Bei ya Gharama) kwa kila bidhaa.',
        'Kamisheni = Faida Jumla × Kiwango cha Kamisheni ya Mfanyakazi (mfano, 5% ya TSh 200,000 faida = TSh 10,000).',
        'Ikiwa oda ina faida sifuri au hasi, kamisheni haipatikani.',
        'Kamisheni zinafuatiliwa kwa mfanyakazi mmoja mmoja na zinaongezeka mpaka zilipwe.',
    ]))
    el.append(spacer())
    el.append(body('Mmiliki anaweza kusimamia kamisheni kutoka <b>Mmiliki → Kamisheni</b>:'))
    el.extend(bullet_list([
        '<b>Ona</b> kamisheni zinazosubiri kwa kila mfanyakazi pamoja na maelezo ya faida.',
        '<b>Lipa</b> kamisheni za mtu mmoja kuziweka kama zilipwa.',
        '<b>Lipa Zote</b> kulipa kamisheni zote zinazosubiri mara moja.',
    ]))
    el.append(spacer())
    el.append(section('Mapato ya Wafanyakazi'))
    el.append(body('Wafanyakazi wanaweza kuona mapato yao mwenyewe katika <b>/employee/earnings</b>. Dashibodi ya mapato inaonyesha:'))
    el.extend(bullet_list([
        '<b>Faida Jumla Iliyotolewa</b> — Faida ya jumla kutoka kwa oda zote zilizoshughulikiwa na mfanyakazi huyu.',
        '<b>Oda Jumla</b> — Idadi ya oda zenye kamisheni.',
        '<b>Kamisheni Zinazosubiri</b> — Kiasi cha kamisheni kinachosubiri malipo.',
        '<b>Kamisheni Zilizolipwa</b> — Jumla ya kiasi kilicholipwa kwa mfanyakazi.',
    ]))
    el.append(note('Kamisheni ni za faida pekee bila mshahara wa msingi. Hii inahimiza wafanyakazi kuzingatia bidhaa zenye faida kubwa.'))
    el.append(spacer())
    el.append(section('Winga (Wakuza Biashara wa Mtaani)'))
    el.append(body('A <b>Winga</b> ni mkuza biashara wa mtaani anayeleta wateja kwenye duka lako. Unaweza kusajili winga kwa biashara yako (hiari kwa kila tawi) na kuwalipa kamisheni kwa wateja wanaoleta. Winga husimamiwa kutoka <b>Mmiliki → Winga</b>; wafanyakazi pia wanaweza kuwaona na kuwahudumia.'))
    el.append(spacer())
    el.append(section('Jinsi Kamisheni ya Winga Inavyofanya Kazi'))
    el.append(body('Oda inapowekwa na winga kuambatanishwa, kiwango cha kamisheni ya winga huongezwa kama <b>asilimia ya kuongeza bei ya bidhaa</b>. Hii "ada ya winga" imojumuishwa kwenye jumla ya mteja na inafadhili kamisheni ya winga. Kwa mfano, kiwango cha winga cha 10% kwenye oda ya TSh 100,000 kinaongeza TSh 10,000 kwenye jumla, ambayo inakuwa kamisheni ya winga.'))
    el.append(spacer())
    el.append(body('Kusajili winga:'))
    el.extend(bullet_list([
        'Nenda kwenye <b>Mmiliki → Winga</b> na ubofye <b>"Ongeza Winga"</b>.',
        'Weka <b>jina</b> na <b>nambari ya simu</b>.',
        'Weka <b>nambari ya TIN</b> ya winga (Nambari ya Kitambulisho cha Mlipa Kodi TRA) na <b>nambari ya NIDA</b> kwa kufuata sheria za kodi.',
        'Weka <b>kiwango cha kamisheni (%)</b> — asilimia inayoongezwa kwenye mauzo.',
        'Kwa hiari, mgawa winga kwa <b>tawi</b>.',
        'Bofya <b>"Hifadhi"</b>.',
    ]))
    el.append(spacer())
    el.append(section('Kodi ya Kuzuia (TDS)'))
    el.append(body('Tanzania inahitaji <b>kodi ya kuzuia (TDS) ya 5%</b> kutolewa kwenye malipo ya kamisheni. Unapolipa winga, mfumo hutoa 5% kiotomatiki kutoka kwa kamisheni ya jumla na kuiweka kama <b>Kodi ya Kuzuia Inayolipwa</b> kwa ajili ya kuipeleka TRA.'))
    el.append(spacer())
    el.append(body('Mfano: Winga mwenye kamisheni ya TSh 10,000 anapokea <b>TSh 9,500</b>, na <b>TSh 500</b> huzuiliwa kwa TRA. Kuingiza jumla kunatokea kiotomatiki (debiti Winga Kamisheni Inayolipwa, mkopo Fedha Taslimu na Kodi ya Kuzuia Inayolipwa).'))
    el.append(spacer())
    el.append(section('Kulipa Kamisheni za Winga'))
    el.append(body('Kutoka kwenye mtazamo wa kamisheni za winga, unaweza:'))
    el.extend(bullet_list([
        '<b>Ona</b> kamisheni zinazosubiri kwa kila winga na kiasi cha jumla, kodi (TDS), na halisi.',
        '<b>Lipa</b> kamisheni moja — kiasi halisi hulipwa na kodi ya kuzuia inarekodiwa.',
        '<b>Lipa Zote</b> — lipa kamisheni zote zinazosubiri kwa hatua moja.',
    ]))
    el.append(spacer())
    el.append(note('Kamisheni zinaundwa kiotomatiki pale oda yenye winga inapowekwa kama imelipwa. Kughairi oda au kurejesha bidhaa kunarejesha kamisheni kwa uwiano.'))
    el.append(PageBreak())

    # ── Sura ya 16: Usimamizi wa Hifadhi ──
    el.append(chapter('16. Usimamizi wa Hifadhi'))
    el.append(hr())
    el.append(body('Fuatilia na simamia viwango vya hisa yako kutoka <b>Mmiliki → Hifadhi</b>.'))
    el.append(spacer())
    el.append(section('Dashibodi ya Hisa'))
    el.append(body('Dashibodi ya hifadhi inakupa mtazamo wa haraka wa hali ya hisa yako:'))
    el.extend(bullet_list([
        '<b>Aina Jumla</b> — Nambari jumla ya aina za bidhaa katika katalogi yako.',
        '<b>Hisa Ndogo</b> — Nambari ya aina ambazo hisa iko au chini ya kiwango cha kuamuru upya.',
        '<b>Thamani Jumla ya Hisa</b> — Thamani iliyounganishwa ya hifadhi yote kulingana na bei za gharama.',
        '<b>Hisa Iliyokwisha</b> — Nambari ya aina zenye hisa sifuri.',
    ]))
    el.append(spacer())
    el.append(section('Kurekebisha Hisa'))
    el.append(body('Fanya marekebisho ya hisa kwa mkono kupitia modali ya marekebisho:'))
    el.append(steps_table([
        'Bofya <b>"Rekebisha Hisa"</b> kwenye ukurasa wa hifadhi.',
        'Chagua <b>aina ya bidhaa</b> ya kurekebisha.',
        'Chagua <b>aina ya marekebisho</b>:',
        '    — <b>Marekebisho</b>: Marekebisho ya jumla ya viwango vya hisa.',
        '    — <b>Uharibifu</b> — Rekodi bidhaa zilizoharibika.',
        '    — <b>Fungua</b> — Kiasi cha kuanza cha bidhaa mpya.',
        'Weka <b>kiasi</b> (chanya kuongeza, hasi kupunguza).',
        'Ongeza <b>maelezo</b> yanayoeleza sababu ya marekebisho.',
        'Bofya <b>"Hifadhi"</b> ili kurekodi marekebisho.',
    ]))
    el.append(spacer())
    el.append(section('Historia ya Shughuli'))
    el.append(body('Kila mabadiliko ya hisa yanaandikwa kwenye historia ya shughuli. Kila kipengele kinaonyesha:'))
    el.extend(bullet_list([
        '<b>Aina</b> — Sababu ya mabadiliko ya hisa (Mauzo, Kughairi, Marekebisho, Uharibifu, Fungua, Oda ya Ununuzi, n.k.).',
        '<b>Bidhaa</b> — Aina iliyoathiriwa.',
        '<b>Kiasi</b> — Nambari iliyoongezwa (+) au kuondolewa (-).',
        '<b>Mizani Inayoendelea</b> — Kiwango cha hisa baada ya shughuli hii.',
    ]))
    el.append(note('Hisa huondolewa kiotomatiki pale oda zinapolipwa na kurejeshwa pale oda zinapoghairiwa. Kupokea oda za ununuzi pia huongeza hisa kiotomatiki.'))
    el.append(PageBreak())

    # ── Sura ya 17: Oda za Ununuzi na Wachuuzi ──
    el.append(chapter('17. Oda za Ununuzi na Wachuuzi'))
    el.append(hr())
    el.append(section('Wachuuzi'))
    el.append(body('Simamia wachuuzi wako kutoka <b>Mmiliki → Wachuuzi</b>. Kila rekodi ya mtu anayeuza inajumuisha:'))
    el.extend(bullet_list([
        '<b>Jina la Mchuuzi</b> — Jina la kampuni au mtu.',
        '<b>Mtu wa Mawasiliano</b> — Mtu wa mawasiliano wa msingi kwa mhuzaji.',
        '<b>Barua Pepe</b> — Anwani ya barua pepe ya mhuzaji.',
        '<b>Simu</b> — Nambari ya simu ya mhuzaji.',
        '<b>Anwani</b> — Anwani ya kimwili.',
    ]))
    el.append(spacer())
    el.append(body('Unaweza kuongeza, kuhariri, na kufuta wachuuzi. Tumia upau wa utafutaji kupata wachuuzi kwa uwanja wowote (jina, mtu wa mawasiliano, barua pepe, simu, au anwani).'))
    el.append(spacer())
    el.append(section('Oda za Ununuzi'))
    el.append(body('Unda na simamia oda za ununuzi kutoka <b>Mmiliki → Oda za Ununuzi</b> ili kujaza upya hifadhi kutoka kwa wachuuzi.'))
    el.append(spacer())
    el.append(body('Kuunda Oda ya Ununuzi:'))
    el.append(steps_table([
        'Bofya <b>"Unda Oda ya Ununuzi"</b>.',
        'Chagua <b>mhuzaji</b> kunja chini.',
        'Ongeza <b>vipengele vya mstari</b> — kwa kila kitu, chagua aina ya bidhaa, weka kiasi na gharama ya kitu.',
        'Kagua jumla ya gharama.',
        'Bofya <b>"Hifadhi"</b> ili kuunda PO katika hali ya Muhtasari.',
    ]))
    el.append(spacer())
    el.append(body('Mtiririko wa hali ya Oda ya Ununuzi:'))
    el.extend(bullet_list([
        '<b>Muhtasari</b> — PO imeundwa bado haijatumwa kwa mhuzaji. Inaweza kuhaririwa.',
        '<b>Imetumwa</b> — PO imetumwa kwa mhuzaji. Inasubiri uwasilishaji.',
        '<b>Imepokelewa</b> — Bidhaa zimepokelewa. Hifadhi husahihishwa kiotomatiki na jumla za fedha zinaundwa (debiti Hifadhi, mkopo Akaunti zinazolipwa).',
    ]))
    el.append(spacer())
    el.append(section('Mlango wa Mchuuzi'))
    el.append(body('Wachuuzi wana mlango wao wa kuingia kuona oda za ununuzi zilizowakilishwa kwao. Kutoka kwa mlango wa mhuzaji, wachuuzi wanaweza:'))
    el.extend(bullet_list([
        '<b>Kuona</b> oda zao zote za ununuzi na hali ya sasa.',
        '<b>Sahihisha Hali</b> — Weka oda kama zimetumwa au zimepokelewa.',
        '<b>Kuona Maelezo</b> — Ona vipengele, kiasi, na gharama.',
    ]))
    el.append(note('Mlango wa mhuzaji hurahisisha mawasiliano kati ya biashara yako na wachuuzi, kupunguza uhitaji wa simu au barua pepe kufuatilia oda.'))
    el.append(PageBreak())

    # ── Sura ya 18: Tahadhari za Hisa ──
    el.append(chapter('18. Tahadhari za Hisa'))
    el.append(hr())
    el.append(section('Utambuzi wa Hisa Ndogo'))
    el.append(body('Mfumo unafuatilia viwango vya hifadhi kiotomatiki na kuunda tahadhari za hisa pale vikwazavyo vinapovunjika. Tahadhari zinaundwa kulingana na <b>kiwango cha kuamuru upya</b> kilichowekwa kwa kila aina ya bidhaa.'))
    el.append(spacer())
    el.append(body('Aina mbili za tahadhari zinaundwa:'))
    el.extend(bullet_list([
        '<b>Hisa Ndogo</b> — Inaundwa pale kiasi cha aina kikiwa sawa au chini ya kiwango cha kuamuru upya bado juu ya sifuri. Inaonyesha kuwa hisa inahitaji kujazwa upya hivi karibuni.',
        '<b>Hisa Imekwisha</b> — Inaundwa pale kiasi cha aina kifikia sifuri. Inaonyesha hitaji la dharura la kujaza upya.',
    ]))
    el.append(spacer())
    el.append(body('Tahadhari zinakaguliwa na kuundwa kiotomatiki pale mabadiliko ya hifadhi yanapotokea (mfano, oda inapolipwa, marekebisho ya hisa yanaporekodiwa, au oda ya ununuzi inapopokelewa).'))
    el.append(spacer())
    el.append(section('Kusimamia Tahadhari'))
    el.append(body('Ona na simamia tahadhari za hisa kutoka <b>Mmiliki → Tahadhari za Hisa</b>.'))
    el.append(spacer())
    el.append(body('Chuja tahadhari kwa hali:'))
    el.extend(bullet_list([
        '<b>Zote</b> — Ona tahadhari zote bila kujali hali.',
        '<b>Zinaendelea</b> — Ona tahadhari zisizotatuliwa zinazohitaji uvuvi.',
        '<b>Zinakiriwa</b> — Tahadhari ambazo zimeonwa bado hazijatatuliwa.',
        '<b>Zimetatuliwa</b> — Tahadhari zilizoshughulikiwa (hisa imejazwa upya).',
    ]))
    el.append(spacer())
    el.append(body('Vifungo vinavyopatikana kwenye tahadhari:'))
    el.extend(bullet_list([
        '<b>Kukiri</b> — Weka tahadhari kama imeonwa. Inaihamisha kutoka Hali ya Active hadi Zinakiriwa, ikimaanisha unaifahamu.',
        '<b>Katatua</b> — Weka tahadhari kama imetatuliwa. Hii lazima ifanyike baada ya hisa kujazwa upya au tatizo kushughulikiwa.',
    ]))
    el.append(note('Kuweka viwango vinavyofaa vya kuamuru upya kwa kila aina ya bidhaa kuhakikisha unapokea tahadhari za wakati kabla ya kukimbia maarufu.'))
    el.append(PageBreak())

    # ── Sura ya 19: Ununuzi kwa Mteja ──
    el.append(chapter('19. Ununuzi kwa Mteja'))
    el.append(hr())
    el.append(body('Wateja wanaweza kuangalia na kununua bidhaa kutoka duka la mtandaoni.'))
    el.append(spacer())
    el.append(section('Kuangalia Bidhaa'))
    el.extend(bullet_list([
        'Ukurasa wa nyumbani unaonyesha bidhaa mashuhuri na kategoria.',
        'Tumia <b>ramani ya kategoria</b> kuchuja kwa aina.',
        'Bofya bidhaa yoyote kuona maelezo kamili, aina, na bei.',
    ]))
    el.append(spacer())
    el.append(section('Kuongeza kwenye Kikapu'))
    el.append(steps_table([
        'Chagua aina ya bidhaa (rangi/uhifadhi) ikiwa inatumika.',
        'Chagua kiasi.',
        'Bofya <b>"Ongeza kwenye Kikapu"</b>.',
        'Ikoni ya kikapu kwenye upau wa juu inasahihishwa na idadi ya bidhaa.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 20: Malipo na Uthibitishaji ──
    el.append(chapter('20. Malipo na Uthibitishaji'))
    el.append(hr())
    el.append(steps_table([
        'Bofya ikoni ya <b>Kikapu</b> na ukague bidhaa zako.',
        'Bofya <b>"Endelea na Malipo"</b>.',
        'Chagua au ongeza <b>anwani ya usafirishaji</b>.',
        'Chagua <b>chaguo la usafirishaji</b>: Chukua Dukani (bure) au Usafirishaji wa Nyumbani (ada inakokolewa kiotomatiki kulingana na jiji lako).',
        'Chagua <b>njia ya malipo</b>: Pesa Taslimu, M-Pesa, Airtel Money, Mixx by Yas, au Halopesa.',
        'Ikiwa unalipia kupitia pesa za simu, weka nambari yako ya simu.',
        'Bofya <b>"Weka Oda"</b>.',
        'Kwa <b>Pesa Taslimu</b>: Oda yako inathibitishwa mara moja. Chukua dukani.',
        'Kwa <b>Pesa za Simu</b>: Tuma malipo kwa nambari iliyoonyeshwa. Oda yako itathibishwa na wafanyakazi.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 21: Akaunti Yangu ──
    el.append(chapter('21. Akaunti Yangu (Mteja)'))
    el.append(hr())
    el.append(body('Wateja wanaweza kusimamia akaunti yao kutoka <b>Akaunti Yangu</b>.'))
    el.append(spacer())
    el.extend(bullet_list([
        '<b>Dashibodi</b> — Ona takwimu za oda: Oda Jumla, Inachakatwa, Imefikishwa.',
        '<b>Historia ya Oda</b> — Angalia oda zote za zamani kwa hali na maelezo.',
        '<b>Msaada</b> — Tuma ujumbe kuhusu masuala ya malipo, hali ya oda, usafirishaji, au maombi ya kurejeshewa pesa. Angalia majibu kutoka kwa wafanyakazi.',
        '<b>Kikasha</b> — Mazungumzo na mmiliki wa duka kuhusu oda zako. Unaweza kufuta ujumbe wako uliotumwa (aikoni ya takataka kwenye ujumbe) au mazungumzo yote (aikoni ya takataka juu ya mazungumzo).',
        '<b>Wasifu</b> — Sahihisha jina na taarifa za kibinafsi.',
        '<b>Nenosiri</b> — Badilisha nenosiri lako (lazima lifikie mahitaji ya usalama).',
        '<b>Anwani</b> — Simamia anwani zilizohifadhiwa za usafirishaji.',
    ]))
    el.append(PageBreak())

    # ── Sura ya 22: Mipangilio ya Lugha ──
    el.append(chapter('22. Mipangilio ya Lugha'))
    el.append(hr())
    el.append(body('Mfumo unasaidia lugha mbili: <b>English</b> na <b>Kiswahili</b>.'))
    el.append(spacer())
    el.append(steps_table([
        'Bofya kichaguzi cha lugha kwenye upau wa urambazaji wa juu.',
        'Chagua <b>English</b> au <b>Kiswahili</b>.',
        'Kiolesura chote hubadilika mara moja — hakuna haja ya kupakia upya ukurasa.',
    ]))
    el.append(note('Upendeleo wako wa lughuba unahifadhiwa na unadumu katika vikao.'))
    el.append(PageBreak())

    # ── Sura ya 23: Sera ya Nenosiri ──
    el.append(chapter('23. Sera ya Nenosiri'))
    el.append(hr())
    el.append(body('Nenosiri zote lazima zifikie mahitaji yafuatayo:'))
    el.append(spacer())
    el.extend(bullet_list([
        'Angalau herufi <b>8</b> ndefu.',
        'Angalau herufi moja <b>kubwa</b> (A-Z).',
        'Angalau herufi moja <b>ndogo</b> (a-z).',
        'Angalau <b>nambari</b> moja (0-9).',
        'Angalau herufi moja <b>maalum</b> (!@#$%...).',
    ]))
    el.append(spacer())
    el.append(section('Kubadilisha Nenosiri Lazima'))
    el.append(body('Ikiwa nenosiri lako halijabadilishwa au lilibadilishwa zaidi ya siku 3 zilizopita, modal ya kulazimisha kubadilisha nenosiri itaonekana unapoingia. Lazima weke nenosiri jipya kabla ya kufikia mfumo.'))
    el.append(spacer())
    el.append(section('Nenosiri Chaguo-msingi la Mfanyakazi'))
    el.append(body('Mmiliki anapounda akaunti mpya ya mfanyakazi, nenosiri chaguo-msingi ni <b>jina kamili la mfanyakazi kwa herufi kubwa</b> (mfano, "MATHEW ZACHARIA"). Wafanyakazi wanapaswa kubadilisha hili mara moja wakati wa kuingia kwa mara ya kwanza.'))
    el.append(spacer())
    el.append(section('Nenosiri Chaguo-msingi la Mmiliki'))
    el.append(body('Akaunti mpya ya mmiliki inapoundwa na msimamizi wa mfumo, nenosiri chaguo-msingi ni <b>jina kamili la mmiliki kwa herufi kubwa</b> (mfano, "JOHN DOE"). Msimamizi hushiriki nenosiri hili kwa usalama na mmiliki.'))
    el.append(PageBreak())

    # ── Sura ya 24: Kipindi na Usalama ──
    el.append(chapter('24. Kipindi na Usalama'))
    el.append(hr())
    el.append(section('Kutoka Kiotomatiki (Kutokuwa na Shughuli)'))
    el.append(body('Kwa usalama wako, mfumo unakutoa nje kiotomatiki baada ya <b>dakika 15 za kutokuwa na shughuli</b>. Kusogeza kipanya, kubofya, au kuandika kunarejesha saa.'))
    el.append(spacer())
    el.append(body('Ukiwa kimya kwa dakika 14, onyo linaonekana na <b>hesabu ya chini ya sekunde 60</b>. Shughuli yoyote ya kipanya au kibodi inaondoa onyo na kukuweka umeingia. Hesabu inapofikia sifuri, unatolewa nje na kurudishwa kwenye ukurasa wa kuingia.'))
    el.append(spacer())
    el.append(section('Kuondoka kwenye Dashibodi'))
    el.append(body('Ukibadilisha kichupo au kuingia programu nyingine, saa inasitisha. Ukirudi ndani ya <b>dakika 10</b>, kipindi chako kinaendelea. Ukibaki mbali kwa <b>zaidi ya dakika 10</b>, mfumo unakutoa nje kulinda akaunti yako.'))
    el.append(spacer())
    el.append(section('Usalama wa Kuingia'))
    el.append(body('Ili kulinda akaunti yako dhidi ya ufikiaji usioidhinishwa:'))
    el.extend(bullet_list([
        'Majerabi ya kuingia yamepunguzwa hadi <b>5 kwa dakika</b> kwa kila anwani ya IP.',
        'Baada ya majerabi <b>5 yaliyoshindikana</b>, akaunti inafungwa kiotomatiki kwa <b>dakika 30</b>.',
        'Usajili wa akaunti mpya umepunguzwa hadi <b>3 kwa dakika</b> na <b>10 kwa siku</b> kwa kila IP.',
    ]))
    el.append(spacer())
    el.append(note('Ikiwa akaunti yako imefungwa, subiri dakika 30 na ujaribu tena, au wasiliana na msimamizi wako wa mfumo kwa msaada.'))
    el.append(spacer())
    el.append(spacer())
    el.append(hr())
    el.append(Paragraph('<b>ERP Duka la Elektroniki</b> — Manual ya Mtumiaji Toleo 3.0 — Julai 2026', sFooter))
    el.append(Paragraph('Kwa msaada wa kiufundi, wasiliana na msimamizi wako wa mfumo.', sFooter))

    return el


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def build_pdf(elements, filename):
    out_dir = os.path.join(os.path.dirname(__file__), 'docs')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f'✅ Generated: {path}')
    return path


if __name__ == '__main__':
    print('Generating English user manual...')
    build_pdf(build_en(), 'User_Manual_EN.pdf')

    print('Generating Swahili user manual...')
    build_pdf(build_sw(), 'User_Manual_SW.pdf')

    print('Done!')
