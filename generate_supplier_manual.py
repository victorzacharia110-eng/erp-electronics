#!/usr/bin/env python3
"""Generate PDF Supplier Manuals for ERP Electronics Store (English + Swahili)."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBd', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

RED = HexColor('#e74c3c')
DARK = HexColor('#2c3e50')
LIGHT_GRAY = HexColor('#f5f5f5')
GRAY = HexColor('#888888')
GREEN = HexColor('#27ae60')

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
sBullet = make_style('sBullet', fontSize=10, textColor=HexColor('#333333'), leading=14, leftIndent=20, spaceAfter=3)
sNote = make_style('sNote', fontSize=9, textColor=GRAY, leading=13, spaceAfter=4, leftIndent=10)
sTocEntry = make_style('sTocEntry', fontSize=11, textColor=DARK, leading=16, spaceAfter=4, leftIndent=10)
sFooter = make_style('sFooter', fontSize=8, textColor=GRAY, alignment=TA_CENTER)
sTableHeader = make_style('sTableHeader', fontSize=9, fontName='DejaVuBd', textColor=white, leading=12)
sTableCell = make_style('sTableCell', fontSize=9, textColor=HexColor('#333333'), leading=12)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd'), spaceAfter=8, spaceBefore=8)

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

def info_table(rows, col_widths=None):
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

def docs_table(rows):
    data = [[
        Paragraph('<b>#</b>', sTableHeader),
        Paragraph('<b>Document</b>', sTableHeader),
        Paragraph('<b>Issued By</b>', sTableHeader),
        Paragraph('<b>Purpose</b>', sTableHeader),
    ]]
    for i, (doc, issuer, purpose) in enumerate(rows, 1):
        data.append([
            Paragraph(str(i), sTableCell),
            Paragraph(f'<b>{doc}</b>', sTableCell),
            Paragraph(issuer, sTableCell),
            Paragraph(purpose, sTableCell),
        ])
    t = Table(data, colWidths=[22, 120, 95, 233])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ]))
    return t

def steps_table(steps):
    data = [[Paragraph('<b>#</b>', sTableHeader), Paragraph('<b>Action</b>', sTableHeader)]]
    for i, step in enumerate(steps, 1):
        data.append([Paragraph(str(i), sTableCell), Paragraph(step, sTableCell)])
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
    elements = []
    elements.append(Spacer(1, 60))
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
    elements.append(overlay)
    elements.append(PageBreak())
    return elements

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 20 * mm, f'Page {doc.page}')
    canvas.restoreState()


def build_en():
    el = []
    el += cover_page(
        'ERP Electronics Store',
        'Supplier Manual',
        'Version 1.0',
        'July 2026'
    )

    el.append(chapter('Table of Contents'))
    el.append(hr())
    toc = [
        ('1.', 'Introduction'),
        ('2.', 'Registering a Supplier'),
        ('3.', 'Required Tanzanian Legal Documents'),
        ('4.', 'Uploading Supplier Documents'),
        ('5.', 'Managing Suppliers'),
        ('6.', 'The Supplier Portal'),
        ('7.', 'Purchase Orders'),
        ('8.', 'Support & Contact'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    # 1. Introduction
    el.append(chapter('1. Introduction'))
    el.append(hr())
    el.append(body(
        'This manual explains how suppliers are onboarded into the ERP Electronics system and how they work with the '
        'business. A supplier is a company, partnership or individual who provides products or materials to the store '
        'through purchase orders.'
    ))
    el.append(section('How it works'))
    el += bullet_list([
        'Suppliers are registered by the store owner, who enters the business details and required legal documents.',
        'Each supplier keeps a record of Tanzanian legal documents (registration, tax and licensing certificates).',
        'Approved suppliers can be linked to purchase orders and use the Supplier Portal to view and fulfil orders.',
    ])
    el.append(spacer())

    # 2. Registering a supplier
    el.append(chapter('2. Registering a Supplier'))
    el.append(hr())
    el.append(body(
        'To add a supplier, open the Supplier Management page from the owner dashboard. The registration form captures '
        'the supplier’s contact details, Tanzanian business information and legal documents.'
    ))
    el.append(section('Contact details'))
    el += bullet_list([
        'Business name, contact person, phone and email.',
        'Physical address, city and country.',
    ])
    el.append(section('Tanzanian business details'))
    el += bullet_list([
        'Business type — Sole Proprietorship, Partnership, Limited Company or Other.',
        'TIN Number (Taxpayer Identification Number issued by TRA).',
        'VAT Number — if the business is VAT registered.',
        'Business Registration Number (issued by BRELA).',
    ])
    el.append(section('Supplier status'))
    el += bullet_list([
        'A supplier can be marked active or inactive. Inactive suppliers cannot be selected for new purchase orders.',
    ])
    el.append(spacer())

    # 3. Required Tanzanian legal documents
    el.append(chapter('3. Required Tanzanian Legal Documents'))
    el.append(hr())
    el.append(body(
        'Tanzanian law requires suppliers to hold valid business and tax registration documents. The system stores a '
        'digital copy of each document so the business can verify the supplier before placing orders. The documents below '
        'follow the standard Tanzanian supplier documentation format.'
    ))
    el.append(docs_table([
        ('Business Registration Certificate', 'BRELA',
         'Proves the business is legally registered in Tanzania.'),
        ('TIN Certificate', 'TRA',
         'Taxpayer Identification Number certificate; required for tax compliance and issuing invoices.'),
        ('VAT Registration Certificate', 'TRA',
         'Required when annual turnover is above the VAT threshold (TZS 100 million); allows VAT invoicing.'),
        ('Business License', 'Local Government Authority',
         'Annual trading permit issued by the city or municipal council where the business operates.'),
        ('Certificate of Incorporation', 'BRELA',
         'Confirms a limited company is incorporated under the Companies Act.'),
        ('Identification Document', 'NIDA / Government',
         'National ID (NIDA) for individual suppliers; a passport or driving licence for foreign suppliers.'),
        ('Signed Supply Contract', 'Both parties',
         'The agreement between the supplier and the business covering terms of supply.'),
    ]))
    el.append(spacer())
    el.append(section('Accepted file formats'))
    el += bullet_list([
        'PDF, JPG, JPEG, PNG, DOC or DOCX.',
        'Each document must be 20 MB or smaller.',
        'Documents are stored securely under the supplier’s record and can be downloaded or deleted by the owner at any time.',
    ])
    el.append(spacer())

    # 4. Uploading documents
    el.append(chapter('4. Uploading Supplier Documents'))
    el.append(hr())
    el.append(body(
        'Documents are uploaded in the Add or Edit Supplier form, in the "Legal Documents (Tanzanian Format)" section.'
    ))
    el.append(steps_table([
        'Open the Add Supplier or Edit Supplier form.',
        'Click the file drop area and select the document files (multiple files allowed).',
        'For each file, choose the correct document type from the list (Contract, BRELA, TIN Certificate, VAT Certificate, Business License, Certificate of Incorporation, Identification, Other).',
        'Complete the remaining supplier details and save. For an existing supplier, uploaded documents are saved automatically.',
    ]))
    el.append(note('When editing a supplier you can also download or delete previously uploaded documents from the same section.'))
    el.append(spacer())

    # 5. Managing suppliers
    el.append(chapter('5. Managing Suppliers'))
    el.append(hr())
    el.append(section('Viewing suppliers'))
    el.append(body(
        'The Supplier Management page lists all suppliers with their contact person, phone, email, city, number of '
        'purchase orders and active status. Use the search box to find a supplier by name, contact or email.'
    ))
    el.append(section('Editing a supplier'))
    el.append(steps_table([
        'Click the edit icon next to a supplier.',
        'Update the contact or business details as needed.',
        'Upload new documents or delete outdated ones.',
        'Save your changes.',
    ]))
    el.append(section('Deleting a supplier'))
    el.append(body(
        'A supplier can only be deleted if they have no purchase orders. Suppliers with an order history are kept for '
        'accounting and reporting purposes.'
    ))
    el.append(spacer())

    # 6. Supplier portal
    el.append(chapter('6. The Supplier Portal'))
    el.append(hr())
    el.append(body(
        'Registered suppliers can receive their own login credentials so they can use the Supplier Portal. After logging '
        'in with the email and password provided by the owner, the supplier sees their dashboard with three summary '
        'cards: Total Orders, Pending Delivery and Completed.'
    ))
    el += bullet_list([
        'The supplier can view all purchase orders assigned to them.',
        'Each order shows the PO number, date, line items, total cost, status and expected date.',
        'Order details list the exact products, quantities and unit costs to be supplied.',
        'The supplier can open an order and mark it as Received once the goods have been delivered.',
    ])
    el.append(spacer())

    # 7. Purchase orders
    el.append(chapter('7. Purchase Orders'))
    el.append(hr())
    el.append(body(
        'A purchase order (PO) is created by the owner when the store needs to restock products. The order records the '
        'supplier, the products, quantities and unit costs. Each PO follows a status flow:'
    ))
    el.append(info_table([
        ('Draft', 'The order has been created but not yet confirmed with the supplier.'),
        ('Ordered', 'The order has been sent to the supplier and is awaiting delivery.'),
        ('Received', 'The supplier has delivered the goods and the order is complete.'),
    ]))
    el.append(spacer())
    el.append(body(
        'When the supplier marks an order as received, the stock is updated automatically and the goods become '
        'available for sale.'
    ))
    el.append(spacer())

    # 8. Support
    el.append(chapter('8. Support & Contact'))
    el.append(hr())
    el.append(body(
        'For help with onboarding, document requirements or using the portal, contact the store owner or your system '
        'administrator. The owner manages supplier records, document verification and portal access from the '
        'Supplier Management page.'
    ))
    el.append(spacer())
    el.append(hr())
    el.append(Paragraph('<b>ERP Electronics Store</b> — Supplier Manual Version 1.0 — July 2026', sFooter))
    el.append(Paragraph('For technical support, contact your system administrator.', sFooter))

    return el


def build_sw():
    el = []
    el += cover_page(
        'Duka la ERP Electronics',
        'Mwongozo wa Muuzaji (Supplier)',
        'Toleo 1.0',
        'Julai 2026'
    )

    el.append(chapter('Yaliyomo'))
    el.append(hr())
    toc = [
        ('1.', 'Utangulizi'),
        ('2.', 'Kusajili Muuzaji'),
        ('3.', 'Nyaraka za Kisheria za Tanzania Zinazohitajika'),
        ('4.', 'Kupakia Nyaraka za Muuzaji'),
        ('5.', 'Kusimamia Wachuuzi'),
        ('6.', 'Lango la Muuzaji (Supplier Portal)'),
        ('7.', 'Oda za Ununuzi'),
        ('8.', 'Msaada na Mawasiliano'),
    ]
    for num, title in toc:
        el.append(Paragraph(f'<b>{num}</b>  {title}', sTocEntry))
    el.append(PageBreak())

    # 1. Utangulizi
    el.append(chapter('1. Utangulizi'))
    el.append(hr())
    el.append(body(
        'Mwongozo huu unaelezea jinsi wachuuzi wanavyojisajili katika mfumo wa ERP Electronics na jinsi wanavyofanya '
        'kazi na biashara. Muuzaji ni kampuni, ushirikiano au mtu binafsi anayetoa bidhaa au vifaa kwa duka kupitia '
        'oda za ununuzi.'
    ))
    el.append(section('Jinsi mfumo unavyofanya kazi'))
    el += bullet_list([
        'Wachuuzi husajiliwa na mmiliki wa duka, ambaye anaingiza maelezo ya biashara na nyaraka za kisheria zinazohitajika.',
        'Kila muuzaji huhifadhi rekodi ya nyaraka za kisheria za Tanzania (vyeti vya usajili, kodi na leseni).',
        'Wachuuzi walioidhinishwa wanaweza kuunganishwa na oda za ununuzi na kutumia Lango la Muuzaji kuona na kukamilisha oda.',
    ])
    el.append(spacer())

    # 2. Kusajili muuzaji
    el.append(chapter('2. Kusajili Muuzaji'))
    el.append(hr())
    el.append(body(
        'Ili kuongeza muuzaji, fungua ukurasa wa Usimamizi wa Wachuuzi kutoka dashibodi ya mmiliki. Fomu ya usajili '
        'inakusanya maelezo ya mawasiliano, maelezo ya biashara ya Tanzania na nyaraka za kisheria.'
    ))
    el.append(section('Maelezo ya mawasiliano'))
    el += bullet_list([
        'Jina la biashara, mtu wa mawasiliano, simu na barua pepe.',
        'Anwani ya makazi, mji na nchi.',
    ])
    el.append(section('Maelezo ya biashara ya Tanzania'))
    el += bullet_list([
        'Aina ya biashara — Miliki Moja, Ushirikiano, Kampuni ya Dhima Ndogo au Nyingine.',
        'Namba ya TIN (Namba ya Utambulisho wa Mlipakodi iliyotolewa na TRA).',
        'Namba ya VAT — ikiwa biashara imesajiliwa VAT.',
        'Namba ya Usajili wa Biashara (iliyotolewa na BRELA).',
    ])
    el.append(section('Hali ya muuzaji'))
    el += bullet_list([
        'Muuzaji anaweza kuwekwa kama anayefanya kazi au asiyefanya kazi. Wachuuzi wasiofanya kazi hawawezi kuchaguliwa kwa oda mpya za ununuzi.',
    ])
    el.append(spacer())

    # 3. Nyaraka za kisheria
    el.append(chapter('3. Nyaraka za Kisheria za Tanzania Zinazohitajika'))
    el.append(hr())
    el.append(body(
        'Sheria ya Tanzania inahitaji wachuuzi kuwa na nyaraka halali za usajili wa biashara na kodi. Mfumo unahifadhi '
        'nakala ya kidijitali ya kila hati ili biashara iweze kuthibitisha muuzaji kabla ya kuagiza bidhaa. Nyaraka '
        'zifuatazo zinafuata muundo wa nyaraka za kisheria za wachuuzi Tanzania.'
    ))
    el.append(docs_table([
        ('Cheti cha Usajili wa Biashara', 'BRELA',
         'Kinathibitisha biashara imesajiliwa kihalali Tanzania.'),
        ('Cheti cha TIN', 'TRA',
         'Cheti cha Namba ya Utambulisho wa Mlipakodi; kinahitajika kwa kuzingatia kodi na kutoa ankara.'),
        ('Cheti cha Usajili wa VAT', 'TRA',
         'Kinahitajika wakati mauzo ya mwaka yanazidi kiwango cha VAT (TZS milioni 100); kinaruhusu ankara za VAT.'),
        ('Leseni ya Biashara', 'Mamlaka ya Serikali ya Mitaa',
         'Kibali cha biashara cha kila mwaka kinachotolewa na halmashauri ya jiji au manispaa.'),
        ('Cheti cha Uingizaji Kampuni', 'BRELA',
         'Kinathibitisha kampuni ya dhima ndogo imeingizwa kwa mujibu wa Sheria ya Kampuni.'),
        ('Hati ya Utambulisho', 'NIDA / Serikali',
         'Kitambulisho cha Taifa (NIDA) kwa wachuuzi binafsi; pasipoti au leseni ya udereva kwa wachuuzi wa kigeni.'),
        ('Mkataba wa Ugavi UlioSainiwa', 'Pande zote mbili',
         'Makubaliano kati ya muuzaji na biashara yanayoeleza masharti ya ugavi.'),
    ]))
    el.append(spacer())
    el.append(section('Miundo ya faili inayokubalika'))
    el += bullet_list([
        'PDF, JPG, JPEG, PNG, DOC au DOCX.',
        'Kila hati lazima iwe megabaiti 20 au ndogo.',
        'Nyaraka huhifadhiwa kwa usalama chini ya rekodi ya muuzaji na zinaweza kupakuliwa au kufutwa na mmiliki wakati wowote.',
    ])
    el.append(spacer())

    # 4. Kupakia nyaraka
    el.append(chapter('4. Kupakia Nyaraka za Muuzaji'))
    el.append(hr())
    el.append(body(
        'Nyaraka hupakiwa katika fomu ya Kuongeza au Kuhariri Muuzaji, katika sehemu ya "Nyaraka za Kisheria '
        '(Muundo wa Tanzania)".'
    ))
    el.append(steps_table([
        'Fungua fomu ya Kuongeza Muuzaji au Kuhariri Muuzaji.',
        'Bonyeza eneo la kupakia faili na uchague faili za nyaraka (faili nyingi zinaruhusiwa).',
        'Kwa kila faili, chagua aina sahihi ya hati kutoka kwenye orodha (Mkataba, BRELA, Cheti cha TIN, Cheti cha VAT, Leseni ya Biashara, Cheti cha Uingizaji Kampuni, Utambulisho, Nyingine).',
        'Kamilisha maelezo mengine ya muuzaji na uhifadhi. Kwa muuzaji aliyepo, nyaraka zilizopakiwa huhifadhiwa kiotomatiki.',
    ]))
    el.append(note('Unapohariri muuzaji, unaweza pia kupakua au kufuta nyaraka zilizopakiwa hapo awali katika sehemu hiyo hiyo.'))
    el.append(spacer())

    # 5. Kusimamia wachuuzi
    el.append(chapter('5. Kusimamia Wachuuzi'))
    el.append(hr())
    el.append(section('Kutazama wachuuzi'))
    el.append(body(
        'Ukurasa wa Usimamizi wa Wachuuzi unaorodhesha wachuuzi wote na mtu wa mawasiliano, simu, barua pepe, mji, '
        'idadi ya oda za ununuzi na hali ya kufanya kazi. Tumia kisanduku cha utafutaji kupata muuzaji kwa jina, '
        'mawasiliano au barua pepe.'
    ))
    el.append(section('Kuhariri muuzaji'))
    el.append(steps_table([
        'Bonyeza alama ya kuhariri karibu na muuzaji.',
        'Sasisha maelezo ya mawasiliano au biashara inavyohitajika.',
        'Pakia nyaraka mpya au futa nyaraka zilizopitwa na wakati.',
        'Hifadhi mabadiliko yako.',
    ]))
    el.append(section('Kufuta muuzaji'))
    el.append(body(
        'Muuzaji anaweza kufutwa tu ikiwa hana oda za ununuzi. Wachuuzi walio na historia ya oda huhifadhiwa kwa '
        'madhumuni ya uhasibu na ripoti.'
    ))
    el.append(spacer())

    # 6. Lango la muuzaji
    el.append(chapter('6. Lango la Muuzaji (Supplier Portal)'))
    el.append(hr())
    el.append(body(
        'Wachuuzi waliosajiliwa wanaweza kupokea vitambulisho vya kuingia ili waweze kutumia Lango la Muuzaji. Baada '
        'ya kuingia kwa barua pepe na nenosiri kutoka kwa mmiliki, muuzaji anaona dashibodi yenye kadi tatu za '
        'muhtasari: Jumla ya Oda, Inayosubiri Uwasilishaji na Imekamilika.'
    ))
    el += bullet_list([
        'Muuzaji anaweza kuona oda zote za ununuzi zilizopangiwa kwake.',
        'Kila oda inaonyesha namba ya PO, tarehe, bidhaa, gharama ya jumla, hali na tarehe inayotarajiwa.',
        'Maelezo ya oda yanaorodhesha bidhaa kamili, idadi na gharama za kitengo zitakazotolewa.',
        'Muuzaji anaweza kufungua oda na kuiweka kama Imepokelewa mara bidhaa zinapofikishwa.',
    ])
    el.append(spacer())

    # 7. Oda za ununuzi
    el.append(chapter('7. Oda za Ununuzi'))
    el.append(hr())
    el.append(body(
        'Oda ya ununuzi (PO) inaundwa na mmiliki wakati duka linahitaji kujaza bidhaa. Oda inarekodi muuzaji, '
        'bidhaa, idadi na gharama za kitengo. Kila PO inafuata hatua zifuatazo:'
    ))
    el.append(info_table([
        ('Rasimu (Draft)', 'Oda imeundwa lakini bado haijathibitishwa na muuzaji.'),
        ('Imeagizwa (Ordered)', 'Oda imetumwa kwa muuzaji na inasubiri uwasilishaji wa bidhaa.'),
        ('Imepokelewa (Received)', 'Muuzaji amefikisha bidhaa na oda imekamilika.'),
    ]))
    el.append(spacer())
    el.append(body(
        'Wakati muuzaji anapoweka oda kama Imepokelewa, hisa husasishwa kiotomatiki na bidhaa zinakuwa '
        'zinapatikana kwa ajili ya kuuzwa.'
    ))
    el.append(spacer())

    # 8. Msaada
    el.append(chapter('8. Msaada na Mawasiliano'))
    el.append(hr())
    el.append(body(
        'Kwa msaada kuhusu usajili, mahitaji ya nyaraka au matumizi ya lango, wasiliana na mmiliki wa duka au '
        'msimamizi wa mfumo. Mmiliki anasimamia rekodi za wachuuzi, uthibitishaji wa nyaraka na ufikiaji wa lango '
        'kutoka ukurasa wa Usimamizi wa Wachuuzi.'
    ))
    el.append(spacer())
    el.append(hr())
    el.append(Paragraph('<b>Duka la ERP Electronics</b> — Mwongozo wa Muuzaji Toleo 1.0 — Julai 2026', sFooter))
    el.append(Paragraph('Kwa msaada wa kiufundi, wasiliana na msimamizi wako wa mfumo.', sFooter))

    return el


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
    print(f'Generated: {path}')
    return path


if __name__ == '__main__':
    print('Generating English supplier manual...')
    build_pdf(build_en(), 'Supplier_Manual_EN.pdf')

    print('Generating Swahili supplier manual...')
    build_pdf(build_sw(), 'Supplier_Manual_SW.pdf')

    print('Done!')
