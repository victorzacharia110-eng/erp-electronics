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
        [Paragraph('Developer &amp; Technical Documentation', sSubtitle)],
        [Spacer(1, 30)],
        [HRFlowable(width="55%", thickness=2, color=RED, spaceBefore=4, spaceAfter=4)],
        [Spacer(1, 14)],
        [Paragraph('Version 2.3 &nbsp;|&nbsp; August 2026', sCoverMeta)],
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
    canvas.drawCentredString(A4[0] / 2, 20 * mm, f'ERP Electronics Store — Developer Documentation v2.3  ·  Page {doc.page}')
    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
#  ENVIRONMENTS
# ══════════════════════════════════════════════════════════════════════════════

DEV_FE = 'http://localhost:5173'
DEV_API = 'http://localhost:8000/api'
PROD_FE = 'https://electroshophub.online'
PROD_API = 'https://api.electroshophub.online/api'


def mono(text):
    return f'<font face="Mono">{text}</font>'


# ══════════════════════════════════════════════════════════════════════════════
#  CONTENT — CHAPTER BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def ch_document_control():
    el = []
    el.append(chapter('1. Document Control'))
    el.append(hr())
    el.append(info_table([
        ('Version', '2.3'),
        ('Date', 'August 2026'),
        ('Status', 'Released'),
        ('Audience', 'Software developers, system administrators, superadmins, and technical stakeholders'),
        ('Scope', 'Every file in both repositories, the full request cycle, architecture, security, deployment, and local-to-production workflow'),
        ('Related documents', 'User_Manual_EN.pdf, User_Manual_SW.pdf, Supplier_Manual.pdf, ERD.drawio, ClassDiagram.drawio, UseCase.drawio, SequenceDiagrams.drawio'),
    ]))
    el.append(spacer(10))
    el.append(section('Repositories'))
    el.append(info_table([
        ('Frontend', mono('erp-electronics/') + ' — Vue 3 SPA (storefront + dashboards + superadmin panel); this document and all PDF generators live here.'),
        ('Backend', mono('erp-electronics-api/') + ' — Laravel 13 REST API.'),
        ('Documentation', mono('docs/') + ' in the frontend repository (manuals, diagrams, this document).'),
    ]))
    el.append(spacer(10))
    el.append(section('Environments'))
    el.append(info_table(header=['Environment', 'Frontend', 'Backend API base'], col_widths=[100, 190, 190], rows=[
        ('Local development', mono(DEV_FE), mono(DEV_API)),
        ('Production (live)', mono(PROD_FE), mono(PROD_API)),
    ]))
    el.append(note('The local frontend talks to the local backend. The production build is compiled with VITE_API_URL set to the production API base; the local untracked .env keeps the localhost value, so development and deployment do not interfere.'))
    el.append(PageBreak())
    return el


def ch_overview():
    el = []
    el.append(chapter('2. System Overview & Architecture'))
    el.append(hr())
    el.append(body('ERP Electronics Store is a <b>multi-tenant SaaS platform</b> for electronics retail businesses in Tanzania. A platform <b>superadmin</b> registers business <b>owners</b>; each owner runs a white-label online store with their own branding, subscription plan, and resource limits. Owners manage <b>employees</b>, who operate the store — processing orders, managing customers, inventory, and support. <b>Customers</b> shop and pay via mobile money (M-Pesa, Airtel Money, Mixx by Yas, Halopesa, ClickPesa) or cash. <b>Suppliers</b> fulfil purchase orders through a dedicated portal. <b>Winga</b> street promoters drive orders from a per-order commission.'))
    el.append(spacer(8))
    el.append(section('High-Level Architecture'))
    el.extend(code_block([
        '┌────────────────────────┐        ┌───────────────────────────────┐',
        '│  Vue 3 Frontend (SPA)  │  HTTP  │  Laravel 13 REST API           │',
        '│  electroshophub.online │◄──────►│  api.electroshophub.online/api │',
        '│  (local: :5173)        │ Bearer │  (local: localhost:8000/api)   │',
        '│                        │ token  │                               │',
        '│  · Pinia stores        │        │  · Sanctum auth               │',
        '│  · Vue Router + guards │        │  · Eloquent ORM               │',
        '│  · Axios client        │        │  · SQLite (dev) / DB (prod)   │',
        '│  · vue-i18n (SW/EN)    │        │  · Rate limiting + scheduler  │',
        '└────────────────────────┘        └───────────────────────────────┘',
    ]))
    el.append(spacer(6))
    el.append(section('Multi-Tenancy Model'))
    el.extend(bullet_list([
        'The tenant key is the <b>owner user id</b>. Every owner-scoped row (products, orders, accounts, commissions, suppliers, wingas, branches, businesses) carries an <b>owner_id</b> foreign key.',
        '<b>Businesses</b> (multi-store) sit above the owner: a <b>Business</b> row is seeded per owner and can be shared with <b>co-owners</b> via the <font face="Mono">business_user</font> pivot.',
        'Tenant resolution is centralized in <font face="Mono">app/Support/Tenant.php</font> and exposed as request macros <font face="Mono">request()->business()</font> and <font face="Mono">request()->ownerId()</font>.',
        'The active business is selected by the <font face="Mono">X-Business-Id</font> request header (sent by the frontend from <font face="Mono">active_business_id</font> in localStorage), falling back to the first owned business.',
        'Storefront routes scope by a business <b>slug</b> in the URL — e.g. <font face="Mono">/:businessSlug</font> renders that store\'s branding and catalog.',
    ]))
    el.append(spacer(6))
    el.append(section('Request Flow'))
    el.extend(bullet_list([
        'The SPA calls the API through an <b>Axios</b> client configured with a base URL (<font face="Mono">VITE_API_URL</font>).',
        'Authenticated requests send <b>Authorization: Bearer &lt;token&gt;</b> (Sanctum personal access token) and <b>X-Business-Id</b>.',
        'A <b>401</b> response clears the stored token and redirects to the login page.',
        'API responses are JSON; all <font face="Mono">/api/*</font> routes render JSON errors automatically (<font face="Mono">shouldRenderJsonWhen api/*</font>).',
        'Public storefront routes (products, categories, businesses, branding, payment providers, shipping estimate) require no authentication.',
    ]))
    el.append(spacer(6))
    el.append(section('Cross-Origin Resource Sharing (CORS)'))
    el.append(body('The API permits requests from any origin (<b>allowed_origins: *</b>), which allows both the local Vite server and the production domain to consume the API without CORS configuration changes. Preflight requests are handled automatically.'))
    el.append(PageBreak())
    return el


def ch_stack():
    el = []
    el.append(chapter('3. Technology Stack'))
    el.append(hr())
    el.append(section('Frontend'))
    el.append(info_table(header=['Package', 'Version', 'Purpose'], col_widths=[150, 90, 240], rows=[
        ('vue', '^3.5', 'UI framework (Composition API)'),
        ('vue-router', '^5.1', 'Client-side routing with role guards'),
        ('pinia', '^3.0', 'State management (auth, business, cart, products, session)'),
        ('pinia-plugin-persistedstate', '^4.7', 'Persist the auth token to localStorage'),
        ('axios', '^1.18', 'HTTP client with auth/business interceptors'),
        ('vue-i18n', '^10.0', 'Internationalization (Swahili default, English fallback)'),
        ('@fortawesome/fontawesome-free', '^7.3', 'Icons (fas fa-*)'),
        ('chart.js + vue-chartjs', '^4.5 / ^5.3', 'Analytics and sales charts'),
        ('vite', '^8.0', 'Build tooling and dev server'),
        ('vitest / @vue/test-utils', '^4.1 / ^2.4', 'Unit testing'),
        ('playwright', '^1.61', 'End-to-end testing'),
        ('oxlint / oxfmt / eslint', '—', 'Linting and formatting'),
    ]))
    el.append(note('Node requirement: engines field in package.json — ^22.18.0 || >= 24.12.0'))
    el.append(spacer(8))
    el.append(section('Backend'))
    el.append(info_table(header=['Package', 'Purpose'], col_widths=[180, 300], rows=[
        ('Laravel 13 (^13.8) / PHP ^8.3', 'Application framework'),
        ('Laravel Sanctum', 'Token-based API authentication'),
        ('Eloquent ORM', 'Database abstraction and relationships'),
        ('SQLite (development)', 'Local database (database/database.sqlite)'),
        ('MySQL (production alternative)', 'Configured in config/database.php'),
        ('Gemini API', 'AI-powered analytics and accounting suggestions (gemini-2.0-flash)'),
        ('Flysystem S3', 'Production file storage on Laravel Cloud'),
        ('Scheduler', 'Artisan scheduled tasks (daily reports, order cleanup, superadmin password reset, monthly/year-end accounting)'),
    ]))
    el.append(spacer(8))
    el.append(section('Documentation Tooling'))
    el.extend(bullet_list([
        '<b>Python 3 + ReportLab</b> — generates the PDF user manuals and this developer documentation.',
        '<b>DejaVu Sans</b> fonts — full Swahili character and symbol support in generated PDFs.',
        '<b>diagrams.net</b> (drawio) — ERD, class, use case, and sequence diagrams; also exported to PDF.',
    ]))
    el.append(PageBreak())
    return el


def ch_repo_layout():
    el = []
    el.append(chapter('4. Repository Layout'))
    el.append(hr())
    el.append(section('Frontend — erp-electronics/'))
    el.extend(code_block([
        'erp-electronics/',
        '├── generate_dev_doc.py          # this document generator',
        '├── generate_manual.py           # EN + SW user manuals',
        '├── generate_supplier_manual.py  # supplier portal manual',
        '├── generate_diagrams.py         # drawio diagram generator',
        '├── docs/                        # generated PDFs + drawio sources',
        '├── public/                      # favicon.svg, index.html, assets',
        '└── src/',
        '    ├── api/                     # axios.js + index.js (API barrel)',
        '    ├── components/              # shared Vue components',
        '    ├── composables/             # useTablePagination.js',
        '    ├── layouts/                 # StoreLayout, SuperadminLayout, StoreFooter',
        '    ├── locales/                 # i18n.js, sw.json, en.json',
        '    ├── pages/                   # 53 pages across 13 areas',
        '    ├── router/                  # routes + navigation guard',
        '    ├── stores/                  # auth, business, cart, products, session',
        '    ├── utils/                   # image.js',
        '    ├── App.vue, main.js',
        '    └── __tests__/               # unit tests',
    ]))
    el.append(spacer(6))
    el.append(section('Backend — erp-electronics-api/'))
    el.extend(code_block([
        'erp-electronics-api/',
        '├── app/',
        '│   ├── Console/Commands/        # 5 artisan commands',
        '│   ├── Exceptions/              # AccountingException',
        '│   ├── Http/Controllers/Api/    # 31 controllers',
        '│   ├── Http/Middleware/         # Owner, Superadmin, Supplier',
        '│   ├── Models/                  # 38 Eloquent models',
        '│   ├── Providers/               # AppServiceProvider (macros + limiters)',
        '│   ├── Services/                # AccountingEntryService, AccountingReportService, AiSuggestionService',
        '│   └── Support/                 # Tenant.php (multi-tenancy resolver)',
        '├── bootstrap/                   # app.php (middleware/aliases), providers.php',
        '├── config/                      # app, auth, database, filesystems, sanctum, services…',
        '├── database/',
        '│   ├── factories/UserFactory.php',
        '│   ├── migrations/              # 56 migrations',
        '│   └── seeders/                 # DatabaseSeeder, SuperadminSeeder, AccountingSeeder',
        '├── routes/                      # api.php (175 routes), web.php, console.php',
        '└── tests/                       # Feature + Unit tests',
    ]))
    el.append(PageBreak())
    return el


def ch_frontend():
    el = []
    el.append(chapter('5. Frontend Deep Dive — Every File'))
    el.append(hr())
    el.append(body('This chapter documents the purpose and behaviour of every source file in <font face="Mono">erp-electronics/</font>. The stack is Vue 3 (Composition API) with Pinia, Vue Router, Axios, and vue-i18n. Paths are relative to the repository root.'))
    el.append(spacer(8))

    el.append(section('5.1 Application Bootstrap'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/main.js'), 'Application entry point. Creates the Vue app, registers Pinia (with the persistedstate plugin), the router, and i18n. Installs a global helper <font face="Mono">$storeLink</font> that routes links through the business store (slug-aware). Mounts #app.'),
        (mono('src/App.vue'), 'Root component: renders <font face="Mono">&lt;router-view/&gt;</font> plus the session warning modal. Watches the auth token to start/stop the idle-session timer. Hosts global CSS (Inter font, .btn, .card, .container, form styles, selection color).'),
        (mono('src/api/axios.js'), 'Single Axios instance. Base URL from <font face="Mono">VITE_API_URL</font> (default localhost:8000/api). Request interceptor injects the Bearer token and the X-Business-Id header. Response interceptor clears the token and redirects to /login on any 401.'),
        (mono('src/api/index.js'), 'The API barrel — 38 typed modules (authApi, employeeApi, branchApi, …) that map one-to-one to backend routes. Every page imports its endpoints from here; see §9 for the route mapping.'),
        (mono('src/locales/i18n.js'), 'Creates the vue-i18n instance (legacy: false). Locale is read from localStorage (key <font face="Mono">locale</font>), defaulting to <b>sw</b> with <b>en</b> as fallback.'),
        (mono('src/locales/sw.json'), 'Swahili message catalog (hundreds of keys across nav, pages, forms, validation).'),
        (mono('src/locales/en.json'), 'English message catalog; mirror of sw.json keys.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.2 Router'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/router/index.js'), 'Client-side router (createWebHistory). Three top-level areas: the storefront at <font face="Mono">/</font> and at <font face="Mono">/:businessSlug</font> (white-label store), the auth pages, and the superadmin panel at <font face="Mono">/superadmin</font>. A global beforeEach guard enforces meta flags: requiresAuth (redirect to /login with redirect query), guest (redirect away from login/register when logged in), and role (fetches the profile if needed and redirects to the user\'s dashboard when the role does not match).'),
    ]))
    el.append(spacer(8))

    el.append(section('5.3 Pinia Stores'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/stores/auth.js'), 'Identity + token. Holds user, token (persisted to localStorage <font face="Mono">auth_token</font>), and mustChangePassword. Actions: register, login, logout, fetchProfile, updateProfile, changePassword. Role helper computed properties (isCustomer/isEmployee/isOwner/isSuperadmin).'),
        (mono('src/stores/business.js'), 'Multi-store context. Holds directory (public business list), mine (owned + co-owned), current business, and slugMode. Persists <font face="Mono">active_business_id</font> so the Axios interceptor can send X-Business-Id. Provides link() to prefix storefront routes with the active slug.'),
        (mono('src/stores/cart.js'), 'Cart state. items, itemCount, subtotal, and a local total that adds a 5000 TSh default shipping constant. Actions fetch/add/update/remove/clear the cart via the API; $reset on logout.'),
        (mono('src/stores/products.js'), 'Catalog state: products, featuredProducts, categories, currentProduct, currentCategory, pagination. All fetches append ?business=&lt;slug&gt; when a business is active (businessParams).'),
        (mono('src/stores/session.js'), 'Idle-session enforcement: 15-minute inactivity timeout, warning modal for the final 60 seconds, 10-minute grace on tab switch, and a persisted <font face="Mono">session_last_active</font> timestamp so a reopened tab logs out if the idle window passed. Calls authStore.logout() and routes to /login on terminate.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.4 Layouts'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/layouts/StoreLayout.vue'), 'The storefront shell: top bar, search, header actions (cart badge, inbox badge with 15 s unread polling, dashboard link, logout), primary nav with top 5 categories, mobile dropdown, and footer. Applies the business brand colors as CSS variables (<font face="Mono">--brand</font>, <font face="Mono">--brand-dark</font>) and the store name in the logo. Mounts the forced-password ChangePasswordModal. Resolves the business context (slug mode vs directory) on mount and when the slug changes.'),
        (mono('src/layouts/SuperadminLayout.vue'), 'Shell for the /superadmin panel: sidebar navigation (dashboard, owners, inbox), top bar with the platform name.'),
        (mono('src/layouts/StoreFooter.vue'), 'Standalone footer component. Not imported by any current page (the footer is inlined in StoreLayout.vue); retained as a reusable footer for storefront pages.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.5 Shared Components'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/components/ChangePasswordModal.vue'), 'Forced password-change dialog shown whenever the API reports must_change_password. Validates strength and calls authApi.changePassword; hides itself on success.'),
        (mono('src/components/ResetOwnerPasswordModal.vue'), 'Superadmin dialog to reset an owner password to the default and optionally unlock the account.'),
        (mono('src/components/SessionWarningModal.vue'), 'Countdown overlay for the final minute of the idle session; any activity dismisses it.'),
        (mono('src/components/SkeletonLoader.vue'), 'Loading placeholder block used by pages while fetching data.'),
        (mono('src/components/TablePagination.vue'), 'Shared pagination bar (per-page count, page links, show-all toggle) bound to the useTablePagination composable.'),
        (mono('src/components/product/ProductCard.vue'), 'Storefront product card: image (via imageUrl), name, price, add-to-cart button; used by the product list, home, and search results.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.6 Composables & Utilities'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/composables/useTablePagination.js'), 'Client-side pagination + search for tables: filteredItems (dot-path search fields), paginatedItems, pageInfo, goToPage, toggleShowAll. Default 15 per page.'),
        (mono('src/utils/image.js'), 'imageUrl(path) helper. Turns relative paths into absolute API URLs: /products/… paths resolve against the API origin derived from VITE_API_URL; already-absolute URLs pass through.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.7 Pages — Storefront & Customer'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/home/DirectoryPage.vue'), 'Landing page of the platform (route /): lists all active businesses from the public /businesses API as store cards and lets the visitor open a white-label store. Headline, badge, counts and empty-state copy load from the DB-driven home content setting (dir* keys) with i18n fallback.'),
        (mono('pages/home/HomePage.vue'), 'Storefront homepage of a business (route /:businessSlug): hero, featured products, categories, brand-colored UI. Hero/badge/count copy loads from the DB-driven home content setting with i18n fallback; {count} placeholders are substituted with live product counts.'),
        (mono('pages/products/ProductListPage.vue'), 'Searchable, paginated product grid (public /products with ?search, ?category_id, ?business).'),
        (mono('pages/products/ProductDetailPage.vue'), 'Product detail: images, variant picker (color/storage), price, stock, add-to-cart.'),
        (mono('pages/products/CategoryPage.vue'), 'Category listing with its products and children.'),
        (mono('pages/cart/CartPage.vue'), 'Cart review: line items, quantities, subtotal, shipping estimate, proceed to checkout.'),
        (mono('pages/checkout/CheckoutPage.vue'), 'Checkout: delivery-required toggle, address selection, shipping-cost calculation (/shipping/calculate), payment provider choice (M-Pesa/Airtel/Mixx/Halopesa/ClickPesa/cash), optional winga reference; places the order and shows the payment outcome.'),
        (mono('pages/account/OrdersPage.vue'), 'Order history for the logged-in user with status, items, and payments.'),
        (mono('pages/account/AccountPage.vue'), 'Profile + address book (CRUD via addressApi) and account settings.'),
        (mono('pages/account/SupportPage.vue'), 'Customer support tickets: create a ticket against an order, view replies and status.'),
        (mono('pages/customer/CustomerInboxPage.vue'), 'Customer chat with the store owner (conversationApi); live unread badges; WhatsApp-style read ticks (grey = delivered, blue = read) on sent messages.'),
        (mono('pages/dashboards/CustomerDashboard.vue'), 'Customer landing after login: quick stats, recent orders, quick links.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.8 Pages — Authentication'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/auth/LoginPage.vue'), 'Login form with live password-strength rules, remaining-attempts feedback, account-lockout notice, and language switch.'),
        (mono('pages/auth/RegisterPage.vue'), 'Customer registration form; enforces the same password rules; creates the account and logs in.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.9 Pages — Employee & Owner Operations'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/dashboards/EmployeeDashboard.vue'), 'Staff home: stats (orders, revenue, alerts), quick actions, accounting issues scoped to the branch.'),
        (mono('pages/dashboards/OwnerDashboard.vue'), 'Owner home: sales KPIs, low-stock alerts, recent orders, quick links, and the AI suggestions panel.'),
        (mono('pages/dashboards/analytics/SalesCharts.vue'), 'Chart.js line/bar visuals for monthly sales, items, profit, and cancellations from /analytics/sales.'),
        (mono('pages/dashboards/analytics/AiSuggestions.vue'), 'AI insights panel: posts the analytics payload to /analytics/ai-suggestions and renders bilingual suggestions with priority and category.'),
        (mono('pages/employee/OrderManagementPage.vue'), 'Order desk (shared owner/employee): filter by status/branch/search; confirm payment, advance status, add tracking, process returns.'),
        (mono('pages/employee/CustomerManagementPage.vue'), 'Customer list for staff: search, toggle active, delete.'),
        (mono('pages/employee/EmployeeEarningsPage.vue'), 'Employee commissions: pending/paid totals and recent commission records (my-earnings).'),
        (mono('pages/employee/EmployeeInboxPage.vue'), 'Employee chat with the owner (owner_employee conversations); read ticks (grey = delivered, blue = read).'),
        (mono('pages/employee/SupportInboxPage.vue'), 'Staff support-ticket desk: reply, change status, unread/open counts.'),
        (mono('pages/owner/ProductManagementPage.vue'), 'Owner product list with search, stock value, active toggle, edit/delete links.'),
        (mono('pages/owner/ProductFormPage.vue'), 'Product create/edit form: SKU, prices, category, image upload or URL, variants with per-variant cost/price/quantity.'),
        (mono('pages/owner/EmployeeManagementPage.vue'), 'Employee CRUD: NIDA/voting IDs, branch assignment, commission rate, guarantors (Wadhamini), document uploads, reset password.'),
        (mono('pages/owner/BranchManagementPage.vue'), 'Branches CRUD with default branch, order/employee counts.'),
        (mono('pages/owner/PaymentSettingsPage.vue'), 'Payment providers management and the ClickPesa enable flag.'),
        (mono('pages/owner/ShippingSettingsPage.vue'), 'Shipping rules CRUD (from/to city, base cost, value-based tiers).'),
        (mono('pages/owner/ReportsPage.vue'), 'Daily and summary sales reports.'),
        (mono('pages/owner/InventoryManagementPage.vue'), 'Inventory dashboard: stock levels, adjust (opening/adjustment/damage), transactions log, low-stock list.'),
        (mono('pages/owner/PurchaseOrderPage.vue'), 'Purchase orders CRUD and receiving (stock-in + journal).'),
        (mono('pages/owner/SupplierManagementPage.vue'), 'Supplier CRUD with legal fields (TIN/VAT/registration), documents, and purchase-order counts.'),
        (mono('pages/owner/StockAlertsPage.vue'), 'Low/out-of-stock alerts: acknowledge, resolve.'),
        (mono('pages/owner/CommissionManagementPage.vue'), 'Employee commissions: summary per employee, pay individually or pay-all.'),
        (mono('pages/owner/OwnerInboxPage.vue'), 'Owner chat: with customers and with the platform superadmin, plus unread counts; read ticks on sent messages.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.10 Pages — Accounting'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/owner/AccountingDashboardPage.vue'), 'Accounting overview: trial-balance match, recent entries, generated reports, quick links.'),
        (mono('pages/owner/ChartOfAccountsPage.vue'), 'Chart of accounts tree with balances; create/edit/delete accounts (system accounts read-only).'),
        (mono('pages/owner/JournalEntryListPage.vue'), 'Journal entries list with status filters and search.'),
        (mono('pages/owner/JournalEntryCreatePage.vue'), 'Manual journal entry creator: balanced debit/credit line editor, draft or post.'),
        (mono('pages/owner/JournalEntryDetailPage.vue'), 'Entry detail: lines, totals, poster/void info; post, void, delete actions where allowed.'),
        (mono('pages/owner/TrialBalancePage.vue'), 'Trial balance as of a date.'),
        (mono('pages/owner/ProfitLossPage.vue'), 'Profit &amp; loss for a date range.'),
        (mono('pages/owner/BalanceSheetPage.vue'), 'Balance sheet as of a date.'),
        (mono('pages/owner/GeneralLedgerPage.vue'), 'General ledger per account with running balances.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.11 Pages — Winga Street Promoters'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/winga/WingaManagementPage.vue'), 'Winga CRUD (shared owner/employee): name, phone, TIN/NIDA, commission rate, branch, status.'),
        (mono('pages/winga/WingaCommissionPage.vue'), 'Winga commissions list + summary (gross, TRA TDS withholding, net) and payout actions (owner).'),
    ]))
    el.append(spacer(8))

    el.append(section('5.12 Pages — Superadmin'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/superadmin/SuperadminDashboard.vue'), 'Platform stats: owners, employees, customers, orders, revenue, subscription distribution.'),
        (mono('pages/superadmin/OwnerManagementPage.vue'), 'Owners table: create owner, toggle active, delete, navigate to detail.'),
        (mono('pages/superadmin/OwnerDetailPage.vue'), 'Owner detail: subscription, limits, password status; reset/set password, force change, unlock account.'),
        (mono('pages/superadmin/BrandingPage.vue'), 'White-label branding editor: store name, tagline, logo upload, brand colors.'),
        (mono('pages/superadmin/SuperadminInboxPage.vue'), 'Superadmin inbox with owners (superadmin_owner conversations); read ticks on sent messages.'),
        (mono('pages/superadmin/HomeContentPage.vue'), 'System-wide content editor: EN/SW inputs for the directory landing (dir* keys) and every white-label storefront hero/badge/count string; saves via PUT /superadmin/settings/home-content.'),
    ]))
    el.append(spacer(8))

    el.append(section('5.13 Pages — Supplier Portal'))
    el.append(info_table(header=['Page', 'Purpose'], col_widths=[230, 250], rows=[
        (mono('pages/supplier/SupplierPortalPage.vue'), 'Supplier-facing portal: profile, purchase orders assigned to the supplier\'s email, update PO status (ordered → received).'),
    ]))
    el.append(spacer(8))

    el.append(section('5.14 Tests'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('src/__tests__/App.spec.js'), 'Vitest unit test for the root App component (token watch / session wiring).'),
    ]))
    el.append(PageBreak())
    return el


def ch_backend():
    el = []
    el.append(chapter('6. Backend Deep Dive — Every File'))
    el.append(hr())
    el.append(body('This chapter documents the Laravel backend (<font face="Mono">erp-electronics-api/</font>): bootstrap, middleware, providers, models, controllers, services, tenant support, console commands, and configuration. Paths are relative to the backend repository root.'))
    el.append(spacer(8))

    el.append(section('6.1 Bootstrap & Kernel'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('bootstrap/app.php'), 'Application configuration. withRouting mounts the /api prefix, /up health endpoint, web + console routes. withMiddleware: throttleApi() applies the api rate limiter to every /api route; redirectGuestsTo(null) makes unauthenticated requests return a 401 JSON instead of a redirect; alias() registers the three role middlewares (owner, superadmin, supplier). withExceptions: shouldRenderJsonWhen api/* so every error on API routes is JSON.'),
        (mono('bootstrap/providers.php'), 'Registers AppServiceProvider as the application provider.'),
        (mono('app/Providers/AppServiceProvider.php'), 'boot() registers the request macros business() and ownerId() (delegating to Tenant) and the named rate limiters: api (120/min per user id or IP), login (5/min per IP), register (3/min + 10/day per IP).'),
        (mono('app/Exceptions/AccountingException.php'), 'Domain exception for accounting failures (missing system accounts, unbalanced entries, missing cost prices). Caught by controllers and rendered as HTTP 422.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.2 Middleware'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[200, 280], rows=[
        (mono('app/Http/Middleware/OwnerMiddleware.php'), 'Alias owner. Returns 403 "Unauthorized. Owner access required." unless the authenticated user isOwner().'),
        (mono('app/Http/Middleware/SuperadminMiddleware.php'), 'Alias superadmin. Returns 403 "Unauthorized" unless isSuperadmin().'),
        (mono('app/Http/Middleware/SupplierMiddleware.php'), 'Alias supplier. Requires an authenticated, is_active user (else 401); then requires role supplier or superadmin (else 403 "Forbidden"). Wraps the supplier-portal routes.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.3 Models (app/Models/) — 38'))
    el.append(info_table(header=['Model', 'Table', 'Purpose & key behaviour'], col_widths=[130, 120, 230], rows=[
        ('User', 'users', 'Identity for all roles (customer/employee/owner/supplier/superadmin). Attributes: role enum, is_active, is_superadmin, phone, password_changed_at, failed_login_attempts, locked_until. Constants MAX_LOGIN_ATTEMPTS=5, LOCKOUT_MINUTES=30. Logic: mustChangePassword() (≥3 days), superadminPasswordExpired() (≥6 months), getPasswordStatus(), recordFailedLogin/resetFailedLoginAttempts/unlockAccount/isLocked. Relations: profiles, orders, addresses, documents, guarantors, branches, businesses.'),
        ('OwnerProfile', 'owner_profiles', 'Subscription + white-label branding per owner: plan, expiry, max_products/max_employees limits, brand_store_name/tagline/logo/colors. Helpers isSubscriptionActive(), isTrialActive().'),
        ('EmployeeProfile', 'employee_profiles', 'Employment data: employee_code (EMP-xxxxxx), position, department, hire_date, branch_id, commission_rate, base_salary, NIDA/voting ID numbers.'),
        ('CustomerProfile', 'customer_profiles', 'Customer extras: date_of_birth, loyalty_points.'),
        ('Category', 'categories', 'Self-referential parent/children tree; name_sw for Swahili; getTranslatedNameAttribute() respects Accept-Language: sw.'),
        ('Product', 'products', 'SKU, name, slug (auto from name on creating), price, cost_price, images JSON, category_id, owner_id. Cost price feeds COGS.'),
        ('ProductVariant', 'product_variants', 'Variant per product: color/storage/SKU, own price + cost_price; hasOne inventory.'),
        ('Inventory', 'inventory', 'quantity_on_hand + reorder_level per variant; isInStock()/needsReorder().'),
        ('Address', 'addresses', 'Customer/owner address book rows (label, street, city, is_default).'),
        ('Order', 'orders', 'status machine (pending_payment/pending/inactive/paid/processing/shipped/delivered/cancelled); order_number auto ORD-xxxx; subtotal/shipping/total/winga_fee; branch_id, handled_by, delivery fields. markAsPaid() sets paid and decrements inventory.'),
        ('OrderItem', 'order_items', 'Line item: variant, quantity, unit_price, total, returned_quantity.'),
        ('Payment', 'payments', 'Provider (mpesa/airtel/mixx_by_yas/halopesa/clickpesa/cash), amount, status (pending/completed/failed), metadata, provider_reference.'),
        ('PaymentProvider', 'payment_providers', 'Enabled payment method configuration (name, slug, number, icon, sort).'),
        ('Branch', 'branches', 'Owner branch; tenant boundary for orders/employees; is_default.'),
        ('Conversation', 'conversations', 'Message threads: type (superadmin_owner/customer_owner/owner_employee), participants, status; otherParty() resolves the counterpart.'),
        ('ConversationMessage', 'conversation_messages', 'Message rows with is_read (read receipts); conversation + sender relations. ConversationController::show() flips is_read when the recipient opens the thread.'),
        ('SupportMessage', 'support_messages', 'Customer support tickets (category, status, admin_reply).'),
        ('ShippingRule', 'shipping_rules', 'City-pair shipping cost with value-based tiers; calculateCost() picks the first matching tier.'),
        ('Setting', 'settings', 'Key/value store (type-tagged) for vat_rate, income_tax_rate, winga_wht_rate, clickpesa_enabled, prices_include_vat. getTypedValue() decodes by type.'),
        ('DailyReport', 'daily_reports', 'Generated daily sales snapshot (revenue, items, paid/pending/cancelled, employee_stats, top_products).'),
        ('Account', 'accounts', 'Chart of accounts: code (unique per owner), type, normal_balance, parent tree, is_system. getBalanceAttribute() sums posted lines by normal-balance direction.'),
        ('JournalEntry', 'journal_entries', 'Double-entry header: reference JE-YYYY-seq, date, status (draft/posted/voided), source_type/source_id, prepared_by/posted_by/voided_by. isBalanced() checks |debit-credit| < 0.01.'),
        ('JournalLine', 'journal_lines', 'Entry lines: account_id, debit, credit, description.'),
        ('AccountingReport', 'accounting_reports', 'Generated monthly/yearly statements with data + summary JSON, suggestions JSON, is_finalized.'),
        ('Commission', 'commissions', 'Employee commission per paid order (order_amount, cost_amount, profit_amount, rate, amount; status pending/paid/reversed).'),
        ('InventoryTransaction', 'inventory_transactions', 'Stock movement audit (sale/return/adjustment/purchase/damage/opening) with quantity_after and reference.'),
        ('Supplier', 'suppliers', 'Vendor master: legal fields (business_type, TIN, VAT, registration), contact, address; documents relation.'),
        ('PurchaseOrder', 'purchase_orders', 'PO header: po_number PO-YYYY-seq, status (draft/ordered/received), total_cost, dates, journal_entry_id.'),
        ('PurchaseOrderItem', 'purchase_order_items', 'PO line items with quantity_received.'),
        ('StockAlert', 'stock_alerts', 'Low/out-of-stock alerts (active/acknowledged/resolved).'),
        ('EmployeeDocument', 'employee_documents', 'Uploaded employee files (contract/background_check/other).'),
        ('EmployeeGuarantor', 'employee_guarantors', 'Guarantor records (Wadhamini) per employee.'),
        ('SupplierDocument', 'supplier_documents', 'Uploaded supplier legal documents (8 categories).'),
        ('Notification', 'notifications', 'In-app notifications (custom table, not Laravel\'s): type, title, message, link, read_at.'),
        ('Business', 'businesses', 'White-label store per owner: name, slug, tagline, logo, is_active; relations to members (co-owners) and products.'),
        ('BusinessUser', 'business_user', 'Pivot (composite PK business_id+user_id) with role column for co-ownership.'),
        ('Winga', 'wingas', 'Street promoter: phone, TIN/NIDA, commission_rate (%), branch, status.'),
        ('WingaCommission', 'winga_commissions', 'Per-order winga commission: gross, withholding_tax (TRA TDS), net, status (pending/paid/reversed), journal_entry_id.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.4 Controllers (app/Http/Controllers/Api/) — 31'))
    el.append(info_table(header=['Controller', 'Area', 'Responsibilities'], col_widths=[150, 110, 220], rows=[
        ('AuthController', 'Auth', 'register (public, creates customer), login (lockout + attempts + flags), logout, profile, updateProfile, changePassword.'),
        ('ProductController', 'Catalog', 'Public index/show/featured (business-scoped) + owner store/update/destroy/manage with variant + inventory creation and image handling.'),
        ('CategoryController', 'Catalog', 'Public category tree + detail with active products; translated names.'),
        ('BusinessController', 'Multi-store', 'Public index/by-slug; owner mine; presentation of store_name/colors.'),
        ('CartController', 'Commerce', 'Cart-as-pending_payment-order: index/add/update/remove/clear with stock checks and recalculation.'),
        ('OrderController', 'Commerce', 'Checkout store, index/show, manage, updateStatus (lifecycle + auto-journaling), updateDelivery, returnItems (partial returns).'),
        ('PaymentController', 'Commerce', 'initiate (auto-confirms ClickPesa/cash), webhook (no auth), status.'),
        ('PaymentProviderController', 'Commerce', 'Public enabled list + owner/staff management CRUD.'),
        ('ShippingController', 'Commerce', 'Public calculate (city pairs + wildcards) + owner CRUD of rules.'),
        ('AddressController', 'Commerce', 'Authenticated user address book (apiResource).'),
        ('BranchController', 'Tenant', 'Owner branches CRUD + set-default.'),
        ('EmployeeController', 'HR', 'Owner-only employee CRUD: default password = strtoupper(name), branch assignment, NIDA/voting IDs, guarantors, document upload/download, reset-password, toggle-status.'),
        ('CustomerController', 'Customers', 'Staff customer list, toggle-status, destroy.'),
        ('ReportController', 'Reports', 'daily + summary reports; generateForDate builds the snapshot.'),
        ('AnalyticsController', 'Analytics', 'sales (SQLite strftime grouping, zero-filled months, summary metrics) + ai-suggestions (Gemini with fallback).'),
        ('ConversationController', 'Messaging', 'Role-based conversations: index/store/show/sendMessage/updateStatus/unreadCount/contacts/ownerDetails/customerDetails/destroy/destroyMessage. show() marks incoming messages read (read receipts), powering the frontend WhatsApp-style ticks.'),
        ('SupportMessageController', 'Support', 'Tickets: index/store/show/reply/updateStatus/unreadCount.'),
        ('NotificationController', 'Notifications', 'index/count/markRead/markAllRead + static create factory.'),
        ('AccountController', 'Accounting', 'Chart of accounts index/tree/store/update/destroy with system-account protections.'),
        ('JournalEntryController', 'Accounting', 'Manual entries: index/store (balanced draft)/show/update/post/void/destroy.'),
        ('AccountingReportController', 'Accounting', 'Live statements (trial-balance/profit-loss/balance-sheet/general-ledger) + generate monthly/yearly + list/show + ai-suggestions.'),
        ('AccountingIssuesController', 'Accounting', 'Actionable issue buckets (unconfirmed payments, pending deliveries, missing cost prices, drafts, voids, pending commissions, unbalanced trial balance, low stock) with owner vs branch scoping.'),
        ('CommissionController', 'Payroll', 'Commissions index/summary/pay/pay-all/employee-earnings with payout journals.'),
        ('WingaController', 'Winga', 'Winga CRUD + toggle-status (owner/employee, tenant-scoped).'),
        ('WingaCommissionController', 'Winga', 'Commissions index/summary/pay/pay-all with TRA TDS payout journals.'),
        ('InventoryController', 'Inventory', 'index/adjust/transactions/low-stock/dashboard; adjustment posts inventory journals + triggers low-stock check.'),
        ('PurchaseOrderController', 'Procurement', 'PO index/store/show/receive/destroy + supplier-portal supplierOrders/supplierShow/supplierUpdateStatus.'),
        ('SupplierController', 'Procurement', 'Supplier CRUD + documents + portal profile.'),
        ('StockAlertController', 'Inventory', 'index/count/acknowledge/resolve + static checkLowStock used by other flows.'),
        ('SettingsController', 'Platform', 'Public payment flag + branding + home content (defaults merged over stored JSON); owner updatePayment; superadmin updateHomeContent (whitelisted keys).'),
        ('SuperadminController', 'Platform', 'Stats, owner CRUD, subscription/limits/branding/logo, password status/reset/set/force/unlock, all-password status.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.5 Services'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[210, 270], rows=[
        (mono('app/Services/AccountingEntryService.php'), 'The accounting engine. VAT/WHT helpers (getVatRate default 18, pricesIncludeVat default true, getWingaWhtRate default 5, splitVat). postSale() posts cash/revenue/VAT/COGS/winga accrual; reverseSale() reverses it; postReturn() books partial returns; postInventoryAdjustment() books stock adjustments; createCommission()/createWingaCommission() accrue payables; reverseCommissions()/reverseWingaCommissions() handle cancellation clawbacks; adjustCommissionForReturn()/adjustWingaCommissionForReturn() prorate on partial returns; closeYear() posts the year-end entry to retained earnings.'),
        (mono('app/Services/AccountingReportService.php'), 'computeTrialBalance/computeProfitLoss/computeBalanceSheet (posted entries only) and generateMonthlyReport/generateYearlyReport with data+summary JSON persistence.'),
        (mono('app/Services/AiSuggestionService.php'), 'Bilingual (EN/SW) accounting suggestions from Gemini (gemini-2.0-flash, temperature 0.7, 4096 tokens, 60 s timeout) with deterministic rule-based fallback (M-Pesa reconciliation, VAT/TRA reminders, inventory counts).'),
    ]))
    el.append(spacer(8))

    el.append(section('6.6 Multi-Tenancy Support'))
    el.append(info_table(header=['File', 'Purpose'], col_widths=[210, 270], rows=[
        (mono('app/Support/Tenant.php'), 'activeBusiness(request) resolves the current business for an owner (owned + co-owned, X-Business-Id first). ownerId(request) returns the active business owner_id or the user\'s own id. forUser() lists manageable businesses; bySlug() resolves a storefront business.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.7 Console Commands (app/Console/Commands/) — 5'))
    el.append(info_table(header=['Command', 'Purpose'], col_widths=[210, 270], rows=[
        ('GenerateDailyReport (report:daily)', 'Generates the daily sales report for --date (default yesterday).'),
        ('CleanupUnpaidOrders (orders:cleanup-unpaid)', 'Marks pending/pending_payment orders inactive after 3 h and deletes inactive orders after 6 h.'),
        ('ResetSuperadminPassword (superadmin:reset-password)', 'Resets the superadmin password to SuperAdmin@2026 when older than 6 months.'),
        ('GenerateAccountingReports (accounting:generate-reports)', 'Generates monthly reports for active owners; --with-suggestions also runs the AI suggestions.'),
        ('CloseYearAccounting (accounting:close-year)', 'Posts year-end closing entries into retained earnings for all active owners.'),
    ]))
    el.append(spacer(8))

    el.append(section('6.8 Scheduler (routes/console.php)'))
    el.append(info_table(header=['Schedule', 'Task'], col_widths=[160, 320], rows=[
        ('Daily 00:10', 'report:daily'),
        ('Every 5 minutes', 'orders:cleanup-unpaid'),
        ('Monthly', 'superadmin:reset-password'),
        ('1st of month 00:30', 'accounting:generate-reports --with-suggestions'),
        ('Jan 1 01:00', 'accounting:close-year'),
    ]))
    el.append(spacer(8))

    el.append(section('6.9 Configuration Highlights (config/)'))
    el.append(info_table(header=['File', 'Notable values'], col_widths=[130, 350], rows=[
        ('app.php', 'timezone UTC, locale en (env-overridable), cipher AES-256-CBC.'),
        ('auth.php', 'web guard with users provider; password broker on password_reset_tokens (60 min).'),
        ('database.php', 'Default connection sqlite; full mysql/mariadb/pgsql/sqlsrv blocks; MySQL utf8mb4 strict.'),
        ('filesystems.php', 'Default disk local; public disk; s3 disk for Laravel Cloud (FILESYSTEM_DISK=s3).'),
        ('sanctum.php', 'Stateful domains include localhost:5173/5174 and the app URL; tokens never expire by default.'),
        ('services.php', 'gemini block reading GEMINI_API_KEY.'),
        ('session.php', 'database driver, 120 min lifetime, http_only, same_site lax.'),
        ('cache.php', 'database store by default.'),
        ('queue.php', 'database connection, retry_after 90 s.'),
        ('mail.php', 'log mailer by default.'),
        ('logging.php', 'stack → single channel at debug level.'),
    ]))
    el.append(PageBreak())
    return el


def ch_schema():
    el = []
    el.append(chapter('7. Database Schema & Models'))
    el.append(hr())
    el.append(body('The database contains <b>46 business tables</b> plus Laravel framework tables, built by <b>56 migrations</b>. A full entity-relationship diagram is available as <b>ERD.drawio</b> (crow\'s foot notation). This section lists the tables by domain and the notable columns added by later migrations.'))
    el.append(spacer(8))
    el.append(section('Tables by Domain'))
    el.append(info_table(header=['Domain', 'Tables'], col_widths=[120, 360], rows=[
        ('Identity', 'users, customer_profiles, employee_profiles, owner_profiles, personal_access_tokens'),
        ('Multi-store', 'businesses, business_user'),
        ('Catalog', 'categories, products, product_variants, inventory'),
        ('Commerce', 'addresses, branches, orders, order_items, payments, payment_providers, shipping_rules'),
        ('Support', 'support_messages, conversations, conversation_messages, notifications'),
        ('Accounting', 'accounts, journal_entries, journal_lines, accounting_reports'),
        ('Payroll', 'commissions, wingas, winga_commissions'),
        ('Operations', 'inventory_transactions, purchase_orders, purchase_order_items, suppliers, stock_alerts'),
        ('Documents', 'employee_documents, employee_guarantors, supplier_documents'),
        ('Settings', 'settings, daily_reports'),
        ('Framework', 'password_reset_tokens, sessions, cache, cache_locks, jobs, job_batches, failed_jobs'),
    ]))
    el.append(spacer(8))
    el.append(section('Order Status Enum'))
    el.append(body('The <font face="Mono">orders.status</font> enum evolved across migrations to its current value set:'))
    el.append(info_table([
        ('Value set', 'pending, pending_payment, inactive, paid, processing, shipped, delivered, cancelled'),
        ('Default', 'pending_payment (a cart)'),
        ('Meaning', 'pending_payment = active cart; pending = checked out awaiting payment confirmation; inactive = abandoned (cleanup command); paid = confirmed (inventory + journals); then processing → shipped → delivered; cancelled is terminal; returns may auto-cancel fully-returned orders'),
    ]))
    el.append(spacer(8))
    el.append(section('Key Relationships'))
    el.extend(bullet_list([
        '<b>User</b> has one profile row depending on role (customer_profile / employee_profile / owner_profile) and belongs to businesses via the business_user pivot (co-owners).',
        '<b>Product</b> → category, has many variants → one inventory row each. Products/categories/shipping_rules carry owner_id.',
        '<b>Order</b> → user, optional branch, winga (plain column), items, payments, shipping address; handled_by references the staff user.',
        '<b>Conversation</b> → owner, optional customer/employee/superadmin; has many messages.',
        '<b>JournalEntry</b> → owner, prepared/posted/voided by users; has many journal_lines → accounts.',
        '<b>Commission / WingaCommission</b> → owner, order, journal entry; commissions reference the employee.',
        '<b>PurchaseOrder</b> → owner, supplier (nullable), items → variants; received POs post inventory journals.',
        '<b>Business</b> → owner; products and members relate back to the business (products by owner_id; members via pivot).',
    ]))
    el.append(spacer(8))
    el.append(section('System Account Codes'))
    el.append(info_table(header=['Code', 'Name', 'Type'], col_widths=[60, 300, 120], rows=[
        ('1020', 'Cash (M-Pesa/Bank) — cash base used by payouts', 'Asset'),
        ('1200', 'Inventory', 'Asset'),
        ('2100', 'Winga Commission Payable', 'Liability'),
        ('2120', 'Withholding Tax Payable (TDS)', 'Liability'),
        ('2500', 'VAT Output', 'Liability'),
        ('3010', 'Owner\'s Capital', 'Equity'),
        ('3020', 'Retained Earnings', 'Equity'),
        ('4010', 'Sales Revenue', 'Revenue'),
        ('4020', 'Shipping Revenue', 'Revenue'),
        ('5010', 'Cost of Goods Sold', 'Expense'),
        ('5100', 'Inventory Adjustments', 'Expense'),
        ('5110', 'Commission Expense', 'Expense'),
    ]))
    el.append(PageBreak())
    return el


def ch_auth():
    el = []
    el.append(chapter('8. Authentication & Authorization'))
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
        '<b>Password expiry</b>: <font face="Mono">password_changed_at</font> must be newer than <b>3 days</b>, otherwise a forced change modal appears on login (owners).',
    ]))
    el.append(spacer(6))
    el.append(section('Default Passwords'))
    el.append(info_table([
        ('Employee (owner-created)', 'Full name in capitals — e.g. "MATHEW ZACHARIA"; password_changed_at null forces a change'),
        ('Owner (superadmin-created)', 'Full name in capitals + random 3-digit suffix — e.g. "JOHN DOE123"; forced change on first login'),
        ('Superadmin', 'SuperAdmin@2026 — auto-reset every 6 months via scheduled artisan command'),
    ]))
    el.append(spacer(6))
    el.append(section('Account Lockout'))
    el.append(body('After <b>5 failed login attempts</b> the account locks for <b>30 minutes</b> (<font face="Mono">users.locked_until</font>). The API returns HTTP <b>423</b> with a remaining-minutes message; the login form also reports remaining attempts.'))
    el.append(spacer(6))
    el.append(section('Role Enforcement'))
    el.append(body('Roles gate both routes (backend middleware) and navigation (frontend router meta). The middleware chain per request is: <b>api group (throttle:api)</b> → <b>auth:sanctum</b> → optional <b>owner / superadmin / supplier</b> role middleware. Missing tokens return 401 JSON; role violations return 403 JSON with a distinct message per middleware.'))
    el.append(spacer(6))
    el.append(section('Session Idle Timeout (frontend)'))
    el.extend(bullet_list([
        '<b>15 minutes</b> of inactivity → session ends (mouse, keyboard, touch, scroll, click, wheel reset the timer).',
        'At <b>14 minutes</b> a warning modal shows a <b>60-second countdown</b>; any activity dismisses it.',
        'Switching tabs/apps pauses the timer; returning within <b>10 minutes</b> continues the session, otherwise the user is signed out.',
        'A <font face="Mono">session_last_active</font> timestamp is persisted, so returning to a closed tab after the idle window forces logout on load.',
        'Logout clears <font face="Mono">auth_token</font> and revokes the Sanctum token on the server.',
    ]))
    el.append(PageBreak())
    return el


def ch_api():
    el = []
    el.append(chapter('9. API Reference — All 179 Routes'))
    el.append(hr())
    el.append(body('All endpoints are JSON and mounted under the <font face="Mono">/api</font> prefix. Development base: ' + mono(DEV_API) + '. Production base: ' + mono(PROD_API) + '. Of the 175 routes, <b>14 are public</b> and <b>161 require a Bearer token</b>; 35 are gated by the owner middleware, 16 by superadmin, and 4 by supplier. The only named routes are the 5 auto-generated addresses.* routes.'))
    el.append(spacer(8))
    el.append(section('9.1 Public Endpoints (no auth)'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Ext. middleware'], col_widths=[48, 170, 180, 82], rows=[
        ('POST', '/auth/register', 'AuthController@register', 'throttle:register'),
        ('POST', '/auth/login', 'AuthController@login', 'throttle:login'),
        ('GET', '/products', 'ProductController@index', '—'),
        ('GET', '/products/featured', 'ProductController@featured', '—'),
        ('GET', '/products/{slug}', 'ProductController@show', '—'),
        ('GET', '/businesses', 'BusinessController@index', '—'),
        ('GET', '/businesses/by-slug/{slug}', 'BusinessController@show', '—'),
        ('GET', '/categories', 'CategoryController@index', '—'),
        ('GET', '/categories/{slug}', 'CategoryController@show', '—'),
        ('GET', '/payment-providers', 'PaymentProviderController@publicIndex', '—'),
        ('POST', '/payments/webhook', 'PaymentController@webhook', '—'),
        ('POST', '/shipping/calculate', 'ShippingController@calculate', '—'),
        ('GET', '/settings/payment', 'SettingsController@payment', '—'),
        ('GET', '/settings/branding', 'SettingsController@branding', '—'),
        ('GET', '/settings/home-content', 'SettingsController@homeContent', '—'),
    ]))
    el.append(spacer(8))
    el.append(section('9.2 Authenticated — Auth, Businesses, Branches, Employees'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Role'], col_widths=[48, 220, 170, 42], rows=[
        ('POST', '/auth/logout', 'AuthController@logout', '—'),
        ('GET', '/auth/profile', 'AuthController@profile', '—'),
        ('PUT', '/auth/profile', 'AuthController@updateProfile', '—'),
        ('POST', '/auth/change-password', 'AuthController@changePassword', '—'),
        ('GET', '/businesses/mine', 'BusinessController@mine', '—'),
        ('GET', '/branches', 'BranchController@index', '—'),
        ('POST', '/branches', 'BranchController@store', '—'),
        ('GET', '/branches/{branch}', 'BranchController@show', '—'),
        ('PUT', '/branches/{branch}', 'BranchController@update', '—'),
        ('PATCH', '/branches/{branch}/set-default', 'BranchController@setDefault', '—'),
        ('DELETE', '/branches/{branch}', 'BranchController@destroy', '—'),
        ('GET', '/employees', 'EmployeeController@index', 'owner'),
        ('POST', '/employees', 'EmployeeController@store', 'owner'),
        ('PUT', '/employees/{user}', 'EmployeeController@update', 'owner'),
        ('PATCH', '/employees/{user}/toggle-status', 'EmployeeController@toggleStatus', 'owner'),
        ('PATCH', '/employees/{user}/assign-branch', 'EmployeeController@assignBranch', 'owner'),
        ('DELETE', '/employees/{user}', 'EmployeeController@destroy', 'owner'),
        ('PUT', '/employees/{user}/profile', 'EmployeeController@updateProfile', 'owner'),
        ('POST', '/employees/{user}/reset-password', 'EmployeeController@resetPassword', 'owner'),
        ('GET', '/employees/{user}/documents', 'EmployeeController@indexDocuments', 'owner'),
        ('POST', '/employees/{user}/documents', 'EmployeeController@storeDocuments', 'owner'),
        ('DELETE', '/employees/{user}/documents/{document}', 'EmployeeController@destroyDocument', 'owner'),
        ('GET', '/employees/{user}/documents/{document}/download', 'EmployeeController@downloadDocument', 'owner'),
    ]))
    el.append(spacer(8))
    el.append(section('9.3 Authenticated — Customers, Products, Settings, Payments'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Role'], col_widths=[48, 220, 170, 42], rows=[
        ('GET', '/customers', 'CustomerController@index', 'staff'),
        ('PATCH', '/customers/{user}/toggle-status', 'CustomerController@toggleStatus', 'staff'),
        ('DELETE', '/customers/{user}', 'CustomerController@destroy', 'staff'),
        ('GET', '/products-manage', 'ProductController@manage', 'owner'),
        ('POST', '/products', 'ProductController@store', 'owner'),
        ('PUT', '/products/{id}', 'ProductController@update', 'owner'),
        ('DELETE', '/products/{id}', 'ProductController@destroy', 'owner'),
        ('PUT', '/settings/payment', 'SettingsController@updatePayment', 'owner'),
        ('GET', '/payment-providers-manage', 'PaymentProviderController@index', '—'),
        ('POST', '/payment-providers', 'PaymentProviderController@store', '—'),
        ('PUT', '/payment-providers/{id}', 'PaymentProviderController@update', '—'),
        ('DELETE', '/payment-providers/{id}', 'PaymentProviderController@destroy', '—'),
        ('POST', '/payments/initiate', 'PaymentController@initiate', '—'),
        ('GET', '/orders/{orderId}/payment-status', 'PaymentController@status', '—'),
    ]))
    el.append(spacer(8))
    el.append(section('9.4 Authenticated — Cart, Orders, Addresses, Support'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Role'], col_widths=[48, 220, 170, 42], rows=[
        ('GET', '/cart', 'CartController@index', '—'),
        ('POST', '/cart', 'CartController@add', '—'),
        ('PUT', '/cart/{itemId}', 'CartController@update', '—'),
        ('DELETE', '/cart/{itemId}', 'CartController@remove', '—'),
        ('DELETE', '/cart', 'CartController@clear', '—'),
        ('GET', '/orders', 'OrderController@index', '—'),
        ('POST', '/orders', 'OrderController@store', '—'),
        ('GET', '/orders/{orderId}', 'OrderController@show', '—'),
        ('GET', '/orders-manage', 'OrderController@manage', 'staff'),
        ('PATCH', '/orders/{orderId}/status', 'OrderController@updateStatus', 'staff'),
        ('POST', '/orders/{orderId}/return', 'OrderController@returnItems', 'staff'),
        ('PATCH', '/orders/{orderId}/delivery', 'OrderController@updateDelivery', 'staff'),
        ('GET', '/addresses', 'AddressController@index', '—'),
        ('POST', '/addresses', 'AddressController@store', '—'),
        ('GET', '/addresses/{address}', 'AddressController@show', '—'),
        ('PUT/PATCH', '/addresses/{address}', 'AddressController@update', '—'),
        ('DELETE', '/addresses/{address}', 'AddressController@destroy', '—'),
        ('GET', '/support-messages', 'SupportMessageController@index', '—'),
        ('POST', '/support-messages', 'SupportMessageController@store', '—'),
        ('GET', '/support-messages/{id}', 'SupportMessageController@show', '—'),
        ('PATCH', '/support-messages/{id}/reply', 'SupportMessageController@reply', 'staff'),
        ('PATCH', '/support-messages/{id}/status', 'SupportMessageController@updateStatus', '—'),
        ('GET', '/support/unread-count', 'SupportMessageController@unreadCount', '—'),
    ]))
    el.append(spacer(8))
    el.append(section('9.5 Authenticated — Shipping, Analytics, Conversations'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Role'], col_widths=[48, 220, 170, 42], rows=[
        ('GET', '/shipping-rules', 'ShippingController@index', 'owner'),
        ('POST', '/shipping-rules', 'ShippingController@store', 'owner'),
        ('PUT', '/shipping-rules/{id}', 'ShippingController@update', 'owner'),
        ('DELETE', '/shipping-rules/{id}', 'ShippingController@destroy', 'owner'),
        ('GET', '/analytics/sales', 'AnalyticsController@sales', 'owner/staff'),
        ('POST', '/analytics/ai-suggestions', 'AnalyticsController@aiSuggestions', 'owner'),
        ('GET', '/conversations', 'ConversationController@index', '—'),
        ('POST', '/conversations', 'ConversationController@store', '—'),
        ('GET', '/conversations/unread-count', 'ConversationController@unreadCount', '—'),
        ('GET', '/conversations/contacts', 'ConversationController@contacts', '—'),
        ('GET', '/conversations/{conversation}', 'ConversationController@show', '—'),
        ('POST', '/conversations/{conversation}/messages', 'ConversationController@sendMessage', '—'),
        ('PATCH', '/conversations/{conversation}/status', 'ConversationController@updateStatus', '—'),
        ('GET', '/conversations/{conversation}/owner-details', 'ConversationController@ownerDetails', '—'),
        ('GET', '/conversations/{conversation}/customer-details', 'ConversationController@customerDetails', '—'),
        ('DELETE', '/conversations/{conversation}', 'ConversationController@destroy', '—'),
        ('DELETE', '/conversations/{conversation}/messages/{messageId}', 'ConversationController@destroyMessage', '—'),
    ]))
    el.append(note('Read receipts: every message carries an is_read flag. GET /conversations/{conversation} marks all incoming messages from the requesting user\'s counterpart as read; the sender picks this up via the 15 s polling in the inbox pages and renders grey (delivered) vs blue (read) ticks. There is no separate delivery flag — messages are server-stored, so unread is the only distinguishable state. Whole conversations (DELETE /conversations/{conversation}) and individual messages (DELETE /conversations/{conversation}/messages/{messageId}) can be removed by their participants.'))
    el.append(spacer(8))
    el.append(section('9.6 Authenticated — Accounting (owner)'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method'], col_widths=[48, 220, 212], rows=[
        ('GET', '/accounts', 'AccountController@index'),
        ('GET', '/accounts/tree', 'AccountController@tree'),
        ('POST', '/accounts', 'AccountController@store'),
        ('PUT', '/accounts/{id}', 'AccountController@update'),
        ('DELETE', '/accounts/{id}', 'AccountController@destroy'),
        ('GET', '/journal-entries', 'JournalEntryController@index'),
        ('POST', '/journal-entries', 'JournalEntryController@store'),
        ('GET', '/journal-entries/{id}', 'JournalEntryController@show'),
        ('PUT', '/journal-entries/{id}', 'JournalEntryController@update'),
        ('DELETE', '/journal-entries/{id}', 'JournalEntryController@destroy'),
        ('POST', '/journal-entries/{id}/post', 'JournalEntryController@post'),
        ('POST', '/journal-entries/{id}/void', 'JournalEntryController@void'),
        ('GET', '/reports/trial-balance', 'AccountingReportController@trialBalance'),
        ('GET', '/reports/profit-loss', 'AccountingReportController@profitLoss'),
        ('GET', '/reports/balance-sheet', 'AccountingReportController@balanceSheet'),
        ('GET', '/reports/general-ledger', 'AccountingReportController@generalLedger'),
        ('POST', '/reports/generate-monthly', 'AccountingReportController@generateMonthly'),
        ('POST', '/reports/generate-yearly', 'AccountingReportController@generateYearly'),
        ('GET', '/reports/list', 'AccountingReportController@listReports'),
        ('GET', '/reports/{id}', 'AccountingReportController@showReport'),
        ('POST', '/reports/ai-suggestions', 'AccountingReportController@aiSuggestions'),
        ('GET', '/accounting-issues', 'AccountingIssuesController@index'),
    ]))
    el.append(spacer(8))
    el.append(section('9.7 Authenticated — Reports, Commissions, Wingas, Inventory, Procurement'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method', 'Role'], col_widths=[48, 220, 170, 42], rows=[
        ('GET', '/reports/daily', 'ReportController@daily', 'staff'),
        ('GET', '/reports/summary', 'ReportController@summary', 'staff'),
        ('GET', '/commissions', 'CommissionController@index', 'owner/staff'),
        ('GET', '/commissions/summary', 'CommissionController@summary', 'owner/staff'),
        ('POST', '/commissions/{id}/pay', 'CommissionController@pay', 'owner'),
        ('POST', '/commissions/pay-all', 'CommissionController@payAll', 'owner'),
        ('GET', '/commissions/my-earnings', 'CommissionController@employeeEarnings', 'employee'),
        ('GET', '/wingas', 'WingaController@index', 'owner/staff'),
        ('POST', '/wingas', 'WingaController@store', 'owner/staff'),
        ('PUT', '/wingas/{winga}', 'WingaController@update', 'owner/staff'),
        ('PATCH', '/wingas/{winga}/toggle-status', 'WingaController@toggleStatus', 'owner/staff'),
        ('DELETE', '/wingas/{winga}', 'WingaController@destroy', 'owner/staff'),
        ('GET', '/winga-commissions', 'WingaCommissionController@index', 'owner/staff'),
        ('GET', '/winga-commissions/summary', 'WingaCommissionController@summary', 'owner/staff'),
        ('POST', '/winga-commissions/{id}/pay', 'WingaCommissionController@pay', 'owner'),
        ('POST', '/winga-commissions/pay-all', 'WingaCommissionController@payAll', 'owner'),
        ('GET', '/inventory', 'InventoryController@index', 'owner'),
        ('POST', '/inventory/adjust', 'InventoryController@adjust', 'owner/staff'),
        ('GET', '/inventory/transactions', 'InventoryController@transactions', 'owner'),
        ('GET', '/inventory/low-stock', 'InventoryController@lowStock', 'owner'),
        ('GET', '/inventory/dashboard', 'InventoryController@dashboard', 'owner'),
        ('GET', '/purchase-orders', 'PurchaseOrderController@index', 'owner'),
        ('POST', '/purchase-orders', 'PurchaseOrderController@store', 'owner'),
        ('GET', '/purchase-orders/{id}', 'PurchaseOrderController@show', 'owner'),
        ('POST', '/purchase-orders/{id}/receive', 'PurchaseOrderController@receive', 'owner'),
        ('DELETE', '/purchase-orders/{id}', 'PurchaseOrderController@destroy', 'owner'),
        ('GET', '/suppliers', 'SupplierController@index', 'owner'),
        ('GET', '/suppliers/all', 'SupplierController@all', 'owner'),
        ('POST', '/suppliers', 'SupplierController@store', 'owner'),
        ('GET', '/suppliers/{id}', 'SupplierController@show', 'owner'),
        ('PUT', '/suppliers/{id}', 'SupplierController@update', 'owner'),
        ('DELETE', '/suppliers/{id}', 'SupplierController@destroy', 'owner'),
        ('GET', '/suppliers/{id}/documents', 'SupplierController@indexDocuments', 'owner'),
        ('POST', '/suppliers/{id}/documents', 'SupplierController@storeDocumentsForSupplier', 'owner'),
        ('DELETE', '/suppliers/{id}/documents/{document}', 'SupplierController@destroyDocument', 'owner'),
        ('GET', '/suppliers/{id}/documents/{document}/download', 'SupplierController@downloadDocument', 'owner'),
        ('GET', '/stock-alerts', 'StockAlertController@index', 'owner'),
        ('GET', '/stock-alerts/count', 'StockAlertController@count', 'owner'),
        ('POST', '/stock-alerts/{id}/acknowledge', 'StockAlertController@acknowledge', 'owner'),
        ('POST', '/stock-alerts/{id}/resolve', 'StockAlertController@resolve', 'owner'),
        ('GET', '/notifications', 'NotificationController@index', '—'),
        ('GET', '/notifications/count', 'NotificationController@count', '—'),
        ('POST', '/notifications/{id}/read', 'NotificationController@markRead', '—'),
        ('POST', '/notifications/read-all', 'NotificationController@markAllRead', '—'),
    ]))
    el.append(spacer(8))
    el.append(section('9.8 Supplier Portal (supplier middleware)'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method'], col_widths=[48, 250, 182], rows=[
        ('GET', '/supplier-portal/profile', 'SupplierController@supplierProfile'),
        ('GET', '/supplier-portal/purchase-orders', 'PurchaseOrderController@supplierOrders'),
        ('GET', '/supplier-portal/purchase-orders/{id}', 'PurchaseOrderController@supplierShow'),
        ('POST', '/supplier-portal/purchase-orders/{id}/update-status', 'PurchaseOrderController@supplierUpdateStatus'),
    ]))
    el.append(spacer(8))
    el.append(section('9.9 Superadmin (superadmin middleware)'))
    el.append(info_table(header=['Method', 'URI', 'Controller@method'], col_widths=[48, 250, 182], rows=[
        ('GET', '/superadmin/stats', 'SuperadminController@stats'),
        ('GET', '/superadmin/owners', 'SuperadminController@index'),
        ('POST', '/superadmin/owners', 'SuperadminController@store'),
        ('GET', '/superadmin/owners/{id}', 'SuperadminController@show'),
        ('PATCH', '/superadmin/owners/{id}/toggle-active', 'SuperadminController@toggleActive'),
        ('PUT', '/superadmin/owners/{id}/subscription', 'SuperadminController@updateSubscription'),
        ('PUT', '/superadmin/owners/{id}/limits', 'SuperadminController@updateLimits'),
        ('PUT', '/superadmin/owners/{id}/branding', 'SuperadminController@updateBranding'),
        ('POST', '/superadmin/owners/{id}/branding-logo', 'SuperadminController@updateBrandingLogo'),
        ('DELETE', '/superadmin/owners/{id}', 'SuperadminController@destroy'),
        ('GET', '/superadmin/passwords/status', 'SuperadminController@allPasswordsStatus'),
        ('GET', '/superadmin/owners/{id}/password-status', 'SuperadminController@getPasswordStatus'),
        ('POST', '/superadmin/owners/{id}/reset-password', 'SuperadminController@resetPassword'),
        ('POST', '/superadmin/owners/{id}/set-password', 'SuperadminController@setPassword'),
        ('POST', '/superadmin/owners/{id}/force-password-change', 'SuperadminController@forcePasswordChange'),
        ('POST', '/superadmin/owners/{id}/unlock-account', 'SuperadminController@unlockAccount'),
        ('PUT', '/superadmin/settings/home-content', 'SettingsController@updateHomeContent'),
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
    return el


def ch_superadmin():
    el = []
    el.append(chapter('10. Superadmin Module'))
    el.append(hr())
    el.append(body('The <b>superadmin</b> is the platform administrator responsible for onboarding and managing business owners. Access the panel at <font face="Mono">/superadmin</font> (role-guarded). This module is intentionally <b>not</b> described in the end-user manuals.'))
    el.append(spacer(8))
    el.append(section('10.1 System Overview'))
    el.extend(bullet_list([
        '<b>System Statistics</b> — total customers, total orders, total revenue, and active owners at a glance.',
        '<b>Owners Table</b> — all registered owners with company name, plan, status, and registration date.',
    ]))
    el.append(spacer(6))
    el.append(section('10.2 Managing Owners'))
    el.extend(bullet_list([
        '<b>Create Owner</b> — registers an owner with name, email, phone, and company name. Default password is the full name in capitals plus a random 3-digit suffix; the response exposes <font face="Mono">default_password</font> to share securely.',
        '<b>Toggle Active/Inactive</b> — enable or disable an owner\'s account instantly.',
        '<b>Delete Owner</b> — removes the owner and all associated data.',
    ]))
    el.append(spacer(6))
    el.append(section('10.3 Owner Details'))
    el.append(body('Opening an owner reveals:'))
    el.extend(bullet_list([
        '<b>Subscription</b> — plan (free/starter/pro/enterprise), status, and expiry date.',
        '<b>Limits</b> — maximum products and employees the owner may register.',
        '<b>Branding</b> — white-label configuration: store name, tagline, logo upload, and the two brand colors.',
    ]))
    el.append(spacer(6))
    el.append(section('10.4 Owner Password Management'))
    el.extend(bullet_list([
        '<b>Reset Password</b> — resets to the default and forces a change on next login.',
        '<b>Set Password</b> — assigns an explicit password.',
        '<b>Force Password Change</b> — clears <font face="Mono">password_changed_at</font> so the owner must change it.',
        '<b>Unlock Account</b> — clears <font face="Mono">locked_until</font> after a 30-minute lockout.',
        '<b>Passwords Status</b> — overview of every owner\'s password state (changed / needs change / expired).',
    ]))
    el.append(spacer(6))
    el.append(section('10.5 Superadmin Inbox'))
    el.append(body('The superadmin communicates with owners through the <b>Inbox</b> (owner ↔ superadmin conversations). Conversations appear in real time with unread badges.'))
    el.append(spacer(6))
    el.append(section('10.6 Home Content Editor'))
    el.append(body('The <b>Home Content</b> page (route <font face="Mono">/superadmin/home-content</font>) edits the platform-wide text shown to visitors and customers: the directory landing copy (<font face="Mono">dir*</font> keys) and every white-label storefront hero/badge/count string. Content is stored as one <font face="Mono">home_content</font> setting (type <font face="Mono">json</font>) holding <font face="Mono">en</font> and <font face="Mono">sw</font> objects.'))
    el.append(body('Fields containing <font face="Mono">{count}</font> (e.g. <font face="Mono">productsCount</font>, <font face="Mono">dirProductsCount</font>, <font face="Mono">dirNewArrivals</font>) are templates: the placeholder is replaced at render time with the real product count. The public <font face="Mono">GET /settings/home-content</font> returns stored values merged over the seeded defaults, so the storefront never sees empty strings; empty stored values fall back to the i18n keys (<font face="Mono">home.*</font> / <font face="Mono">directory.*</font>). Only superadmins can write via <font face="Mono">PUT /superadmin/settings/home-content</font>; keys outside the whitelist are stripped.'))
    el.append(spacer(6))
    el.append(section('10.6 Superadmin Password Lifecycle'))
    el.append(body('The default superadmin password is <b>SuperAdmin@2026</b>. A scheduled command (<font face="Mono">php artisan superadmin:reset-password</font>) auto-resets it every <b>6 months</b>; login and profile responses expose <font face="Mono">superadmin_password_expired</font> so the UI can prompt for a change.'))
    el.append(PageBreak())
    return el


def ch_security():
    el = []
    el.append(chapter('11. Security Measures'))
    el.append(hr())
    el.append(section('11.1 API Rate Limiting'))
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
    el.append(section('11.2 Passwords & Lockout'))
    el.extend(bullet_list([
        'Complexity enforced at the API level (8+ chars; upper, lower, number, symbol).',
        'Accounts lock after <b>5 failed attempts</b> for <b>30 minutes</b>.',
        'Passwords older than <b>3 days</b> trigger a mandatory change; superadmin password resets every 6 months.',
    ]))
    el.append(spacer(6))
    el.append(section('11.3 Tenant Isolation'))
    el.extend(bullet_list([
        'Every owner-scoped controller resolves the tenant through <font face="Mono">request()->ownerId()</font> and scopes all queries to it.',
        'Cross-tenant access attempts fail fast: owner-scoped findOrFail returns 404, guard checks return 403.',
        'Employees are resolved to their branch owner before any owner-scoped data is served.',
    ]))
    el.append(spacer(6))
    el.append(section('11.4 File Uploads'))
    el.extend(bullet_list([
        'Employee documents accept only <b>PDF, JPG, PNG, DOC, DOCX</b>, up to <b>20 MB</b> each; stored under <font face="Mono">employee-documents/</font>.',
        'Supplier documents and product/branding images have per-type size limits and category validation.',
        'Downloads are served only through authenticated, owner-scoped endpoints.',
    ]))
    el.append(spacer(6))
    el.append(section('11.5 JSON Error Rendering'))
    el.append(body('The <font face="Mono">shouldRenderJsonWhen api/*</font> rule guarantees every API error — validation 422s, 401/403, 404s, 429s, and 500s — is returned as JSON, so the SPA always receives parseable responses.'))
    el.append(PageBreak())
    return el


def ch_analytics():
    el = []
    el.append(chapter('12. Analytics & AI Insights'))
    el.append(hr())
    el.append(section('Sales Analytics'))
    el.append(body('<font face="Mono">AnalyticsController::sales()</font> accepts <font face="Mono">?months=12</font> and computes, in parallel: monthly sales, monthly items sold, monthly profit, and monthly cancellations. It returns a gap-free month list plus <b>category_breakdown</b>, <b>top_products</b>, and a <b>summary</b> (total revenue, profit, orders, items sold, average order value, profit margin, revenue and order growth).'))
    el.append(spacer(6))
    el.append(section('AI Suggestions'))
    el.append(body('The owner dashboard can call <font face="Mono">POST /analytics/ai-suggestions</font> with the sales payload. The backend builds a Tanzania-specific business prompt and calls <b>Gemini 2.0 Flash</b> (temperature 0.7, max 2048 tokens, configured via <font face="Mono">GEMINI_API_KEY</font>). If the AI response is unavailable, rule-based fallback suggestions are returned.'))
    el.append(body('Suggestions are bilingual (<font face="Mono">title_sw/title_en</font>, <font face="Mono">description_sw/description_en</font>) with a priority (high/medium/low), category (inventory/pricing/marketing/growth/operations), expected impact, and a <font face="Mono">source</font> of "ai" or "fallback".'))
    el.append(spacer(6))
    el.append(section('Accounting AI Suggestions'))
    el.append(body('The accounting module has a second Gemini integration (<font face="Mono">AiSuggestionService</font>): after generating a monthly report, owners can request up to 8 bilingual accounting suggestions (revenue/expenses/compliance/cash flow/inventory/tax/growth) with prior-period trend context. Results persist on <font face="Mono">accounting_reports.suggestions</font>.'))
    el.append(PageBreak())
    return el


def ch_request_cycles():
    el = []
    el.append(chapter('13. End-to-End Request Cycles'))
    el.append(hr())
    el.append(body('This chapter walks through the complete journeys through both codebases, from a page action in the SPA to the database and back — and the auto-journaling the system performs at each step.'))
    el.append(spacer(8))
    el.append(section('13.1 Generic Request Pipeline'))
    el.extend(code_block([
        'Browser (Vue page) → store action → src/api module → axios instance',
        '  → interceptor adds Bearer token + X-Business-Id → HTTP request',
        '  → public/index.php → bootstrap/app.php → router (/api prefix)',
        '  → throttle:api → auth:sanctum (Bearer token) → role middleware',
        '  → Controller → validates → Service (accounting) → Eloquent models',
        '  → SQLite (dev) / MySQL (prod) → JSON response',
        '  → axios response interceptor → page renders; 401 → clear token → /login',
    ]))
    el.append(spacer(8))
    el.append(section('13.2 Authentication Cycle'))
    el.extend(bullet_list([
        '<b>Login</b>: LoginPage → authStore.login() → authApi.login() → POST /auth/login → AuthController@login validates, checks lockout (423) and attempts, verifies the hash, issues a Sanctum token, eager-loads role relations, returns { token, user, must_change_password, superadmin_password_expired }. The store persists only the token.',
        '<b>Forced change</b>: if must_change_password, StoreLayout mounts ChangePasswordModal → POST /auth/change-password → updates the hash + password_changed_at.',
        '<b>Restore</b>: on any page load the router guard calls authStore.fetchProfile() → GET /auth/profile when a token exists.',
    ]))
    el.append(spacer(8))
    el.append(section('13.3 Storefront Browse Cycle'))
    el.extend(bullet_list([
        '<b>Directory</b>: DirectoryPage → businessApi.list() → GET /businesses (public) → BusinessController@index presents each active business with store_name, brand colors, and product counts.',
        '<b>Open a store</b>: the URL becomes /:businessSlug → StoreLayout resolves the business via businessStore.loadBySlug() (GET /businesses/by-slug/{slug}) and applies branding as CSS variables.',
        '<b>Catalog</b>: HomePage/ProductListPage → productStore.fetchProducts() → GET /products?business=&lt;slug&gt; → ProductController@index scopes by Tenant::bySlug and returns paginated products with variants + inventory.',
        '<b>Detail</b>: ProductDetailPage → GET /products/{slug} → variant picker and stock read from the response.',
    ]))
    el.append(spacer(8))
    el.append(section('13.4 Cart Cycle'))
    el.append(body('The cart is simply an Order row with status pending_payment. CartController::getOrCreateCart() does firstOrCreate per user. Every cart mutation recalculaates subtotal and total server-side and returns the fresh items.'))
    el.extend(bullet_list([
        'Add: CartPage/ProductCard → cartStore.addItem() → POST /cart { product_variant_id, quantity } → stock check (422 "Insufficient stock") → line added or quantity increased.',
        'Update/remove/clear: PUT/DELETE /cart routes keep items and totals in sync with the backend.',
    ]))
    el.append(spacer(8))
    el.append(section('13.5 Checkout & Payment Cycle'))
    el.extend(bullet_list([
        'CheckoutPage loads addresses, payment providers, and calls POST /shipping/calculate for the estimate.',
        'Placing the order: orderApi.create() → POST /orders → OrderController@store validates, loads the cart, applies delivery cost (default 5000 TSh when delivery is required) and the optional winga fee (subtotal × rate%), updates the cart row to status pending with an ORD- number, returns the fresh order.',
        'Payment: paymentApi.initiate() → POST /payments/initiate → PaymentController@initiate creates a pending payment. <b>ClickPesa and cash are auto-confirmed</b>: payment completed, order.markAsPaid() (status paid + inventory decremented). Other mobile-money providers await an employee confirmation or the webhook.',
        'Employee confirmation: OrderManagementPage → orderManageApi.updateStatus(order, "paid") → OrderController::confirmPaidOrder runs the full auto-journal chain (see §13.6).',
    ]))
    el.append(spacer(8))
    el.append(section('13.6 Order Lifecycle & Auto-Journaling'))
    el.append(body('OrderController@updateStatus is the heart of the system. Inside a database transaction with a row lock it transitions statuses and triggers accounting. Only the paid and cancelled transitions post journals; shipping transitions are plain status updates.'))
    el.extend(code_block([
        'pending_payment (cart) ──checkout──▶ pending',
        'pending ──confirm──▶ paid   ← confirmPaidOrder:',
        '   1. decrement each variant inventory',
        '   2. write sale InventoryTransactions',
        '   3. compute COGS (Σ qty × cost_price; throws if missing)',
        '   4. postSale journal: DR Cash 1020  /  CR Sales 4010',
        '                        (VAT Output 2500 + Shipping 4020 + winga accrual 5110/2100)',
        '                        CR Inventory 1200 / DR COGS 5010',
        '   5. createCommission (employee, profit × rate)',
        '   6. createWingaCommission (fee − TRA TDS 5%, net payable)',
        'paid ──▶ processing ──▶ shipped ──▶ delivered   (plain updates + tracking)',
        'paid/processing ──cancel──▶ cancelled ← reversePaidOrder:',
        '   restock inventory + return transactions + reverseSale +',
        '   reverseCommissions (clawback paid, delete pending) +',
        '   reverseWingaCommissions',
        'any item return ──▶ returnItems:',
        '   restock, write return transactions, postReturn partial journal,',
        '   adjustCommissionForReturn + adjustWingaCommissionForReturn;',
        '   fully returned orders auto-cancel',
    ]))
    el.append(spacer(8))
    el.append(section('13.7 Employee Cycle'))
    el.extend(bullet_list([
        'Employee login → EmployeeDashboard (stats + branch-scoped accounting issues).',
        'Order desk: OrderManagementPage → orderManageApi → updateStatus, updateDelivery (tracking), returnItems.',
        'Customers: CustomerManagementPage → customerApi (toggle status, delete).',
        'Support: SupportInboxPage → supportApi.reply/updateStatus.',
        'Earnings: EmployeeEarningsPage → commissionApi.getMyEarnings → GET /commissions/my-earnings.',
        'Inbox: EmployeeInboxPage → conversationApi (owner_employee threads).',
    ]))
    el.append(spacer(8))
    el.append(section('13.8 Owner Cycle — HR, Inventory, Procurement'))
    el.extend(bullet_list([
        'Employees: EmployeeManagementPage → employeeApi.create sends multipart form-data (guarantors + documents). Default password = strtoupper(name); employee_code EMP-xxxxxx.',
        'Inventory: InventoryManagementPage → inventoryApi.adjust → InventoryController@adjust posts the adjustment journal (1200/5100/3010) and triggers the low-stock scan.',
        'Purchase orders: PurchaseOrderPage → purchaseOrderApi → PurchaseOrderController. Receiving (POST /purchase-orders/{id}/receive) increments stock, writes purchase transactions, and posts DR Inventory 1200 / CR Cash 1020.',
        'Suppliers: SupplierManagementPage → supplierApi CRUD + documents.',
        'Stock alerts: StockAlertsPage → stockAlertApi acknowledge/resolve.',
    ]))
    el.append(spacer(8))
    el.append(section('13.9 Accounting Cycle'))
    el.extend(bullet_list([
        'Chart of accounts: ChartOfAccountsPage → accountApi; system accounts (is_system) are protected from edit/delete.',
        'Manual entries: JournalEntryCreatePage → journalApi.create (draft, must balance), then post or void from the detail page.',
        'Live statements: TrialBalance/ProfitLoss/BalanceSheet/GeneralLedger pages → accountingReportApi; general-ledger requires an account_id.',
        'Generated reports: ReportsPage → generate-monthly/yearly; AiSuggestions persist to the report.',
        'Accounting issues: AccountingDashboardPage → accountingIssuesApi.get → AccountingIssuesController bucket scan (unconfirmed payments, pending deliveries, missing cost prices, drafts, voids, pending commissions, unbalanced trial balance, low stock).',
    ]))
    el.append(spacer(8))
    el.append(section('13.10 Winga Commission Cycle'))
    el.extend(bullet_list([
        'Owner registers a winga (name, TIN/NIDA, rate) via WingaManagementPage.',
        'At checkout the customer\'s order stores winga_id + winga_fee.',
        'On payment confirmation, createWingaCommission() accrues gross/fee, withholding tax (5%), net.',
        'Owner pays (WingaCommissionPage → wingaCommissionApi.pay/payAll) → payout journal: DR Winga Payable 2100 / CR Cash 1020 (net) / CR WHT Payable 2120 (TDS).',
    ]))
    el.append(spacer(8))
    el.append(section('13.11 Supplier Portal Cycle'))
    el.extend(bullet_list([
        'Supplier login → SupplierPortalPage → supplierPortalApi.getProfile() matches the user email to a Supplier record.',
        'GET /supplier-portal/purchase-orders lists the supplier\'s POs; supplierUpdateStatus moves draft → ordered → received (received also stamps received_date).',
    ]))
    el.append(spacer(8))
    el.append(section('13.12 Superadmin Onboarding Cycle'))
    el.extend(bullet_list([
        'SuperadminDashboard → superadminApi.getStats() → GET /superadmin/stats.',
        'Create owner → POST /superadmin/owners → default password returned; OwnerProfile created (trial, starter, 50 products, 5 employees) and a Business row seeded.',
        'OwnerDetailPage exposes subscription/limits/password management; BrandingPage → PUT branding + POST branding-logo.',
    ]))
    el.append(spacer(8))
    el.append(section('13.13 Messaging & Read-Receipts Cycle'))
    el.extend(bullet_list([
        'Threads: conversationApi.index / create → GET|POST /conversations; inbox pages list open threads (sidebar) with unread dots (hasUnread = any incoming message with is_read = false).',
        'Send: inbox page → conversationApi.sendMessage → POST /conversations/{id}/messages → ConversationController@sendMessage stores the row (is_read = false) and returns it; the sender renders a grey double tick.',
        'Read: recipient opens the thread → GET /conversations/{id} → show() validates the role/tenant then bulk-updates incoming messages (sender_id != user) to is_read = true before returning the conversation.',
        'Receipt delivery: every inbox page polls GET /conversations and GET /conversations/{id} every 15 s; the sender\'s grey tick turns blue once the recipient has viewed the message. No websockets are used.',
    ]))
    el.append(PageBreak())
    return el


def ch_docs():
    el = []
    el.append(chapter('14. Documentation & Diagrams'))
    el.append(hr())
    el.append(section('PDF Documents (docs/)'))
    el.append(info_table(header=['File', 'Audience', 'Notes'], col_widths=[180, 110, 190], rows=[
        ('User_Manual_EN.pdf', 'End users', 'English user manual, 24 chapters'),
        ('User_Manual_SW.pdf', 'End users', 'Swahili user manual, 24 chapters'),
        ('Supplier_Manual.pdf', 'Suppliers', 'Supplier portal manual'),
        ('Developer_Documentation.pdf', 'Developers & admins', 'This document (v2.3)'),
    ]))
    el.append(spacer(8))
    el.append(section('System Diagrams (docs/)'))
    el.append(info_table(header=['Diagram', 'Contents'], col_widths=[160, 320], rows=[
        ('ERD.drawio (+ PDF)', 'All tables and relationships, crow\'s foot notation'),
        ('ClassDiagram.drawio (+ PDF)', 'Model classes with attributes, methods, and relationships'),
        ('UseCase.drawio (+ PDF)', 'Actors and use cases across all roles'),
        ('SequenceDiagrams.drawio (+ PDF)', '7 flows: customer checkout, order processing, branch + employee management, accounting, commission, inventory, purchase orders'),
    ]))
    el.append(spacer(8))
    el.append(section('Generator Scripts'))
    el.extend(bullet_list([
        mono('generate_manual.py') + ' — user manuals (EN + SW) using ReportLab.',
        mono('generate_supplier_manual.py') + ' — supplier portal manual.',
        mono('generate_dev_doc.py') + ' — this developer documentation.',
        mono('generate_diagrams.py') + ' — drawio diagram generator.',
    ]))
    el.append(PageBreak())
    return el


def ch_commands():
    el = []
    el.append(chapter('15. Development Commands & Environment'))
    el.append(hr())
    el.append(section('15.1 Local Development vs Production'))
    el.append(body('The same repositories serve both environments. Local development uses the Vite dev server against the local Laravel API; deployment builds the frontend with the production API URL. The two never interfere because the frontend URL is a build-time environment variable.'))
    el.append(info_table(header=['Concern', 'Local development', 'Production'], col_widths=[120, 180, 180], rows=[
        ('Frontend URL', mono(DEV_FE), mono(PROD_FE)),
        ('API base (VITE_API_URL)', mono(DEV_API), mono(PROD_API)),
        ('Backend host', 'php artisan serve (localhost:8000)', 'Laravel Cloud (api.electroshophub.online)'),
        ('Database', 'SQLite (database/database.sqlite)', 'Provisioned database on Laravel Cloud'),
        ('File storage', 'local disk', 'S3 (FILESYSTEM_DISK=s3)'),
        ('Environment file', '.env (untracked, git-ignored)', 'Environment variables on Laravel Cloud'),
    ]))
    el.append(spacer(8))
    el.append(section('15.2 Frontend (erp-electronics/)'))
    el.append(info_table(header=['Command', 'Purpose'], col_widths=[240, 240], rows=[
        ('npm install', 'Install dependencies (Node ^22.18 or >= 24.12)'),
        ('npm run dev', 'Start Vite dev server (port 5173)'),
        ('npm run build', 'Production build'),
        ('npm run lint', 'Run oxlint + eslint'),
        ('npm run format', 'Format with oxfmt'),
        ('npm run test:unit', 'Run Vitest unit tests'),
        ('npm run test:e2e', 'Run Playwright end-to-end tests'),
    ]))
    el.append(spacer(8))
    el.append(section('15.3 Backend (erp-electronics-api/)'))
    el.append(info_table(header=['Command', 'Purpose'], col_widths=[280, 200], rows=[
        ('composer install', 'Install PHP dependencies'),
        ('php artisan serve', 'Start dev server (port 8000)'),
        ('php artisan migrate', 'Run migrations'),
        ('php artisan migrate:fresh --seed', 'Reset database and re-seed'),
        ('php artisan report:daily', 'Generate daily report'),
        ('php artisan orders:cleanup-unpaid', 'Clean up unpaid orders'),
        ('php artisan superadmin:reset-password', 'Reset superadmin password if 6 months elapsed'),
        ('php artisan accounting:generate-reports --with-suggestions', 'Generate monthly reports with AI suggestions'),
        ('php artisan accounting:close-year', 'Post year-end closing entries'),
        ('php artisan schedule:work', 'Run the scheduler'),
        ('php artisan route:list', 'List routes'),
        ('php artisan test', 'Run the test suite'),
    ]))
    el.append(spacer(8))
    el.append(section('15.4 Environment Variables'))
    el.extend(code_block([
        '# Frontend (.env — untracked, local only)',
        'VITE_API_URL=http://localhost:8000/api',
        '',
        '# Production build sets instead:',
        'VITE_API_URL=https://api.electroshophub.online/api',
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
    el.append(spacer(8))
    el.append(section('15.5 Documentation Regeneration'))
    el.extend(bullet_list([
        'python3 generate_dev_doc.py        → docs/Developer_Documentation.pdf',
        'python3 generate_manual.py         → docs/User_Manual_EN.pdf + User_Manual_SW.pdf',
        'python3 generate_supplier_manual.py → docs/Supplier_Manual.pdf',
        'python3 generate_diagrams.py       → drawio files (open + export to PDF in diagrams.net)',
    ]))
    el.append(PageBreak())
    return el


def ch_deployment():
    el = []
    el.append(chapter('16. Deployment'))
    el.append(hr())
    el.append(section('16.1 Production Endpoints'))
    el.append(info_table(header=['Service', 'URL', 'How served'], col_widths=[100, 190, 190], rows=[
        ('Frontend', mono(PROD_FE), 'Static SPA build (dist/) with SPA redirects'),
        ('Backend API', mono(PROD_API), 'Laravel Cloud, custom domain api.electroshophub.online'),
        ('Health check', mono('https://api.electroshophub.online/up'), 'GET /up returns 200 when the app is healthy'),
    ]))
    el.append(spacer(6))
    el.append(section('16.2 Backend — Laravel Cloud'))
    el.extend(bullet_list([
        'Pushing to the <b>main</b> branch triggers an automatic deployment.',
        'Custom domain <b>api.electroshophub.online</b> is mapped to the production environment (environment id env-a2578b2b-6a5c-4d19-9c2e-d927b4edafde; app id app-a2578b29-e3ec-4754-a717-a6a208f4f512).',
        'File storage uses S3 (FILESYSTEM_DISK=s3) with the AWS_* variables set on Laravel Cloud.',
        'Deployment verification: <font face="Mono">cloud command:run &lt;env-id&gt; --cmd="php artisan test" -n</font>.',
    ]))
    el.append(spacer(6))
    el.append(section('16.3 Frontend — Production Build'))
    el.extend(bullet_list([
        'Build with the production API URL: set <font face="Mono">VITE_API_URL=https://api.electroshophub.online/api</font> at build time, then run <font face="Mono">npm run build</font>.',
        'Publish the <font face="Mono">dist/</font> directory to the frontend host serving <b>electroshophub.online</b> with SPA redirects to index.html.',
        'The API accepts the frontend origin via CORS (<b>allowed_origins: *</b>).',
    ]))
    el.append(spacer(6))
    el.append(section('16.4 Keeping Local Development Running'))
    el.extend(bullet_list([
        'The local <font face="Mono">.env</font> keeps <font face="Mono">VITE_API_URL=http://localhost:8000/api</font>; it is untracked so production builds never pick it up.',
        'Run the backend with <font face="Mono">php artisan serve</font> (or <font face="Mono">php artisan schedule:work</font> for scheduled tasks) and the frontend with <font face="Mono">npm run dev</font>.',
        'Local SQLite means migrations can be reset freely (<font face="Mono">php artisan migrate:fresh --seed</font>) without touching production data.',
        'Production is only affected by a deploy — nothing local touches the live environment.',
    ]))
    el.append(spacer(6))
    el.append(note('Rate-limit keys are IP-based, so an entire office sharing one public IP shares the 5/min login budget. This is intentional to block brute-force traffic.'))
    el.append(PageBreak())
    return el


def ch_gotchas():
    el = []
    el.append(chapter('17. Implementation Notes & Known Gotchas'))
    el.append(hr())
    el.append(info_table(header=['#', 'Note'], col_widths=[30, 450], rows=[
        ('1', 'The branch routes are documented "owner only" but are not wrapped in the owner middleware — any authenticated user can call them. UI gates them by role.'),
        ('2', 'branch_id on orders/employees and winga_id on orders are plain unsigned columns with no foreign key constraints.'),
        ('3', 'journal_entries.source_type is a foreignId column without an actual FK constraint.'),
        ('4', 'winga_wht_rate is seeded in two migrations (2026_07_31_000004 and 2026_08_01_000007); the first migration\'s down() does not remove it.'),
        ('5', 'Order status enum: pending, pending_payment, inactive, paid, processing, shipped, delivered, cancelled (default pending_payment).'),
        ('6', 'Tenant resolution depends on the X-Business-Id header with fallback to the first owned business; ownerId falls back to the owner\'s own user id for legacy installs.'),
        ('7', 'OwnerProfile productCount()/employeeCount() are global counts, not tenant-scoped — treated as approximate.'),
        ('8', 'The payments webhook currently has no signature validation (documented TODO).'),
        ('9', 'PaymentController auto-confirmation path (ClickPesa/cash) marks orders paid without posting a journal entry — only the OrderController::updateStatus path posts journals.'),
        ('10', 'OrderItem.returned_quantity is used directly in OrderController::returnItems but is not in the model\'s fillable list (updated via update()).'),
        ('11', 'Sanctum tokens have no expiration by default; sessions are protected by the frontend idle timeout and server-side token revocation on logout.'),
    ]))
    el.append(spacer(12))
    el.append(section('Changelog — 2026-08-03'))
    el.append(body('<b>Product form translations fixed</b>: the owner product create/edit routes referenced <font face="Mono">productForm.updateProduct</font>, <font face="Mono">createProduct</font>, <font face="Mono">updatedSuccessfully</font> and <font face="Mono">createdSuccessfully</font> keys that were missing from both <font face="Mono">en.json</font> and <font face="Mono">sw.json</font>, so vue-i18n rendered the raw key. All four keys were added to both locale files; the Swahili submit label now reads <b>"Sahihisha Bidhaa"</b> and the success toast <b>"Bidhaa imesahihishwa!"</b>.'))
    el.append(spacer(10))
    el.append(body('<b>DB-driven home content</b>: storefront (HomePage) and directory (DirectoryPage) copy moved from hardcoded i18n keys to a superadmin-editable <font face="Mono">home_content</font> setting (EN + SW, seeded defaults, 44 keys). New <font face="Mono">SettingsController@homeContent</font> / <font face="Mono">updateHomeContent</font> endpoints and the <font face="Mono">HomeContentPage</font> editor were added; render-time <font face="Mono">{count}</font> placeholders are substituted with live product counts, and empty stored values fall back to the i18n keys. Backend-only endpoints: <font face="Mono">GET /settings/home-content</font> (public), <font face="Mono">PUT /superadmin/settings/home-content</font> (superadmin).'))
    el.append(spacer(10))
    el.append(body('<b>Conversation & message deletion</b>: chat threads can now be deleted (<font face="Mono">DELETE /conversations/{conversation}</font>) and individual messages removed (<font face="Mono">DELETE /conversations/{conversation}/messages/{messageId}</font>), scoped to the participants. The API reference (§9.5) and controller listing were updated; route count revised from 175 to 179.'))
    el.append(spacer(12))
    el.append(hr())
    el.append(Paragraph('<b>ERP Electronics Store</b> — Developer &amp; Technical Documentation v2.3 — August 2026', sFooter))
    el.append(Paragraph('For internal development and administration use only.', sFooter))
    return el


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
        ('4.', 'Repository Layout'),
        ('5.', 'Frontend Deep Dive — Every File'),
        ('6.', 'Backend Deep Dive — Every File'),
        ('7.', 'Database Schema & Models'),
        ('8.', 'Authentication & Authorization'),
        ('9.', 'API Reference — All 179 Routes'),
        ('10.', 'Superadmin Module'),
        ('11.', 'Security Measures'),
        ('12.', 'Analytics & AI Insights'),
        ('13.', 'End-to-End Request Cycles'),
        ('14.', 'Documentation & Diagrams'),
        ('15.', 'Development Commands & Environment'),
        ('16.', 'Deployment'),
        ('17.', 'Implementation Notes & Known Gotchas'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    el += ch_document_control()
    el += ch_overview()
    el += ch_stack()
    el += ch_repo_layout()
    el += ch_frontend()
    el += ch_backend()
    el += ch_schema()
    el += ch_auth()
    el += ch_api()
    el += ch_superadmin()
    el += ch_security()
    el += ch_analytics()
    el += ch_request_cycles()
    el += ch_docs()
    el += ch_commands()
    el += ch_deployment()
    el += ch_gotchas()

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
