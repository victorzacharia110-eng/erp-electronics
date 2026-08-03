#!/usr/bin/env python3
"""Generate draw.io diagrams using native draw.io features: tables, swimlanes, etc.
draw.io uses its own lenient XML parser — raw HTML in value attributes is fine."""

import os
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBd', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

RED = HexColor('#e74c3c')
DARK = HexColor('#2c3e50')
LGRAY = HexColor('#f5f5f5')
GRAY = HexColor('#888888')
styles = getSampleStyleSheet()

def ms(n, **k):
    return ParagraphStyle(n, parent=styles['Normal'], fontName=k.pop('fontName', 'DejaVu'), **k)

sT = ms('dT', fontSize=22, fontName='DejaVuBd', textColor=DARK, spaceAfter=10, leading=28)
sS = ms('dS', fontSize=14, fontName='DejaVuBd', textColor=RED, spaceAfter=6, spaceBefore=12, leading=18)
sB = ms('dB', fontSize=10, textColor=HexColor('#333333'), alignment=TA_JUSTIFY, leading=15, spaceAfter=6)
sL = ms('dL', fontSize=10, textColor=HexColor('#333333'), leading=14, leftIndent=20, spaceAfter=3)
sN = ms('dN', fontSize=9, textColor=GRAY, leading=13, spaceAfter=4, leftIndent=10)
sTH = ms('dTH', fontSize=9, fontName='DejaVuBd', textColor=white, leading=12)
sTC = ms('dTC', fontSize=9, textColor=HexColor('#333333'), leading=12)
sF = ms('dF', fontSize=8, textColor=GRAY, alignment=TA_CENTER)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd'), spaceAfter=8, spaceBefore=8)
def bl(i): return [Paragraph(f'• {x}', sL) for x in i]
def bd(t): return Paragraph(t, sB)
def sc(t): return Paragraph(t, sS)
def nt(t): return Paragraph(f'<i>{t}</i>', sN)
def sp(h=6): return Spacer(1, h)
def itbl(rows, cw=None):
    if cw is None: cw = [140, 330]
    d = [[Paragraph(f'<b>{r[0]}</b>', sTC), Paragraph(str(r[1]), sTC)] for r in rows]
    t = Table(d, colWidths=cw)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),LGRAY),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.5,HexColor('#dddddd'))]))
    return t

def apn(c, d):
    c.saveState(); c.setFont('DejaVu', 8); c.setFillColor(GRAY); c.drawCentredString(A4[0]/2, 20*mm, f'Page {d.page}'); c.restoreState()

def bpdf(el, fn):
    od = os.path.join(os.path.dirname(__file__), 'docs'); os.makedirs(od, exist_ok=True)
    p = os.path.join(od, fn)
    doc = SimpleDocTemplate(p, pagesize=A4, topMargin=25*mm, bottomMargin=25*mm, leftMargin=20*mm, rightMargin=20*mm)
    doc.build(el, onFirstPage=apn, onLaterPages=apn); print(f'  PDF: {p}')


# ═══════════════════════════════════════════════════════════════════════════════
#  DRAW.IO HELPER — Native features with proper contrast & visible edges
# ═══════════════════════════════════════════════════════════════════════════════

def xe(s):
    """XML-escape a string for use in XML attribute values."""
    return html.escape(str(s), quote=True)

def darken(hex_color, factor=0.7):
    """Darken a hex color by multiplying RGB channels by factor."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return '#{:02x}{:02x}{:02x}'.format(int(r*factor), int(g*factor), int(b*factor))


class D:
    def __init__(s, title, w=3600, h=2800):
        s.c = []; s.n = 2; s.t = title; s.w = w; s.h = h

    def _id(s):
        s.n += 1; return str(s.n)

    def text(s, x, y, t, sz=14, bold=True, w=400, h=30, color='#000000', bgColor=None, strokeColor=None):
        cid = s._id()
        fs = 1 if bold else 0
        bg = f'fillColor={bgColor};' if bgColor else 'fillColor=none;'
        sc = f'strokeColor={strokeColor};' if strokeColor else 'strokeColor=none;'
        st = f'text;html=1;{sc}{bg}align=center;verticalAlign=middle;fontSize={sz};fontStyle={fs};fontColor={color};'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(t)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n        </mxCell>')
        return cid

    def table(s, x, y, name, cols, fill='#dae8fc', stroke='#6c8ebf', cw=220):
        """Native draw.io table with darkened header (white text) + light body rows."""
        cid = s._id()
        rh = 32
        hdr = 38
        total_h = hdr + len(cols) * rh
        hdr_fill = darken(fill, 0.55)
        st = f'shape=table;startSize={hdr};container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;fillColor={fill};strokeColor={stroke};strokeWidth=2;fontColor=#ffffff;fontSize=15;swimlaneLine=1;'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(name)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="{cw}" height="{total_h}" as="geometry"/>\n        </mxCell>')
        for i, (cn, ct, pk) in enumerate(cols):
            rid = s._id()
            ry = hdr + i * rh
            alt_fill = '#ffffff' if i % 2 == 0 else lighten(fill)
            s.c.append(f'        <mxCell id="{rid}" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor={alt_fill};collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;strokeColor={stroke};" vertex="1" parent="{cid}">\n          <mxGeometry y="{ry}" width="{cw}" height="{rh}" as="geometry"/>\n        </mxCell>')
            nid = s._id()
            pk_s = 'fontStyle=1;fontColor=#c0392b;' if pk else ''
            s.c.append(f'        <mxCell id="{nid}" value="{xe(cn)}" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;strokeColor=inherit;fontSize=12;align=left;fontColor=#111111;{pk_s}" vertex="1" parent="{rid}">\n          <mxGeometry width="{cw*0.55}" height="{rh}" as="geometry"><mxRectangle width="{cw*0.55}" height="{rh}" as="alternateBounds"/></mxGeometry>\n        </mxCell>')
            tid = s._id()
            s.c.append(f'        <mxCell id="{tid}" value="{xe(ct)}" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;strokeColor=inherit;fontStyle=5;fontSize=11;align=left;fontColor=#333333;" vertex="1" parent="{rid}">\n          <mxGeometry x="{cw*0.55}" width="{cw*0.45}" height="{rh}" as="geometry"><mxRectangle width="{cw*0.45}" height="{rh}" as="alternateBounds"/></mxGeometry>\n        </mxCell>')
        return cid

    def edge(s, src, tgt, label='', ex=0.5, ey=1, ix=0.5, iy=0, dashed=False, color='#333333', labelBg=None):
        eid = s._id()
        d = 'dashed=1;dashPattern=8 4;' if dashed else ''
        bg = labelBg if labelBg else '#ffffff'
        label_style = f'labelBackgroundColor={bg};' if label else ''
        st = f'relative=1;orthogonalLoop=1;jettySize=auto;html=1;exitX={ex};exitY={ey};entryX={ix};entryY={iy};{d}strokeColor={color};strokeWidth=2;fontColor=#000000;fontSize=15;fontStyle=1;endArrow=classic;endFill=1;endSize=8;{label_style}'
        val = f' value="{xe(label)}"' if label else ''
        s.c.append(f'        <mxCell id="{eid}"{val} style="{st}" edge="1" source="{src}" target="{tgt}" parent="1">\n          <mxGeometry relative="1" as="geometry"/>\n        </mxCell>')
        return eid

    def stick(s, x, y, label, h=100):
        cid = s._id()
        st = f'shape=actor;whiteSpace=wrap;html=1;fillColor=#2c3e50;strokeColor=#1a252f;fontSize=16;fontStyle=1;verticalLabelPosition=bottom;verticalAlign=top;fontColor=#111111;fontStyle=1;'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(label)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="40" height="{h}" as="geometry"/>\n        </mxCell>')
        return cid

    def oval(s, x, y, t, w=210, h=56, fill='#fff2cc', stroke='#333333'):
        cid = s._id()
        st = f'shape=ellipse;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=2;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;fontColor=#111111;'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(t)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n        </mxCell>')
        return cid

    def lifeline(s, x, y, label, h=400):
        cid = s._id()
        st = f'shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=0;collapsible=0;recursiveResize=0;outlineConnect=0;size=50;fillColor=#2c3e50;strokeColor=#1a252f;fontSize=15;fontStyle=1;fontColor=#ffffff;'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(label)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="100" height="{h}" as="geometry"/>\n        </mxCell>')
        return cid

    def msg(s, src, tgt, label, y, dashed=False):
        eid = s._id()
        d = 'dashed=1;dashPattern=8 8;' if dashed else ''
        st = f'html=1;verticalAlign=bottom;endArrow=open;endFill=0;{d}exitX=0.5;exitY=0;entryX=0.5;entryY=0;strokeColor=#2c3e50;strokeWidth=2;fontColor=#111111;fontSize=13;fontStyle=0;'
        s.c.append(f'        <mxCell id="{eid}" value="{xe(label)}" style="{st}" edge="1" source="{src}" target="{tgt}" parent="1">\n          <mxGeometry y="{y}" relative="1" as="geometry"/>\n        </mxCell>')
        return eid

    def boundary(s, x, y, w, h, label):
        cid = s._id()
        st = f'shape=mxgraph.basic.rect;fillColor=none;strokeColor=#2c3e50;strokeWidth=3;rounded=1;arcSize=3;fontSize=19;fontStyle=1;verticalAlign=top;align=center;fontColor=#2c3e50;'
        s.c.append(f'        <mxCell id="{cid}" value="{xe(label)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n        </mxCell>')
        return cid

    def xml(s):
        cells = '\n'.join(s.c)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="{xe(s.t)}" id="d1">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{s.w}" pageHeight="{s.h}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{cells}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    def save(s, fn):
        od = os.path.join(os.path.dirname(__file__), 'docs'); os.makedirs(od, exist_ok=True)
        p = os.path.join(od, fn)
        with open(p, 'w') as f: f.write(s.xml())
        print(f'  DrawIO: {p}')


def lighten(hex_color, amount=0.15):
    """Lighten a hex color."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


# ═══════════════════════════════════════════════════════════════════════════════
#  1. ERD — Native tables with clear relationships
# ═══════════════════════════════════════════════════════════════════════════════

def gen_erd():
    d = D('ElectroShop ERP — Entity Relationship Diagram', w=5200, h=4000)

    d.text(1800, 15, 'ElectroShop ERP — Entity Relationship Diagram', sz=24, w=1600, bold=True, color='#2c3e50')

    # Section labels with subtle background
    d.text(80, 60, 'USERS & PROFILES', sz=15, bold=True, w=260, color='#1a252f', bgColor='#eaf2f8', strokeColor='#2c3e50')
    d.text(750, 60, 'PRODUCT CATALOG', sz=15, bold=True, w=260, color='#7d6608', bgColor='#fef9e7', strokeColor='#d6b656')
    d.text(1420, 60, 'LOCATIONS', sz=15, bold=True, w=260, color='#6c3483', bgColor='#f4ecf7', strokeColor='#9673a6')
    d.text(2100, 60, 'ORDERS & PAYMENTS', sz=15, bold=True, w=260, color='#922b21', bgColor='#fdedec', strokeColor='#b85450')
    d.text(3000, 60, 'CONFIG & SUPPORT', sz=15, bold=True, w=260, color='#1a252f', bgColor='#f2f3f4', strokeColor='#666666')
    d.text(3900, 60, 'MESSAGING', sz=15, bold=True, w=260, color='#7e5109', bgColor='#fef5e7', strokeColor='#d79b00')

    CW = 320

    # ── Col 1: Users & Profiles ──
    users = d.table(80, 100, 'users', [
        ('id', 'BIGINT PK', True),
        ('name', 'VARCHAR(255)', False),
        ('email', 'VARCHAR(255) UNIQUE', False),
        ('password', 'VARCHAR(255)', False),
        ('role', "ENUM('customer','employee','owner','superadmin')", False),
        ('phone', 'VARCHAR(20)', False),
        ('is_active', 'BOOLEAN DEFAULT 1', False),
        ('password_changed_at', 'TIMESTAMP NULL', False),
        ('created_at / updated_at', 'TIMESTAMPS', False),
    ], fill='#dae8fc', stroke='#6c8ebf', cw=CW)

    emp = d.table(80, 510, 'employee_profiles', [
        ('id', 'BIGINT PK', True),
        ('user_id', 'FK → users', False),
        ('branch_id', 'FK → branches NULL', False),
        ('position', 'VARCHAR(100)', False),
        ('salary', 'DECIMAL(12,2)', False),
    ], fill='#d5e8d4', stroke='#82b366', cw=CW)

    cust = d.table(80, 750, 'customer_profiles', [
        ('id', 'BIGINT PK', True),
        ('user_id', 'FK → users', False),
        ('loyalty_points', 'INT DEFAULT 0', False),
    ], fill='#d5e8d4', stroke='#82b366', cw=CW)

    owner = d.table(80, 920, 'owner_profiles', [
        ('id', 'BIGINT PK', True),
        ('user_id', 'FK → users', False),
        ('company_name', 'VARCHAR(255)', False),
        ('is_active', 'BOOLEAN DEFAULT 1', False),
        ('subscription_status', "ENUM('trial','active','suspended')", False),
        ('subscription_plan', 'VARCHAR(50)', False),
        ('subscription_expires_at', 'TIMESTAMP NULL', False),
        ('max_products / max_employees', 'INT DEFAULT 50/5', False),
        ('brand_store_name / tagline', 'VARCHAR(255) NULL', False),
        ('brand_logo_path / color', 'VARCHAR(255) NULL', False),
    ], fill='#d5e8d4', stroke='#82b366', cw=CW)

    # ── Col 2: Product Catalog ──
    cats = d.table(750, 100, 'categories', [
        ('id', 'BIGINT PK', True),
        ('name', 'VARCHAR(100)', False),
        ('name_sw', 'VARCHAR(100)', False),
        ('slug', 'VARCHAR(100) UNIQUE', False),
        ('created_at / updated_at', 'TIMESTAMPS', False),
    ], fill='#fff2cc', stroke='#d6b656', cw=CW)

    prods = d.table(750, 370, 'products', [
        ('id', 'BIGINT PK', True),
        ('name', 'VARCHAR(255)', False),
        ('slug', 'VARCHAR(255) UNIQUE', False),
        ('description', 'TEXT', False),
        ('brand', 'VARCHAR(100)', False),
        ('sku', 'VARCHAR(100)', False),
        ('image', 'VARCHAR(500)', False),
        ('category_id', 'FK → categories', False),
        ('created_at / updated_at', 'TIMESTAMPS', False),
    ], fill='#fff2cc', stroke='#d6b656', cw=CW)

    variants = d.table(750, 740, 'product_variants', [
        ('id', 'BIGINT PK', True),
        ('product_id', 'FK → products', False),
        ('name', 'VARCHAR(255)', False),
        ('sku', 'VARCHAR(100) UNIQUE', False),
        ('color / storage', 'VARCHAR(100)', False),
        ('price', 'DECIMAL(12,2)', False),
        ('cost_price', 'DECIMAL(12,2)', False),
        ('stock_quantity', 'INT DEFAULT 0', False),
    ], fill='#fff2cc', stroke='#d6b656', cw=CW)

    inv = d.table(750, 1100, 'inventory', [
        ('id', 'BIGINT PK', True),
        ('variant_id', 'FK → product_variants UQ', False),
        ('quantity', 'INT DEFAULT 0', False),
        ('reserved', 'INT DEFAULT 0', False),
        ('updated_at', 'TIMESTAMP', False),
    ], fill='#fff2cc', stroke='#d6b656', cw=CW)

    # ── Col 3: Locations ──
    branches = d.table(1420, 100, 'branches', [
        ('id', 'BIGINT PK', True),
        ('owner_id', 'FK → users', False),
        ('name', 'VARCHAR(100)', False),
        ('city', 'VARCHAR(100)', False),
        ('address', 'VARCHAR(255)', False),
        ('phone', 'VARCHAR(20)', False),
        ('is_active', 'BOOLEAN DEFAULT 1', False),
        ('is_default', 'BOOLEAN DEFAULT 0', False),
    ], fill='#e1d5e7', stroke='#9673a6', cw=CW)

    addrs = d.table(1420, 470, 'addresses', [
        ('id', 'BIGINT PK', True),
        ('user_id', 'FK → users', False),
        ('label', 'VARCHAR(50)', False),
        ('full_name', 'VARCHAR(255)', False),
        ('phone', 'VARCHAR(20)', False),
        ('city / district / street', 'VARCHAR(255)', False),
        ('is_default', 'BOOLEAN DEFAULT 0', False),
    ], fill='#e1d5e7', stroke='#9673a6', cw=CW)

    # ── Col 4: Orders & Payments ──
    orders = d.table(2100, 100, 'orders', [
        ('id', 'BIGINT PK', True),
        ('order_number', 'VARCHAR(50) UNIQUE', False),
        ('user_id', 'FK → users (customer)', False),
        ('handled_by', 'FK → users (employee) NULL', False),
        ('branch_id', 'FK → branches NULL', False),
        ('shipping_address_id', 'FK → addresses NULL', False),
        ('subtotal', 'DECIMAL(12,2)', False),
        ('shipping_cost', 'DECIMAL(12,2) DEFAULT 0', False),
        ('total', 'DECIMAL(12,2)', False),
        ('status', "ENUM('pending_payment','pending', ...)", False),
        ('delivery_method', "ENUM('pickup','delivery')", False),
        ('tracking_number / notes', 'TEXT NULL', False),
    ], fill='#f8cecc', stroke='#b85450', cw=CW+20)

    items = d.table(2100, 600, 'order_items', [
        ('id', 'BIGINT PK', True),
        ('order_id', 'FK → orders ON DELETE CASCADE', False),
        ('variant_id', 'FK → product_variants', False),
        ('quantity', 'INT', False),
        ('price', 'DECIMAL(12,2)', False),
    ], fill='#f8cecc', stroke='#b85450', cw=CW+20)

    pays = d.table(2100, 850, 'payments', [
        ('id', 'BIGINT PK', True),
        ('order_id', 'FK → orders ON DELETE CASCADE', False),
        ('provider', "ENUM('cash','mpesa','airtel', ...)", False),
        ('amount', 'DECIMAL(12,2)', False),
        ('status', "ENUM('pending','confirmed','failed')", False),
        ('transaction_id', 'VARCHAR(255) NULL', False),
    ], fill='#f8cecc', stroke='#b85450', cw=CW+20)

    # ── Col 5: Config & Support ──
    prov = d.table(3000, 100, 'payment_providers', [
        ('id', 'BIGINT PK', True),
        ('name', 'VARCHAR(100)', False),
        ('slug', 'VARCHAR(100) UNIQUE', False),
        ('icon', 'VARCHAR(100)', False),
        ('phone_number', 'VARCHAR(20)', False),
        ('is_active', 'BOOLEAN DEFAULT 1', False),
        ('is_online', 'BOOLEAN DEFAULT 0', False),
    ], fill='#f5f5f5', stroke='#666666', cw=CW)

    ship = d.table(3000, 430, 'shipping_rules', [
        ('id', 'BIGINT PK', True),
        ('name', 'VARCHAR(100)', False),
        ('from_city / to_city', "VARCHAR(100) DEFAULT '*'", False),
        ('min_value / max_value', 'DECIMAL(12,2) NULL', False),
        ('base_cost', 'DECIMAL(12,2)', False),
        ('shipping_cost', 'DECIMAL(12,2)', False),
        ('is_active', 'BOOLEAN DEFAULT 1', False),
    ], fill='#f5f5f5', stroke='#666666', cw=CW)

    reports = d.table(3000, 720, 'daily_reports', [
        ('id', 'BIGINT PK', True),
        ('report_date', 'DATE UNIQUE', False),
        ('total_orders', 'INT', False),
        ('total_revenue', 'DECIMAL(14,2)', False),
        ('total_items_sold', 'INT', False),
        ('paid / pending / cancelled', 'INT', False),
        ('employee_stats', 'JSON', False),
        ('top_products', 'JSON', False),
    ], fill='#f5f5f5', stroke='#666666', cw=CW)

    support = d.table(3000, 1060, 'support_messages', [
        ('id', 'BIGINT PK', True),
        ('user_id', 'FK → users', False),
        ('subject', 'VARCHAR(255)', False),
        ('category', "ENUM('payment','order', ...)", False),
        ('status', "ENUM('open','in_progress', ...)", False),
        ('message', 'TEXT', False),
        ('admin_reply', 'TEXT NULL', False),
        ('replied_at', 'TIMESTAMP NULL', False),
    ], fill='#f5f5f5', stroke='#666666', cw=CW)

    # ── Col 6: Messaging ──
    convs = d.table(3900, 100, 'conversations', [
        ('id', 'BIGINT PK', True),
        ('owner_id', 'FK → users', False),
        ('customer_id', 'FK → users NULL', False),
        ('superadmin_id', 'FK → users NULL', False),
        ('type', "ENUM('superadmin_owner', ...)", False),
        ('subject', 'VARCHAR(255)', False),
        ('status', "ENUM('open','in_progress', ...)", False),
        ('last_message_at', 'TIMESTAMP NULL', False),
    ], fill='#ffe6cc', stroke='#d79b00', cw=CW)

    convmsg = d.table(3900, 450, 'conversation_messages', [
        ('id', 'BIGINT PK', True),
        ('conversation_id', 'FK → conversations', False),
        ('sender_id', 'FK → users', False),
        ('message', 'TEXT', False),
        ('is_read', 'BOOLEAN DEFAULT false', False),
    ], fill='#ffe6cc', stroke='#d79b00', cw=CW)

    # ══════════════════════════════════════════════════════════════
    #  RELATIONSHIP EDGES — color-coded, thick, clearly labeled
    # ══════════════════════════════════════════════════════════════

    # BLUE group: users ↔ profiles
    d.edge(users, emp, '1:1', ex=0.1, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')
    d.edge(users, cust, '1:1', ex=0.3, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')
    d.edge(users, owner, '1:1', ex=0.5, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')

    # GREEN group: users ↔ locations
    d.edge(users, branches, '1:N', ex=0.7, ey=1, ix=0.15, iy=0, color='#27ae60', labelBg='#d5f5e3')
    d.edge(branches, emp, '1:N', ex=0, ey=0.7, ix=1, iy=0.4, color='#27ae60', labelBg='#d5f5e3')
    d.edge(users, addrs, '1:N', ex=0.85, ey=1, ix=0.5, iy=0, color='#27ae60', labelBg='#d5f5e3')

    # GOLD group: product cascade
    d.edge(cats, prods, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')
    d.edge(prods, variants, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')
    d.edge(variants, inv, '1:1', ex=0.5, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')

    # RED group: orders & payments
    d.edge(users, orders, '1:N customer', ex=0.9, ey=1, ix=0.1, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(users, orders, '1:N handler', ex=1, ey=0.8, ix=0.2, iy=0, color='#e74c3c', labelBg='#fdedec')
    d.edge(branches, orders, '1:N', ex=0.5, ey=1, ix=0.3, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(addrs, orders, '1:N', ex=0.5, ey=1, ix=0.45, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(orders, items, '1:N CASCADE', ex=0.3, ey=1, ix=0.5, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(orders, pays, '1:N CASCADE', ex=0.7, ey=1, ix=0.5, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(variants, items, '1:N', ex=1, ey=0.5, ix=1, iy=0.3, color='#c0392b', labelBg='#fdedec')

    # GRAY group: config & support
    d.edge(users, support, '1:N', ex=1, ey=0.6, ix=0, iy=0.3, color='#7f8c8d', labelBg='#f2f3f4')

    # ORANGE group: messaging
    d.edge(users, convs, '1:N', ex=1, ey=0.4, ix=0, iy=0.15, color='#d79b00', labelBg='#fef5e7')
    d.edge(convs, convmsg, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d79b00', labelBg='#fef5e7')

    d.save('ERD.drawio')


# ═══════════════════════════════════════════════════════════════════════════════
#  2. CLASS DIAGRAM — Native swimlane-style boxes with white headers
# ═══════════════════════════════════════════════════════════════════════════════

def gen_class():
    d = D('ElectroShop ERP — UML Class Diagram', w=4400, h=3400)
    d.text(1500, 15, 'ElectroShop ERP — UML Class Diagram', sz=24, w=1600, bold=True, color='#2c3e50')

    def cls(x, y, name, attrs, methods=None, fill='#dae8fc'):
        cid = d._id()
        rh = 26
        ah = len(attrs) * rh + 10
        mh = (len(methods or []) * rh + 10) if methods else 0
        hdr = 38
        total_h = hdr + ah + mh
        cw = 330
        hdr_fill = darken(fill, 0.55)
        st = f'shape=swimlane;fontStyle=1;align=center;startSize={hdr};fillColor={fill};strokeColor={darken(fill, 0.4)};strokeWidth=2;fontColor=#ffffff;fontSize=15;collapsible=0;'
        d.c.append(f'        <mxCell id="{cid}" value="{xe(name)}" style="{st}" vertex="1" parent="1">\n          <mxGeometry x="{x}" y="{y}" width="{cw}" height="{total_h}" as="geometry"/>\n        </mxCell>')
        for i, a in enumerate(attrs):
            aid = d._id()
            ay = hdr + i * rh
            bg = '#ffffff' if i % 2 == 0 else lighten(fill)
            d.c.append(f'        <mxCell id="{aid}" value="{xe(a)}" style="text;strokeColor=none;fillColor={bg};align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;fontColor=#111111;" vertex="1" parent="{cid}">\n          <mxGeometry y="{ay}" width="{cw}" height="{rh}" as="geometry"/>\n        </mxCell>')
        if methods:
            sid = d._id()
            sy = hdr + ah
            d.c.append(f'        <mxCell id="{sid}" value="" style="line;strokeWidth=2;fillColor=none;strokeColor={darken(fill, 0.4)};" vertex="1" parent="{cid}">\n          <mxGeometry y="{sy}" width="{cw}" height="8" as="geometry"/>\n        </mxCell>')
            for i, m in enumerate(methods):
                mid = d._id()
                my = sy + 8 + i * rh
                bg = '#ffffff' if i % 2 == 0 else lighten(fill)
                d.c.append(f'        <mxCell id="{mid}" value="{xe(m)}" style="text;strokeColor=none;fillColor={bg};align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;fontColor=#111111;" vertex="1" parent="{cid}">\n          <mxGeometry y="{my}" width="{cw}" height="{rh}" as="geometry"/>\n        </mxCell>')
        return cid

    # Row 1
    u = cls(40, 80, 'User', [
        '- id: int',
        '- name: string',
        '- email: string',
        '- password: string',
        '- role: string',
        '- phone: string',
        '- is_active: bool',
    ], [
        '+ isSuperadmin(): bool',
        '+ isOwner(): bool',
        '+ ownerProfile(): OwnerProfile',
        '+ branches(): Collection',
    ])

    cat = cls(480, 80, 'Category', [
        '- id: int',
        '- name: string',
        '- name_sw: string',
        '- slug: string',
    ], [
        '+ translated_name: string',
        '+ products(): HasMany',
    ], fill='#fff2cc')

    br = cls(960, 80, 'Branch', [
        '- id: int',
        '- owner_id: FK',
        '- name: string',
        '- city / address: string',
        '- phone: string',
        '- is_active: bool',
        '- is_default: bool',
    ], [
        '+ owner(): BelongsTo',
        '+ orders(): HasMany',
        '+ employees(): HasMany',
    ], fill='#e1d5e7')

    o = cls(1480, 80, 'Order', [
        '- id: int',
        '- order_number: string',
        '- user_id: FK (customer)',
        '- handled_by: FK (employee)',
        '- branch_id: FK (nullable)',
        '- shipping_address_id: FK',
        '- subtotal / total: decimal',
        '- status: string',
        '- delivery_method: string',
    ], [
        '+ customer(): BelongsTo',
        '+ handler(): BelongsTo',
        '+ branch(): BelongsTo',
        '+ items(): HasMany',
        '+ payments(): HasMany',
        '+ latestPayment(): HasOne',
    ], fill='#f8cecc')

    pp = cls(2100, 80, 'PaymentProvider', [
        '- id: int',
        '- name / slug: string',
        '- icon: string',
        '- phone_number: string',
        '- is_active: bool',
        '- is_online: bool',
    ], [], fill='#f5f5f5')

    cv = cls(2800, 80, 'Conversation', [
        '- id: int',
        '- owner_id: FK',
        '- customer_id: FK (nullable)',
        '- superadmin_id: FK (nullable)',
        '- type: string',
        '- subject: string',
        '- status: string',
        '- last_message_at: timestamp',
    ], [
        '+ owner(): BelongsTo',
        '+ customer(): BelongsTo',
        '+ superadmin(): BelongsTo',
        '+ messages(): HasMany',
        '+ lastMessage(): HasOne',
        '+ otherParty(): User',
    ], fill='#ffe6cc')

    # Row 2
    op = cls(40, 540, 'OwnerProfile', [
        '- id: int',
        '- user_id: FK',
        '- company_name: string',
        '- is_active: bool',
        '- subscription_status: string',
        '- subscription_plan: string',
        '- max_products / max_employees: int',
        '- brand_store_name / tagline: string',
    ], [
        '+ user(): BelongsTo',
    ], fill='#d5e8d4')

    p = cls(480, 520, 'Product', [
        '- id: int',
        '- name / slug: string',
        '- description: text',
        '- brand / sku: string',
        '- image: string',
        '- category_id: FK',
    ], [
        '+ category(): BelongsTo',
        '+ variants(): HasMany',
    ], fill='#fff2cc')

    a = cls(960, 540, 'Address', [
        '- id: int',
        '- user_id: FK',
        '- label / full_name: string',
        '- phone: string',
        '- city / district / street: string',
        '- is_default: bool',
    ], [
        '+ user(): BelongsTo',
    ], fill='#e1d5e7')

    oi = cls(1480, 580, 'OrderItem', [
        '- id: int',
        '- order_id: FK (cascade)',
        '- variant_id: FK',
        '- quantity: int',
        '- price: decimal',
    ], [
        '+ order(): BelongsTo',
        '+ variant(): BelongsTo',
    ], fill='#f8cecc')

    sr = cls(2100, 400, 'ShippingRule', [
        '- id: int',
        '- name: string',
        '- from_city / to_city: string',
        '- min_value / max_value: decimal',
        '- base_cost / shipping_cost: decimal',
        '- is_active: bool',
    ], [], fill='#f5f5f5')

    cmsg = cls(2800, 540, 'ConversationMessage', [
        '- id: int',
        '- conversation_id: FK',
        '- sender_id: FK',
        '- message: text',
        '- is_read: bool (default false)',
    ], [
        '+ conversation(): BelongsTo',
        '+ sender(): BelongsTo',
    ], fill='#ffe6cc')

    # Row 3
    ep = cls(40, 980, 'EmployeeProfile', [
        '- id: int',
        '- user_id: FK',
        '- branch_id: FK (nullable)',
        '- position: string',
        '- salary: decimal',
    ], [
        '+ user(): BelongsTo',
        '+ branch(): BelongsTo',
    ], fill='#d5e8d4')

    pv = cls(480, 840, 'ProductVariant', [
        '- id: int',
        '- product_id: FK',
        '- name / sku: string',
        '- color / storage: string',
        '- price / cost_price: decimal',
        '- stock_quantity: int',
    ], [
        '+ product(): BelongsTo',
        '+ inventory(): HasOne',
    ], fill='#fff2cc')

    cp = cls(960, 800, 'CustomerProfile', [
        '- id: int',
        '- user_id: FK',
        '- loyalty_points: int',
    ], [
        '+ user(): BelongsTo',
    ], fill='#d5e8d4')

    pay = cls(1480, 860, 'Payment', [
        '- id: int',
        '- order_id: FK (cascade)',
        '- provider: string',
        '- amount: decimal',
        '- status: string',
        '- transaction_id: string',
    ], [
        '+ order(): BelongsTo',
    ], fill='#f8cecc')

    dr = cls(2100, 660, 'DailyReport', [
        '- id: int',
        '- report_date: date (unique)',
        '- total_orders / revenue: numeric',
        '- total_items_sold: int',
        '- paid / pending / cancelled: int',
        '- employee_stats: json',
        '- top_products: json',
    ], [], fill='#f5f5f5')

    sm = cls(2800, 860, 'SupportMessage', [
        '- id: int',
        '- user_id: FK',
        '- subject / category: string',
        '- status: string',
        '- message: text',
        '- admin_reply: text',
    ], [], fill='#f5f5f5')

    inv = cls(480, 1160, 'Inventory', [
        '- id: int',
        '- variant_id: FK (unique)',
        '- quantity / reserved: int',
    ], [
        '+ variant(): BelongsTo',
    ], fill='#fff2cc')

    # Relationships — color-coded
    d.edge(u, op, '1:1', ex=0.1, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')
    d.edge(u, ep, '1:1', ex=0.25, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')
    d.edge(u, cp, '1:1', ex=0.4, ey=1, ix=0.5, iy=0, color='#2980b9', labelBg='#d6eaf8')
    d.edge(cat, p, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')
    d.edge(p, pv, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')
    d.edge(pv, inv, '1:1', ex=0.3, ey=1, ix=0.5, iy=0, color='#d4ac0d', labelBg='#fef9e7')
    d.edge(br, ep, '1:N', ex=0.8, ey=1, ix=1, iy=0.5, color='#27ae60', labelBg='#d5f5e3')
    d.edge(o, oi, '1:N', ex=0.3, ey=1, ix=0.5, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(o, pay, '1:N', ex=0.7, ey=1, ix=0.5, iy=0, color='#c0392b', labelBg='#fdedec')
    d.edge(pv, oi, '1:N', ex=1, ey=0.5, ix=1, iy=0.3, color='#c0392b', labelBg='#fdedec')
    d.edge(cv, cmsg, '1:N', ex=0.5, ey=1, ix=0.5, iy=0, color='#d79b00', labelBg='#fef5e7')

    d.save('ClassDiagram.drawio')


# ═══════════════════════════════════════════════════════════════════════════════
#  3. USE CASE DIAGRAM — Clear actors and relationships
# ═══════════════════════════════════════════════════════════════════════════════

def gen_uc():
    d = D('ElectroShop ERP — Use Case Diagram', w=3600, h=2500)
    d.text(1100, 15, 'ElectroShop ERP — Use Case Diagram', sz=24, w=1400, bold=True, color='#2c3e50')

    sa = d.stick(80, 350, 'Superadmin')
    ow = d.stick(80, 850, 'Owner')
    em = d.stick(3200, 350, 'Employee')
    cu = d.stick(3200, 850, 'Customer')
    ai = d.stick(3200, 1350, 'Gemini AI')

    d.boundary(360, 80, 2500, 1850, 'ElectroShop ERP System')

    uc1  = d.oval(480, 130, 'Manage Owners (CRUD)')
    uc2  = d.oval(480, 220, 'Manage Subscriptions & Limits')
    uc3  = d.oval(480, 310, 'Manage White-Label Branding')
    uc4  = d.oval(480, 400, 'View System Statistics')
    uc5  = d.oval(480, 490, 'Message Owners (Inbox)')

    uc6  = d.oval(480, 650, 'Manage Employees')
    uc7  = d.oval(480, 740, 'Manage Branches')
    uc8  = d.oval(480, 830, 'Manage Products & Variants')
    uc9  = d.oval(480, 920, 'Configure Payment Providers')
    uc10 = d.oval(480, 1010, 'Configure Shipping Rules')
    uc11 = d.oval(480, 1100, 'View Reports & Analytics')
    uc12 = d.oval(480, 1190, 'Get AI Business Insights')
    uc13 = d.oval(480, 1280, 'Message Superadmin & Customers')

    uc14 = d.oval(2150, 130, 'Manage Orders')
    uc15 = d.oval(2150, 220, 'Confirm Mobile Money Payments')
    uc16 = d.oval(2150, 310, 'Manage Customers')
    uc17 = d.oval(2150, 400, 'Handle Support Messages')
    uc18 = d.oval(2150, 490, 'Update Order Status')
    uc19 = d.oval(2150, 650, 'Browse Products')
    uc20 = d.oval(2150, 740, 'Add to Cart & Checkout')
    uc21 = d.oval(2150, 830, 'Make Payment')
    uc22 = d.oval(2150, 920, 'Track Orders')
    uc23 = d.oval(2150, 1010, 'Contact Support')
    uc24 = d.oval(2150, 1100, 'Manage Addresses')
    uc25 = d.oval(2150, 1190, 'Message Owner (Inbox)')

    for uc in [uc1,uc2,uc3,uc4,uc5]:
        d.edge(sa, uc, 'manages', color='#2980b9', labelBg='#d6eaf8')
    for uc in [uc6,uc7,uc8,uc9,uc10,uc11,uc12,uc13]:
        d.edge(ow, uc, 'manages', color='#27ae60', labelBg='#d5f5e3')
    for uc in [uc14,uc15,uc16,uc17,uc18]:
        d.edge(em, uc, 'handles', color='#c0392b', labelBg='#fdedec')
    for uc in [uc19,uc20,uc21,uc22,uc23,uc24,uc25]:
        d.edge(cu, uc, 'uses', color='#d79b00', labelBg='#fef5e7')
    d.edge(ai, uc12, 'powers', ex=0, ey=0.5, ix=1, iy=0.5, color='#8e44ad', labelBg='#f4ecf7')

    d.edge(uc20, uc21, '<<include>>', ex=0.5, ey=1, ix=0.5, iy=0, dashed=True, color='#7f8c8d', labelBg='#f2f3f4')
    d.edge(uc21, uc15, '<<include>>', ex=0.5, ey=1, ix=0.5, iy=0, dashed=True, color='#7f8c8d', labelBg='#f2f3f4')
    d.edge(uc14, uc15, '<<extend>>', ex=0.5, ey=1, ix=1, iy=0.5, dashed=True, color='#7f8c8d', labelBg='#f2f3f4')

    d.save('UseCase.drawio')


# ═══════════════════════════════════════════════════════════════════════════════
#  4. SEQUENCE DIAGRAMS — Bold lifelines, clear message labels
# ═══════════════════════════════════════════════════════════════════════════════

def gen_seq():
    d = D('ElectroShop ERP — Sequence Diagrams', w=3400, h=3600)
    d.text(1000, 10, 'ElectroShop ERP — Sequence Diagrams', sz=24, w=1400, bold=True, color='#2c3e50')

    def flow(sx, sy, title, lifelines, messages):
        d.text(sx, sy, title, sz=16, w=700, bold=True, color='#2c3e50', bgColor='#eaf2f8', strokeColor='#2c3e50')
        ly = sy + 45
        ll_ids = []
        spacing = 300
        for i, (name, w) in enumerate(lifelines):
            x = sx + i * spacing
            ll = d.lifeline(x, ly, name, h=len(messages)*42+90)
            ll_ids.append(ll)
        my = ly + 90
        for src_i, tgt_i, label, dashed in messages:
            d.msg(ll_ids[src_i], ll_ids[tgt_i], label, my, dashed=dashed)
            my += 42
        return my + 25

    y = flow(200, 70, 'Flow 1: Customer Checkout & Payment', [
        ('Customer', 100), ('Vue Storefront', 100), ('Laravel API', 100), ('Database', 100), ('Payment Provider', 100)
    ], [
        (0, 1, 'Click "Buy Now"', False),
        (1, 2, 'POST /cart/items {variant_id, qty}', False),
        (2, 3, 'INSERT order_items', False),
        (3, 2, '200 OK', False),
        (2, 1, '200 OK {cart}', False),
        (0, 1, 'Click "Checkout"', False),
        (1, 2, 'GET /checkout', False),
        (2, 3, 'SELECT shipping_rules, addresses', False),
        (3, 2, 'results', False),
        (2, 1, '200 OK {checkout_data}', False),
        (0, 1, 'Select delivery + payment', False),
        (1, 2, 'POST /orders {address, delivery, payment}', False),
        (2, 3, 'INSERT orders + order_items + payments', False),
        (2, 4, 'Process payment (if online)', True),
        (2, 3, 'UPDATE inventory (reserved)', False),
        (2, 1, '201 Created {order_number}', False),
        (1, 0, 'Show confirmation page', False),
    ])

    y = flow(200, y+25, 'Flow 2: Employee Confirms Mobile Money Payment', [
        ('Employee', 100), ('Vue Dashboard', 100), ('Laravel API', 100), ('Database', 100)
    ], [
        (0, 1, 'Open Order Management', False),
        (1, 2, 'GET /orders?status=pending', False),
        (2, 3, 'SELECT orders WHERE status=pending', False),
        (3, 2, 'results', False),
        (2, 1, '200 OK {pending_orders}', False),
        (0, 1, 'Click "Confirm Payment"', False),
        (1, 2, 'POST /orders/{id}/confirm {customer_name}', False),
        (2, 3, 'UPDATE payments SET status=confirmed', False),
        (2, 3, 'UPDATE orders SET status=paid', False),
        (2, 3, 'UPDATE inventory (deduct stock)', False),
        (2, 1, '200 OK {success}', False),
        (1, 0, 'Show "Payment Confirmed"', False),
    ])

    y = flow(200, y+25, 'Flow 3: Customer-Owner Conversation', [
        ('Customer', 100), ('Vue Storefront', 100), ('Laravel API', 100), ('Database', 100), ('Owner', 100)
    ], [
        (0, 1, 'Open Inbox - New Conversation', False),
        (1, 2, 'POST /conversations {type, subject, message}', False),
        (2, 3, 'INSERT conversations + messages', False),
        (3, 2, 'result', False),
        (2, 1, '201 Created', False),
        (0, 1, 'Type and send message', False),
        (1, 2, 'POST /conversations/{id}/messages', False),
        (2, 3, 'INSERT conversation_messages', False),
        (2, 1, '201 Created', False),
        (4, 2, 'GET /conversations (polling every 15s)', True),
        (2, 3, 'SELECT conversations WHERE owner_id', False),
        (2, 4, '200 OK {new_message}', False),
        (4, 2, 'POST /conversations/{id}/messages {reply}', False),
        (2, 3, 'INSERT conversation_messages', False),
        (2, 4, '201 Created', False),
    ])

    y = flow(200, y+25, 'Flow 4: Superadmin Creates Owner Account', [
        ('Superadmin', 100), ('Vue Dashboard', 100), ('Laravel API', 100), ('Database', 100)
    ], [
        (0, 1, 'Fill create owner form', False),
        (1, 2, 'POST /superadmin/owners {name, email, company}', False),
        (2, 3, 'INSERT users (role=owner)', False),
        (2, 3, 'INSERT owner_profiles', False),
        (2, 1, '201 Created {default_password}', False),
        (1, 0, 'Show password to share', False),
        (0, 1, 'Owner logs in with default password', False),
        (1, 2, 'POST /login {email, password}', False),
        (2, 3, 'SELECT users WHERE email', False),
        (2, 3, 'Check password_changed_at IS NULL', True),
        (2, 1, '200 OK {token, force_password_change: true}', False),
        (1, 0, 'Show Change Password modal', False),
    ])

    d.save('SequenceDiagrams.drawio')


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def pdf_erd():
    el = []
    el.append(Paragraph('ElectroShop ERP — Entity Relationship Diagram', sT)); el.append(hr())
    el.append(bd('All 19 database tables and their relationships. SQLite with foreign key constraints.')); el.append(sp(10))
    el.append(sc('Tables Overview'))
    el.append(itbl([
        ['users', 'Central user table (customer, employee, owner, superadmin)'],
        ['owner_profiles', 'Subscription, limits, branding (white-label)'],
        ['employee_profiles', 'Position, salary, branch assignment'],
        ['customer_profiles', 'Loyalty points'],
        ['categories', 'Product categories with Swahili translations'],
        ['products', 'Product catalog (name, brand, SKU, image)'],
        ['product_variants', 'Size/color/storage with individual pricing & stock'],
        ['inventory', 'Stock tracking per variant'],
        ['branches', 'Physical store locations (owner-scoped, optional)'],
        ['addresses', 'Customer delivery addresses'],
        ['orders', 'Orders with status workflow & delivery method'],
        ['order_items', 'Line items (FK CASCADE on delete)'],
        ['payments', 'Payment records (FK CASCADE on delete)'],
        ['payment_providers', 'M-Pesa, Airtel, etc.'],
        ['shipping_rules', 'Wildcard city-to-city with value-based tiers'],
        ['daily_reports', 'Auto-generated daily sales summaries'],
        ['support_messages', 'Customer tickets with admin replies'],
        ['conversations', 'superadmin-owner & customer-owner messaging'],
        ['conversation_messages', 'Individual messages within conversations'],
    ])); el.append(sp(10))
    el.append(sc('Key Relationships'))
    el.extend(bl([
        '<b>users → owner_profiles</b>: 1:1, subscription & branding',
        '<b>users → employee_profiles</b>: 1:1, optional branch link',
        '<b>categories → products → variants → inventory</b>: cascading hierarchy',
        '<b>users → orders</b>: customer places, employee handles',
        '<b>orders → items/payments</b>: ON DELETE CASCADE',
        '<b>conversations → messages</b>: threaded messaging',
    ])); el.append(sp(10))
    el.append(sc('Order Status Workflow'))
    el.append(bd('pending_payment → pending → paid → processing → shipped → delivered'))
    el.append(bd('inactive (auto-deleted after 6h) | cancelled'))
    el.append(sp(10)); el.append(hr())
    el.append(Paragraph('<b>ElectroShop ERP</b> — ERD Documentation — July 2026', sF))
    bpdf(el, 'ERD_Documentation.pdf')

def pdf_class():
    el = []
    el.append(Paragraph('ElectroShop ERP — UML Class Diagram', sT)); el.append(hr())
    el.append(bd('18 Eloquent model classes with attributes, methods, and relationships.')); el.append(sp(10))
    el.append(sc('Model Groups'))
    el.append(itbl([
        ['User & Profiles', 'User, OwnerProfile, EmployeeProfile, CustomerProfile'],
        ['Product Catalog', 'Category, Product, ProductVariant, Inventory'],
        ['Locations', 'Branch, Address'],
        ['Orders & Payments', 'Order, OrderItem, Payment'],
        ['Config & Support', 'PaymentProvider, ShippingRule, DailyReport, SupportMessage'],
        ['Conversations', 'Conversation, ConversationMessage'],
    ])); el.append(sp(10))
    el.append(sc('Key Models'))
    el.append(itbl([
        ['User', 'Role enum, isSuperadmin()/isOwner(), polymorphic profiles'],
        ['Order', 'Status workflow, customer/handler/branch/items/payments'],
        ['Conversation', 'Type-determined, otherParty() returns other user'],
        ['OwnerProfile', 'Subscription, limits, branding'],
    ])); el.append(sp(10)); el.append(hr())
    el.append(Paragraph('<b>ElectroShop ERP</b> — Class Diagram Documentation — July 2026', sF))
    bpdf(el, 'ClassDiagram_Documentation.pdf')

def pdf_uc():
    el = []
    el.append(Paragraph('ElectroShop ERP — Use Case Diagram', sT)); el.append(hr())
    el.append(bd('5 actors, 25 use cases with include/extend relationships.')); el.append(sp(10))
    el.append(sc('Actors'))
    el.append(itbl([
        ['Superadmin', 'Manages owners, subscriptions, branding'],
        ['Owner', 'Products, employees, branches, payments, shipping, reports'],
        ['Employee', 'Orders, payments, support'],
        ['Customer', 'Browse, cart, checkout, payment, support'],
        ['Gemini AI', 'AI business insights'],
    ])); el.append(sp(10)); el.append(hr())
    el.append(Paragraph('<b>ElectroShop ERP</b> — Use Case Diagram Documentation — July 2026', sF))
    bpdf(el, 'UseCase_Documentation.pdf')

def pdf_seq():
    el = []
    el.append(Paragraph('ElectroShop ERP — Sequence Diagrams', sT)); el.append(hr())
    el.append(bd('4 key system interaction flows.')); el.append(sp(10))
    el.append(sc('Flow 1: Checkout & Payment'))
    el.append(bd('Customer selects products → cart → checkout → order placed → payment processed → inventory reserved.'))
    el.append(sp(10))
    el.append(sc('Flow 2: Employee Confirms Payment'))
    el.append(bd('Employee opens pending orders → clicks confirm → types customer name IN CAPS → payment confirmed → stock deducted.'))
    el.append(sp(10))
    el.append(sc('Flow 3: Customer-Owner Conversation'))
    el.append(bd('Customer opens inbox → creates conversation → sends message (grey tick) → owner polls every 15s → reads and replies → sender tick turns blue (read receipt).'))
    el.append(sp(10))
    el.append(sc('Flow 4: Superadmin Creates Owner'))
    el.append(bd('Superadmin fills form → creates owner with UPPERCASE password → owner logs in → forced password change.'))
    el.append(sp(10)); el.append(hr())
    el.append(Paragraph('<b>ElectroShop ERP</b> — Sequence Diagrams Documentation — July 2026', sF))
    bpdf(el, 'SequenceDiagrams_Documentation.pdf')

# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating draw.io diagrams...')
    gen_erd(); gen_class(); gen_uc(); gen_seq()
    print('\nGenerating PDF documentation...')
    pdf_erd(); pdf_class(); pdf_uc(); pdf_seq()
    print('\nDone!')
