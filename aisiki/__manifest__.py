{
    "name": "Aisiki API Documentation",
    "summary": """Aisiki API Documentation""",
    "description": """
        Aisiki API Documentation
    """,
    "author": "Babatope Ajepe",
    "website": "http://www.yourcompany.com",
    "category": "Uncategorized",
    "version": "1.0.8",
    "depends": [
        "base",
        "sale_management",
        "account_accountant",
        "stock",
        "hr",
        "contacts",
        "base_geolocalize",
        "base_rest",
        "base_rest_datamodel",
        "component",
        "website_sale",
        "auth_signup",
    ],
    "external_dependencies": {"python": ["jsondiff"]},
    "data": [
        # 'security/ir.model.access.csv',
        "views/product.xml",
        "views/res_users.xml",
        "views/res_partner.xml",
    ],
}
