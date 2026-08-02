#!/usr/bin/env python3
"""Generate the professional Developer & Technical Documentation PDF for ERP Electronics Store."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Register fonts ──────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBd', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Mono', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))

# ── Brand palette (must match the application + favicon) ────────────────────
RED = HexColor('#e74c3c')
DARK = HexColor('#2c3e50')
BLUE = HexColor('#2980b9')
GREEN = HexColor('#27ae60')
GRAY = HexColor('#888888')
LIGHT_GRAY = HexColor('#f5f5f5')
BORDER = HexColor('#dddddd')
DARK_TEXT = HexColor('#333333')
MID_TEXT = HexColor('#555555')

# ── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent='Normal', **kwargs):
    base = styles[parent] if parent in styles else styles['Normal']
    if 'fontName' not in kwargs:
        kwargs['fontName'] = 'DejaVu'
    return ParagraphStyle(name, parent=base, **kwargs)

sTitle = make_style('sTitle', fontSize=30, fontName='DejaVuBd', textColor=white, alignment=TA_CENTER, leading=36)
sSubtitle = make_style('sSubtitle', fontSize=13, textColor=HexColor('#dddddd'), alignment=TA_CENTER, leading=18)
sCoverMeta = make_style('sCoverMeta', fontSize=10, textColor=HexColor('#aaaaaa'), alignment=TA_CENTER, leading=16)
sChapter = make_style('sChapter', fontSize=20, fontName='DejaVuBd', textColor=DARK, spaceAfter=8, spaceBefore=14, leading=26)
sSection = make_style('sSection', fontSize=13.5, fontName='DejaVuBd', textColor=RED, spaceAfter=6, spaceBefore=12, leading=18)
sBody = make_style('sBody', fontSize=9.5, textColor=DARK_TEXT, alignment=TA_JUSTIFY, leading=14.5, spaceAfter=5)
sBullet = make_style('sBullet', fontSize=9.5, textColor=DARK_TEXT, leading=13.5, leftIndent=20, spaceAfter=3)
sNote = make_style('sNote', fontSize=8.5, textColor=GRAY, leading=12, spaceAfter=4, leftIndent=10)
sTocEntry = make_style('sTocEntry', fontSize=10.5, textColor=DARK, leading=15, spaceAfter=4, leftIndent=10)
sFooter = make_style('sFooter', fontSize=8, textColor=GRAY, alignment=TA_CENTER)
sTableHeader = make_style('sTableHeader', fontSize=8.5, fontName='DejaVuBd', textColor=white, leading=11)
sTableCell = make_style('sTableCell', fontSize=8.5, textColor=DARK_TEXT, leading=11)
sCode = make_style('sCode', fontSize=8, fontName='Mono', textColor=HexColor('#1a1a1a'), leading=11.5, spaceAfter=6, leftIndent=6)


class LogoFlowable(Flowable):
    """Brand logo: red rounded square with a white lightning bolt."""

    def __init__(self, width=84, height=84):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        w, h = self.width, self.height
        c = self.canv
        c.saveState()
        c.setFillColor(RED)
        c.roundRect(0, 0, w, h, w * 0.22, stroke=0, fill=1)
        s = w / 64.0
        pts = [(36 * s, 56 * s), (16 * s, 28 * s), (28 * s, 28 * s),
               (24 * s, 8 * s), (44 * s, 36 * s), (32 * s, 36 * s)]
        p = c.beginPath()
        p.moveTo(*pts[0])
        for pt in pts[1:]:
            p.lineTo(*pt)
        p.close()
        c.setFillColor(white)
        c.setStrokeColor(white)
        c.setLineWidth(2)
        c.setLineJoin(1)
        c.drawPath(p, stroke=1, fill=1)
        c.restoreState()


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=8)


def bullet_list(items):
    return [Paragraph(f'• {item}', sBullet) for item in items]


def note(text):
    return Paragraph(f'<i>{text}</i>', sNote)


def body(text):
    return Paragraph(text, sBody)


def section(text):
    return Paragraph(text, sSection)


def chapter(text):
    return Paragraph(text, sChapter)


def spacer(h=6):
    return Spacer(1, h)


def code_block(lines):
    el = []
    for line in lines:
        el.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), sCode))
    return el


def info_table(rows, col_widths=None, header=None):
    if col_widths is None:
        col_widths = [150, 330]
    data = []
    if header:
        data.append([Paragraph(f'<b>{h}</b>', sTableHeader) for h in header])
    for row in rows:
        data.append([Paragraph(str(c), sTableCell) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
    ]
    if header:
        style.append(('BACKGROUND', (0, 0), (-1, 0), DARK))
        style.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]))
    else:
        style.append(('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY))
    t.setStyle(TableStyle(style))
    return t


def swatch_table(rows):
    data = []
    for hex_code, name, usage in rows:
        cell = Table([[Paragraph(f'<b>{hex_code}</b>', make_style('sw', fontSize=8.5, fontName='DejaVuBd', textColor=white))]],
                     colWidths=[64], rowHeights=[34])
        cell.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor(hex_code)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        data.append([cell, Paragraph(f'<b>{name}</b>', sTableCell), Paragraph(usage, sTableCell)])
    t = Table(data, colWidths=[80, 160, 240])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('BACKGROUND', (1, 0), (-1, -1), white),
    ]))
    return t


def cover_page():
    el = []
    el.append(Spacer(1, 24))
    cover = Table([[LogoFlowable(96, 96)]], colWidths=[480], rowHeights=[120])
    cover.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    el.append(cover)
    el.append(Spacer(1, 20))
    txt = Table([
        [Paragraph('ERP Electronics Store', sTitle)],
        [Spacer(1, 8)],
        [Paragraph('Developer & Technical Documentation', sSubtitle)],
        [Spacer(1, 30)],
        [HRFlowable(width="55%", thickness=2, color=RED, spaceBefore=4, spaceAfter=4)],
        [Spacer(1, 14)],
        [Paragraph('Version 1.0 &nbsp;|&nbsp; July 2026', sCoverMeta)],
        [Paragraph('Software Developers &middot; System Administrators &middot; Superadmins', sCoverMeta)],
    ], colWidths=[480])
    txt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    el.append(txt)
    el.append(PageBreak())
    return el


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 20 * mm, f'ERP Electronics Store — Developer Documentation v1.0  ·  Page {doc.page}')
    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
#  CONTENT
# ══════════════════════════════════════════════════════════════════════════════

def build():
    el = []
    el += cover_page()

    # ── Table of Contents ──
    el.append(chapter('Table of Contents'))
    el.append(hr())
    toc = [
        ('1.', 'Document Control'),
        ('2.', 'System Overview & Architecture'),
        ('3.', 'Technology Stack'),
        ('4.', 'Brand Identity & Visual Guidelines'),
        ('5.', 'System Roles & Permissions'),
        ('6.', 'Database Schema & Models'),
        ('7.', 'Authentication & Authorization'),
        ('8.', 'API Reference'),
        ('9.', 'Superadmin Module'),
        ('10.', 'Security Measures'),
        ('11.', 'Analytics & AI Insights'),
        ('12.', 'Documentation & Diagrams'),
        ('13.', 'Development Commands & Environment'),
        ('14.', 'Deployment'),
        ('15.', 'Full Business Cycle'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    # ── 1. Document Control ──
    el.append(chapter('1. Document Control'))
    el.append(hr())
    el.append(info_table([
        ('Version', '1.0'),
        ('Date', 'July 2026'),
        ('Status', 'Released'),
        ('Audience', 'Software developers, system administrators, superadmins, and technical stakeholders'),
        ('Scope', 'Architecture, brand identity, technical design, security, deployment, and administration of the ERP Electronics Store platform'),
        ('Related documents', 'User_Manual_EN.pdf, User_Manual_SW.pdf, ERD.drawio, ClassDiagram.drawio, UseCase.drawio, SequenceDiagrams.drawio'),
    ]))
    el.append(spacer(10))
    el.append(section('Repositories'))
    el.append(info_table([
        ('Frontend', '<font face="Mono">erp-electronics/</font> — Vue 3 SPA (storefront + dashboards + superadmin panel)'),
        ('Backend', '<font face="Mono">erp-electronics-api/</font> — Laravel 12 REST API'),
        ('Documentation', '<font face="Mono">docs/</font> in the frontend repository (manuals, diagrams, this document)'),
    ]))
    el.append(PageBreak())

    # ── 2. System Overview & Architecture ──
    el.append(chapter('2. System Overview & Architecture'))
    el.append(hr())
    el.append(body('ERP Electronics Store is a <b>multi-tenant SaaS platform</b> for electronics retail businesses. A platform <b>superadmin</b> registers business <b>owners</b>; each owner runs a white-label online store with their own branding, subscription plan, and resource limits. Owners manage <b>employees</b>, who operate the store — processing orders, managing customers, inventory, and support. <b>Customers</b> shop and pay via mobile money. <b>Suppliers</b> fulfil purchase orders through a dedicated portal.'))
    el.append(spacer(8))
    el.append(section('High-Level Architecture'))
    el.extend(code_block([
        '┌───────────────────────┐        ┌──────────────────────────────┐',
        '│  Vue 3 Frontend (SPA) │  HTTP  │  Laravel 12 REST API          │',
        '│  localhost:5173       │◄──────►│  localhost:8000/api           │',
        '│                       │ Bearer │                              │',
        '│  · Pinia stores       │ token  │  · Sanctum auth              │',
        '│  · Vue Router         │        │  · Eloquent ORM              │',
        '│  · Axios client       │        │  · SQLite (dev) / DB (prod)  │',
        '│  · vue-i18n (EN/SW)   │        │  · Rate limiting + scheduler │',
        '└───────────────────────┘        └──────────────────────────────┘',
    ]))
    el.append(spacer(6))
    el.append(section('Request Flow'))
    el.extend(bullet_list([
        'The SPA calls the API through an <b>Axios</b> client configured with a base URL (<font face="Mono">VITE_API_URL</font>).',
        'Authenticated requests send <b>Authorization: Bearer &lt;token&gt;</b> (Sanctum personal access token).',
        'A <b>401</b> response clears the stored token and redirects to the login page.',
        'API responses are JSON; all <font face="Mono">/api/*</font> routes render JSON errors automatically.',
        'Public storefront routes (products, categories, branding) require no authentication.',
    ]))
    el.append(spacer(6))
    el.append(section('Cross-Origin Resource Sharing (CORS)'))
    el.append(body('The API permits requests from any origin (<b>allowed_origins: *</b>), which allows the storefront SPA — running on Vite during development or Netlify in production — to consume the API without CORS configuration changes. Preflight requests are handled automatically.'))
    el.append(PageBreak())

    # ── 3. Technology Stack ──
    el.append(chapter('3. Technology Stack'))
    el.append(hr())
    el.append(section('Frontend'))
    el.append(info_table(header=['Package', 'Version', 'Purpose'], col_widths=[150, 90, 240], rows=[
        ('vue', '^3.5', 'UI framework (Composition API)'),
        ('vue-router', '^5.1', 'Client-side routing with role guards'),
        ('pinia', '^3.0', 'State management (auth, session, cart)'),
        ('pinia-plugin-persistedstate', '^4.7', 'Persist auth token to localStorage'),
        ('axios', '^1.18', 'HTTP client with interceptors'),
        ('vue-i18n', '^10.0', 'Internationalization (Swahili / English)'),
        ('@fortawesome/fontawesome-free', '^7.3', 'Icons (fas fa-*)'),
        ('chart.js + vue-chartjs', '^4.x', 'Analytics and sales charts'),
        ('vite', '^8.0', 'Build tooling and dev server'),
        ('vitest / @vue/test-utils', '^4.1 / ^2.4', 'Unit testing'),
        ('playwright', '^1.61', 'End-to-end testing'),
    ]))
    el.append(note('Node requirement: ^22.18.0 || &gt;= 24.12.0'))
    el.append(spacer(8))
    el.append(section('Backend'))
    el.append(info_table(header=['Package', 'Purpose'], col_widths=[180, 300], rows=[
        ('Laravel 12 / PHP 8.4', 'Application framework'),
        ('Laravel Sanctum', 'Token-based API authentication'),
        ('Eloquent ORM', 'Database abstraction and relationships'),
        ('SQLite (development)', 'Local database (database/database.sqlite)'),
        ('Filesystem disk', 'File storage — local in dev, S3 on Laravel Cloud'),
        ('Gemini API', 'AI-powered analytics suggestions'),
        ('Scheduler', 'Artisan scheduled tasks (daily reports, unpaid-order cleanup, superadmin password reset)'),
    ]))
    el.append(spacer(8))
    el.append(section('Documentation Tooling'))
    el.extend(bullet_list([
        '<b>Python 3 + ReportLab</b> — generates the PDF user manuals and this developer documentation.',
        '<b>DejaVu Sans</b> fonts — full Swahili character and symbol support in generated PDFs.',
        '<b>diagrams.net</b> (drawio) — ERD, class, use case, and sequence diagrams; also exported to PDF.',
    ]))
    el.append(PageBreak())

    # ── 4. Brand Identity & Visual Guidelines ──
    el.append(chapter('4. Brand Identity & Visual Guidelines'))
    el.append(hr())
    el.append(body('This section defines the official brand identity used across the storefront, dashboards, PDF manuals, and developer material. When producing any asset, use these colors, fonts, and the logo exactly as specified.'))
    el.append(spacer(8))
    el.append(section('4.1 Logo'))
    el.append(body('The logo is a <b>red rounded-corner square</b> with a <b>white lightning bolt</b>, representing electrical energy and fast service. The primary logo is defined in <font face="Mono">public/favicon.svg</font> (64 × 64 viewBox):'))
    el.append(spacer(4))
    logo_row = Table([[LogoFlowable(64, 64)], [Paragraph('Primary logo mark', make_style('lg', fontSize=8, textColor=GRAY, alignment=TA_CENTER))]], colWidths=[64])
    logo_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    el.append(logo_row)
    el.append(spacer(4))
    el.append(info_table(header=['Rule', 'Guideline'], col_widths=[150, 330], rows=[
        ('Clear space', 'Maintain padding of at least the bolt height on all sides.'),
        ('Minimum size', 'Never render below 16 × 16 px on screen.'),
        ('Backgrounds', 'Preferred on white or on the brand red square itself.'),
        ('Do not', 'Recolor the bolt, rotate the mark, add effects, or place it on low-contrast backgrounds.'),
        ('File source', 'public/favicon.svg (frontend repo).'),
    ]))
    el.append(spacer(10))
    el.append(section('4.2 Brand Color Palette'))
    el.append(body('The palette below is used consistently across the UI and all documentation. Hex values are authoritative.'))
    el.append(spacer(4))
    el.append(swatch_table([
        ('#e74c3c', 'Brand Red (primary)', 'Buttons, CTAs, active tabs, price highlights, icons, selection color, cover accents'),
        ('#2c3e50', 'Dark Slate (secondary)', 'Navigation, footer, headings, cover background, table headers'),
        ('#ffffff', 'White', 'Page background, text on brand red'),
        ('#2980b9', 'Blue', 'Informational accents, links in documents'),
        ('#27ae60', 'Green', 'Success states (valid fields, paid/confirmed status)'),
        ('#888888', 'Gray', 'Muted/secondary text, notes'),
        ('#f5f5f5', 'Light Gray', 'Table striping, subtle section backgrounds'),
        ('#dddddd', 'Border Gray', 'Grid lines, hairline dividers'),
    ]))
    el.append(spacer(6))
    el.append(section('4.3 White-Label Branding (per owner)'))
    el.append(body('Every owner can override the two core brand colors through the <b>superadmin Branding</b> panel (stored on <font face="Mono">owner_profiles</font>):'))
    el.append(info_table([
        ('brand_color', 'Primary accent color — default <b>#e74c3c</b>'),
        ('brand_color_secondary', 'Secondary color — default <b>#2c3e50</b>'),
        ('brand_store_name', 'White-label store name shown in the storefront'),
        ('brand_tagline', 'Store tagline shown in the storefront'),
    ]))
    el.append(spacer(10))
    el.append(section('4.4 Typography'))
    el.append(info_table(header=['Context', 'Typeface', 'Notes'], col_widths=[130, 170, 180], rows=[
        ('Web UI (body)', 'Inter (weights 300–800)', 'Loaded from Google Fonts; fallback -apple-system, BlinkMacSystemFont, sans-serif'),
        ('Web UI (headings)', 'Inter — SemiBold/Bold', 'Body text 14 px; page titles 28 px'),
        ('PDF documents', 'DejaVu Sans', 'Full Latin + Swahili + symbol coverage'),
        ('Code / API', 'DejaVu Sans Mono', 'Code blocks and terminal output in this document'),
    ]))
    el.append(PageBreak())

    # ── 5. System Roles & Permissions ──
    el.append(chapter('5. System Roles & Permissions'))
    el.append(hr())
    el.append(info_table(header=['Role', 'Description', 'Entry point'], col_widths=[85, 250, 145], rows=[
        ('Superadmin', 'Platform administrator. Registers owners, manages subscriptions, limits, branding, and owner passwords.', '/superadmin'),
        ('Owner', 'Business owner. Runs the store: products, employees, orders, inventory, accounting, reports, commissions.', '/owner'),
        ('Employee', 'Store staff. Processes orders, manages customers, updates delivery, answers support, views earnings.', '/employee'),
        ('Customer', 'End shopper. Browses the catalog, checks out, tracks orders, contacts support.', '/customer'),
        ('Supplier', 'External supplier. Views and fulfils the owner\'s purchase orders.', '/supplier'),
    ]))
    el.append(spacer(10))
    el.append(section('Permissions Matrix'))
    el.append(info_table(header=['Capability', 'Customer', 'Employee', 'Owner', 'Superadmin', 'Supplier'], col_widths=[200, 52, 52, 52, 64, 52], rows=[
        ('Browse products / shop', '✓', '✓', '✓', '✓', '✗'),
        ('Place and view own orders', '✓', '✓', '✓', '✗', '✗'),
        ('Process orders (all)', '✗', '✓', '✓', '✗', '✗'),
        ('Manage customers', '✗', '✓', '✓', '✗', '✗'),
        ('Manage employees', '✗', '✗', '✓', '✗', '✗'),
        ('Manage products / branches / shipping', '✗', '✗', '✓', '✗', '✗'),
        ('Accounting & financial reports', '✗', '✗', '✓', '✗', '✗'),
        ('Commissions & inventory', '✗', '✓ (earnings only)', '✓', '✗', '✗'),
        ('Manage owners (CRUD)', '✗', '✗', '✗', '✓', '✗'),
        ('Subscriptions, limits, branding', '✗', '✗', '✗', '✓', '✗'),
        ('Reset owner passwords / unlock', '✗', '✗', '✗', '✓', '✗'),
        ('Supplier portal (view / update POs)', '✗', '✗', '✗', '✗', '✓'),
    ]))
    el.append(PageBreak())

    # ── 6. Database Schema & Models ──
    el.append(chapter('6. Database Schema & Models'))
    el.append(hr())
    el.append(body('The database consists of <b>30 tables</b>. A full entity-relationship diagram is available as <b>ERD.drawio</b> (crow\'s foot notation, 35+ relationships).'))
    el.append(spacer(8))
    el.append(section('Tables by Domain'))
    el.append(info_table(header=['Domain', 'Tables'], col_widths=[130, 350], rows=[
        ('Identity', 'users, customer_profiles, employee_profiles, owner_profiles'),
        ('Catalog', 'categories, products, product_variants, inventory'),
        ('Commerce', 'addresses, branches, orders, order_items, payments, payment_providers, shipping_rules'),
        ('Support', 'support_messages, conversations, conversation_messages'),
        ('Accounting', 'accounts, journal_entries, journal_lines, accounting_reports'),
        ('Operations', 'commissions, wingas, winga_commissions, inventory_transactions, purchase_orders, purchase_order_items, suppliers, stock_alerts'),
        ('Notifications', 'notifications'),
    ]))
    el.append(spacer(8))
    el.append(section('Key Models & Relationships'))
    el.extend(bullet_list([
        '<b>User</b> (polymorphic) — one <b>customer_profile</b>, <b>employee_profile</b>, or <b>owner_profile</b>; role gates access via middleware.',
        '<b>employee_profile</b> — branch_id, position, department, commission_rate, hire_date, employee_code; has many <b>employee_guarantors</b> (Wadhamini) and many <b>employee_documents</b> (contracts, background checks).',
        '<b>Product</b> — belongs to a <b>category</b>; has many <b>product_variants</b> and <b>inventory</b> records.',
        '<b>Order</b> — belongs to a <b>user</b> and optional <b>branch</b>; has many <b>order_items</b>, a <b>payment</b>, and a delivery/tracking payload. Orders placed with a street promoter store <b>winga_id</b> and the <b>winga_fee</b> added at checkout.',
        '<b>Winga</b> — a street promoter (name, phone, TIN/NIDA, commission_rate, optional branch); has many <b>winga_commissions</b>.',
        '<b>WingaCommission</b> — created per winga per paid order with <b>commission_amount</b> (gross), <b>withholding_tax</b> (TRA TDS 5%), and <b>net_amount</b>; paid individually or in bulk, posting a payout journal (Dr 2100 / Cr 1020 / Cr 2120).',
        '<b>Accounting</b> — <b>accounts</b> form a chart of accounts; <b>journal_entries</b> contain <b>journal_lines</b> (double-entry). Payments and cancellations create journals automatically.',
        '<b>Commissions</b> — created per employee per paid order; paid individually or in bulk by the owner.',
        '<b>Purchase orders</b> — link <b>suppliers</b> and <b>purchase_order_items</b>; receiving stock creates inventory transactions and journals.',
        '<b>Conversations</b> — owner ↔ superadmin, owner ↔ customer, and owner ↔ employee messaging with real-time unread badges.',
    ]))
    el.append(PageBreak())

    # ── 7. Authentication & Authorization ──
    el.append(chapter('7. Authentication & Authorization'))
    el.append(hr())
    el.append(section('Token Flow'))
    el.extend(code_block([
        '1. POST /api/auth/login        →  { email, password }',
        '2. Backend validates credentials and returns:',
        '   { token, user, must_change_password, superadmin_password_expired }',
        '3. Frontend stores the token in localStorage (key: auth_token)',
        '4. Every request sends:  Authorization: Bearer <token>',
        '5. A 401 response clears the token and redirects to /login',
    ]))
    el.append(spacer(6))
    el.append(section('Password Policy'))
    el.extend(bullet_list([
        'Minimum <b>8 characters</b> with at least one uppercase, one lowercase, one number, and one special character.',
        'Enforced on both the frontend (real-time rules) and the backend (custom validation messages).',
        '<b>Password expiry</b>: <font face="Mono">password_changed_at</font> must be newer than <b>3 days</b>, otherwise a forced change modal appears on login.',
    ]))
    el.append(spacer(6))
    el.append(section('Default Passwords'))
    el.append(info_table([
        ('Employee', 'Full name in capitals — e.g. "MATHEW ZACHARIA"; owner can reset anytime'),
        ('Owner (created by superadmin)', 'Full name in capitals — e.g. "JOHN DOE"; forced change on first login'),
        ('Superadmin', 'SuperAdmin@2026 — auto-reset every 6 months via scheduled artisan command'),
    ]))
    el.append(spacer(6))
    el.append(section('Account Lockout'))
    el.append(body('After <b>5 failed login attempts</b> the account locks for <b>30 minutes</b> (<font face="Mono">users.locked_until</font>). The API returns HTTP <b>423</b> with a remaining-minutes message; the login form also reports remaining attempts.'))
    el.append(PageBreak())

    # ── 8. API Reference ──
    el.append(chapter('8. API Reference'))
    el.append(hr())
    el.append(body('All endpoints are JSON and mounted under the <font face="Mono">/api</font> prefix. Base URLs — development: <font face="Mono">http://localhost:8000/api</font>; production: <font face="Mono">https://erp-electronics-api-production-iqx4tl.laravel.cloud/api</font>.'))
    el.append(spacer(8))
    el.append(section('Public Endpoints'))
    el.append(info_table(header=['Method', 'Route', 'Notes'], col_widths=[60, 260, 160], rows=[
        ('POST', '/auth/register', 'Customer signup (throttled)'),
        ('POST', '/auth/login', 'Login (throttled)'),
        ('GET', '/products', 'List products'),
        ('GET', '/products/featured', 'Featured products'),
        ('GET', '/products/{slug}', 'Product detail'),
        ('GET', '/categories', 'List categories'),
        ('GET', '/categories/{slug}', 'Category with products'),
        ('GET', '/payment-providers', 'Enabled providers'),
        ('POST', '/payments/webhook', 'Payment webhook'),
        ('POST', '/shipping/calculate', 'Shipping cost estimate'),
        ('GET', '/settings/payment', 'Public payment settings'),
        ('GET', '/settings/branding', 'Active owner branding'),
    ]))
    el.append(spacer(8))
    el.append(section('Authenticated Endpoints (Bearer token)'))
    el.append(info_table(header=['Group', 'Key routes', 'Access'], col_widths=[150, 260, 70], rows=[
        ('Auth', '/auth/logout, /auth/profile (GET/PUT), /auth/change-password', 'any'),
        ('Employees', '/employees (GET/POST/PUT), /employees/{user}/toggle-status, /assign-branch, /reset-password, /documents (CRUD + download)', 'owner'),
        ('Branches', '/branches CRUD + set-default', 'owner'),
        ('Customers', '/customers (GET/PATCH/DELETE)', 'employee, owner'),
        ('Products (manage)', '/products-manage, /products CRUD', 'owner'),
        ('Cart / Orders', '/cart, /orders, /orders/{id}/status, /delivery, /return', 'any / employee, owner'),
        ('Accounting', '/accounts, /journal-entries, /reports/trial-balance, /profit-loss, /balance-sheet, /general-ledger', 'owner'),
        ('Reports', '/reports/daily, /reports/summary', 'employee, owner'),
        ('Commissions', '/commissions, /commissions/summary, /commissions/{id}/pay, /pay-all, /my-earnings', 'owner / employee'),
        ('Wingas', '/wingas CRUD + toggle-status, /winga-commissions, /winga-commissions/summary, /winga-commissions/{id}/pay, /pay-all', 'owner / employee'),
        ('Inventory', '/inventory (index, adjust, transactions, low-stock, dashboard)', 'owner'),
        ('Purchase orders', '/purchase-orders CRUD + receive', 'owner'),
        ('Suppliers', '/suppliers CRUD + portal', 'owner / supplier'),
        ('Superadmin', '/superadmin/stats, /owners CRUD, /owners/{id}/branding, /passwords/status, /owners/{id}/reset-password, /unlock-account', 'superadmin'),
    ]))
    el.append(spacer(8))
    el.append(section('Rate Limits'))
    el.append(info_table(header=['Limiter', 'Limit', 'Keyed by'], col_widths=[110, 210, 160], rows=[
        ('api (global)', '120 requests per minute', 'Authenticated user ID, else IP'),
        ('login', '5 requests per minute', 'IP address'),
        ('register', '3 per minute and 10 per day', 'IP address'),
    ]))
    el.append(note('Exceeded limits return HTTP 429 with X-RateLimit-Remaining / X-RateLimit-Reset headers.'))
    el.append(PageBreak())

    # ── 9. Superadmin Module ──
    el.append(chapter('9. Superadmin Module'))
    el.append(hr())
    el.append(body('The <b>superadmin</b> is the platform administrator responsible for onboarding and managing business owners. Access the panel at <font face="Mono">/superadmin</font> (role-guarded). This module is fully documented here for administrators and developers; it is intentionally <b>not</b> described in the end-user manuals.'))
    el.append(spacer(8))
    el.append(section('9.1 System Overview'))
    el.extend(bullet_list([
        '<b>System Statistics</b> — total customers, total orders, total revenue, and active owners at a glance.',
        '<b>Owners Table</b> — all registered owners with company name, plan, status, and registration date.',
    ]))
    el.append(spacer(6))
    el.append(section('9.2 Managing Owners'))
    el.extend(bullet_list([
        '<b>Create Owner</b> — registers an owner with name, email, phone, and company name. Default password is the full name in capitals; the response exposes <font face="Mono">default_password</font> to share securely.',
        '<b>Toggle Active/Inactive</b> — enable or disable an owner\'s account instantly.',
        '<b>Delete Owner</b> — removes the owner and all associated data.',
    ]))
    el.append(spacer(6))
    el.append(section('9.3 Owner Details'))
    el.append(body('Opening an owner reveals:'))
    el.extend(bullet_list([
        '<b>Subscription</b> — plan (Starter, Professional, Enterprise), status, and expiry date.',
        '<b>Limits</b> — maximum products and employees the owner may register.',
        '<b>Branding</b> — white-label configuration: store name, tagline, logo upload, and the two brand colors (see §4.3).',
    ]))
    el.append(spacer(6))
    el.append(section('9.4 Owner Password Management'))
    el.extend(bullet_list([
        '<b>Reset Password</b> — resets to the default (full name in capitals) and forces a change on next login.',
        '<b>Set Password</b> — assigns an explicit password.',
        '<b>Force Password Change</b> — clears <font face="Mono">password_changed_at</font> so the owner must change it.',
        '<b>Unlock Account</b> — clears <font face="Mono">locked_until</font> after a 30-minute lockout.',
        '<b>Passwords Status</b> — overview of every owner\'s password state (changed / needs change / expired).',
    ]))
    el.append(spacer(6))
    el.append(section('9.5 Superadmin Inbox'))
    el.append(body('The superadmin communicates with owners through the <b>Inbox</b> (owner ↔ superadmin conversations). Conversations appear in real time with unread badges.'))
    el.append(spacer(6))
    el.append(section('9.6 Superadmin Password Lifecycle'))
    el.append(body('The default superadmin password is <b>SuperAdmin@2026</b>. A scheduled command (<font face="Mono">php artisan superadmin:reset-password</font>) auto-resets it every <b>6 months</b>; login and profile responses expose <font face="Mono">superadmin_password_expired</font> so the UI can prompt for a change.'))
    el.append(PageBreak())

    # ── 10. Security Measures ──
    el.append(chapter('10. Security Measures'))
    el.append(hr())
    el.append(section('10.1 API Rate Limiting'))
    el.append(body('Laravel\'s named rate limiters protect every API route. The <b>api</b> group limiter is attached to the whole <font face="Mono">/api/*</font> group; the <b>login</b> and <b>register</b> limiters sit on the public auth routes.'))
    el.extend(code_block([
        "// app/Providers/AppServiceProvider.php",
        "RateLimiter::for('api', fn (Request $r) =>",
        "    Limit::perMinute(120)->by($r->user()?->id ?: $r->ip()));",
        "RateLimiter::for('login', fn (Request $r) => Limit::perMinute(5)->by($r->ip()));",
        "RateLimiter::for('register', fn (Request $r) => [",
        "    Limit::perMinute(3)->by($r->ip()),",
        "    Limit::perDay(10)->by($r->ip()),",
        "]);",
    ]))
    el.append(note('Registered with $middleware->throttleApi() in bootstrap/app.php and throttle:login / throttle:register on the auth routes.'))
    el.append(spacer(6))
    el.append(section('10.2 Session Termination (Idle Timeout)'))
    el.append(body('The frontend <b>session store</b> (<font face="Mono">src/stores/session.js</font>) enforces automatic logout:'))
    el.extend(bullet_list([
        '<b>15 minutes</b> of inactivity → session ends (mouse, keyboard, touch, scroll, and click activity reset the timer).',
        'At <b>14 minutes</b> a warning modal shows a <b>60-second countdown</b>; any activity dismisses it.',
        '<b>Leaving the dashboard</b> — switching tabs/apps pauses the timer; returning within <b>10 minutes</b> continues the session, otherwise the user is signed out.',
        'A <font face="Mono">session_last_active</font> timestamp is persisted, so returning to a closed tab after the idle window forces logout on load.',
        'Logout clears <font face="Mono">auth_token</font> from localStorage and revokes the Sanctum token on the server.',
    ]))
    el.append(spacer(6))
    el.append(section('10.3 Passwords & Lockout'))
    el.extend(bullet_list([
        'Complexity enforced at the API level (8+ chars; upper, lower, number, symbol).',
        'Accounts lock after <b>5 failed attempts</b> for <b>30 minutes</b>.',
        'Passwords older than <b>3 days</b> trigger a mandatory change; superadmin password resets every 6 months.',
    ]))
    el.append(spacer(6))
    el.append(section('10.4 File Uploads'))
    el.extend(bullet_list([
        'Employee documents accept only <b>PDF, JPG, PNG, DOC, DOCX</b>, up to <b>20 MB</b> each.',
        'Files are stored on the configured filesystem disk under <font face="Mono">employee-documents/</font> (local in development; S3 on Laravel Cloud).',
        'Downloads are served only through the authenticated owner endpoints.',
    ]))
    el.append(PageBreak())

    # ── 11. Analytics & AI Insights ──
    el.append(chapter('11. Analytics & AI Insights'))
    el.append(hr())
    el.append(section('Sales Analytics'))
    el.append(body('<font face="Mono">AnalyticsController::sales()</font> accepts <font face="Mono">?months=12</font> and computes, in parallel: monthly sales, monthly items sold, monthly profit, and monthly cancellations. It returns a gap-free month list plus <b>category_breakdown</b>, <b>top_products</b>, and a <b>summary</b> (total revenue, profit, orders, items sold, average order value, profit margin, revenue and order growth).'))
    el.append(spacer(6))
    el.append(section('AI Suggestions'))
    el.append(body('The owner dashboard can call <font face="Mono">POST /analytics/ai-suggestions</font> with the sales payload. The backend builds a Tanzania-specific business prompt and calls <b>Gemini 2.0 Flash</b> (temperature 0.7, max 2048 tokens, configured via <font face="Mono">GEMINI_API_KEY</font>). If the AI response is unavailable, rule-based fallback suggestions are returned.'))
    el.append(body('Suggestions are bilingual (<font face="Mono">title_sw/title_en</font>, <font face="Mono">description_sw/description_en</font>) with a priority (high/medium/low), category (inventory/pricing/marketing/growth/operations), expected impact, and a <font face="Mono">source</font> of "ai" or "fallback".'))
    el.append(PageBreak())

    # ── 12. Documentation & Diagrams ──
    el.append(chapter('12. Documentation & Diagrams'))
    el.append(hr())
    el.append(section('PDF Documents'))
    el.append(info_table(header=['File', 'Audience', 'Notes'], col_widths=[180, 120, 180], rows=[
        ('User_Manual_EN.pdf', 'End users', 'English user manual, 24 chapters (v3.0)'),
        ('User_Manual_SW.pdf', 'End users', 'Swahili user manual, 24 chapters (v3.0)'),
        ('Developer_Documentation.pdf', 'Developers & admins', 'This document (v1.0)'),
    ]))
    el.append(spacer(8))
    el.append(section('System Diagrams (docs/)'))
    el.append(info_table(header=['Diagram', 'Contents'], col_widths=[150, 330], rows=[
        ('ERD.drawio (+ PDF)', '28 tables, 35+ relationships, crow\'s foot notation'),
        ('ClassDiagram.drawio (+ PDF)', '28 model classes with attributes, methods, and relationships'),
        ('UseCase.drawio (+ PDF)', '6 actors, 45+ use cases, include/extend relationships'),
        ('SequenceDiagrams.drawio (+ PDF)', '7 flows: customer checkout, order processing, branch + employee management, accounting, commission, inventory, purchase orders'),
    ]))
    el.append(spacer(8))
    el.append(section('Generator Scripts'))
    el.extend(bullet_list([
        '<font face="Mono">generate_manual.py</font> — user manuals (EN + SW) using ReportLab.',
        '<font face="Mono">generate_dev_doc.py</font> — this developer documentation.',
    ]))
    el.append(PageBreak())

    # ── 13. Development Commands & Environment ──
    el.append(chapter('13. Development Commands & Environment'))
    el.append(hr())
    el.append(section('Frontend (erp-electronics/)'))
    el.append(info_table(header=['Command', 'Purpose'], col_widths=[240, 240], rows=[
        ('npm run dev', 'Start Vite dev server (port 5173)'),
        ('npm run build', 'Production build'),
        ('npm run lint', 'Run oxlint + eslint'),
        ('npm run format', 'Format with oxfmt'),
        ('npm run test:unit', 'Run Vitest unit tests'),
        ('npm run test:e2e', 'Run Playwright end-to-end tests'),
    ]))
    el.append(spacer(8))
    el.append(section('Backend (erp-electronics-api/)'))
    el.append(info_table(header=['Command', 'Purpose'], col_widths=[280, 200], rows=[
        ('php artisan serve', 'Start dev server (port 8000)'),
        ('php artisan migrate', 'Run migrations'),
        ('php artisan migrate:fresh --seed', 'Reset database and re-seed'),
        ('php artisan report:daily', 'Generate daily report'),
        ('php artisan orders:cleanup-unpaid', 'Clean up unpaid orders'),
        ('php artisan superadmin:reset-password', 'Reset superadmin password if 6 months elapsed'),
        ('php artisan schedule:work', 'Run the scheduler'),
        ('php artisan route:list', 'List routes'),
        ('php artisan test', 'Run the test suite'),
    ]))
    el.append(spacer(8))
    el.append(section('Environment Variables'))
    el.extend(code_block([
        '# Frontend (.env)',
        'VITE_API_URL=http://localhost:8000/api',
        '',
        '# Backend (.env)',
        'DB_CONNECTION=sqlite',
        'DB_DATABASE=/absolute/path/to/database.sqlite',
        'GEMINI_API_KEY=your-gemini-api-key',
        'FILESYSTEM_DISK=local        # "s3" on Laravel Cloud',
        'AWS_ACCESS_KEY_ID=           # when using S3',
        'AWS_SECRET_ACCESS_KEY=',
        'AWS_DEFAULT_REGION=us-east-1',
        'AWS_BUCKET=',
        'AWS_USE_PATH_STYLE_ENDPOINT=false',
    ]))
    el.append(PageBreak())

    # ── 14. Deployment ──
    el.append(chapter('14. Deployment'))
    el.append(hr())
    el.append(section('14.1 Backend — Laravel Cloud'))
    el.extend(bullet_list([
        'Pushing to the <b>main</b> branch triggers an automatic deployment.',
        'Production environment id: <font face="Mono">env-a2578b2b-6a5c-4d19-9c2e-d927b4edafde</font>; app id: <font face="Mono">app-a2578b29-e3ec-4754-a717-a6a208f4f512</font>.',
        'Deployment verification: <font face="Mono">cloud command:run &lt;env-id&gt; --cmd="php artisan test" -n</font>.',
        'Health check: <font face="Mono">GET /up</font> on the production domain.',
    ]))
    el.append(spacer(6))
    el.append(section('14.2 Frontend — Netlify'))
    el.extend(bullet_list([
        'Set <font face="Mono">VITE_API_URL=https://erp-electronics-api-production-iqx4tl.laravel.cloud/api</font> as a build-time environment variable.',
        'Build command <font face="Mono">npm run build</font>; publish directory <font face="Mono">dist</font>; enable SPA redirects to index.html.',
        'The API accepts the Netlify origin via CORS (<b>allowed_origins: *</b>).',
    ]))
    el.append(spacer(6))
    el.append(note('Rate-limit keys are IP-based, so an entire office sharing one public IP shares the 5/min login budget. This is intentional to block brute-force traffic.'))
    el.append(PageBreak())

    # ── 15. Full Business Cycle ──
    el.append(chapter('15. Full Business Cycle'))
    el.append(hr())
    el.append(section('Customer Journey'))
    el.extend(code_block([
        'Browse → Add to cart (variant, quantity) → Checkout (delivery + payment)',
        '  → Order created (pending_payment)',
        '  → Paid (cash/ClickPesa auto; mobile money confirmed by employee)',
        '  → Auto-journal (Revenue + COGS), inventory decremented, commission created',
        '  → Processing → Shipped (tracking) → Delivered',
        '  → Cancel at any stage: reversal journals, stock restored, commission deleted',
    ]))
    el.append(spacer(6))
    el.append(section('Employee Flow'))
    el.extend(bullet_list([
        'Login → dashboard with stats and quick actions.',
        'Confirm payment (type name) → order to paid → process → ship → deliver.',
        'View earnings at /employee/earnings; handle stock alerts and support.',
    ]))
    el.append(spacer(6))
    el.append(section('Owner Flow'))
    el.extend(bullet_list([
        'Dashboard → products → employees (guarantors + documents + commission rate) → orders.',
        'Inventory, suppliers, purchase orders, commissions, accounting, stock alerts, branches.',
        'Reports & analytics with AI suggestions; owner inbox for customer and administrator conversations.',
    ]))
    el.append(spacer(6))
    el.append(section('Auto-Journal Chain'))
    el.extend(code_block([
        'Customer pays TSh 500,000',
        '  → DR Accounts Receivable 500,000 / CR Sales Revenue 500,000',
        '  → DR Cost of Goods Sold 300,000 / CR Inventory 300,000',
        '  → inventory transactions, stock alerts, commission = profit × rate',
        'Order cancelled',
        '  → DR Sales Revenue 500,000 / CR Accounts Receivable 500,000',
        '  → DR Inventory 300,000 / CR Cost of Goods Sold 300,000',
        'Owner pays commission',
        '  → DR Commission Expense / CR Cash',
    ]))
    el.append(spacer(12))
    el.append(hr())
    el.append(Paragraph('<b>ERP Electronics Store</b> — Developer &amp; Technical Documentation v1.0 — July 2026', sFooter))
    el.append(Paragraph('For internal development and administration use only.', sFooter))

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
    build_pdf(build(), 'Developer_Documentation.pdf')
    print('Done!')
