{
    "name": "Aisiki API Documentation",
    "summary": """Aisiki API Documentation""",
    "description": """
        Aisiki API Documentation
    """,
    "author": "My Company",
    "website": "http://www.yourcompany.com",
    "category": "Uncategorized",
    "version": "0.1",
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
        "auth_signup",
    ],
    "external_dependencies": {"python": ["jsondiff"]},
    "data": [
        # 'security/ir.model.access.csv',
        "views/views.xml",
        "views/templates.xml",
    ],
}
