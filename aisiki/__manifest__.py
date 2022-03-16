{
    "name": "Aisiki API Documentation",
    "summary": """Aisiki API Documentation""",
    "description": """
        Aisiki API Documentation
    """,
    "author": "Babatope Ajepe",
    "website": "http://www.yourcompany.com",
    "category": "Uncategorized",
    "version": "1.1.1",
    "depends": [
        "base",
        "sms",
        "sale_management",
        "account_accountant",
        "stock",
        "hr",
        "aisiki_sms",
        "contacts",
        "base_geolocalize",
        "base_rest",
        "base_rest_datamodel",
        "component",
        "website_sale",
        "auth_signup",
        "l10n_generic_coa",
        "sale_commission",
        "go_sales_order_delivery_status",
    ],
    "external_dependencies": {"python": ["jsondiff"]},
    "data": [
        # 'security/ir.model.access.csv',
        "views/product.xml",
        "views/res_partner.xml",
        "data/account_journal.xml",
    ],
}
