{
    "name": "Aisiki SMS",
    "summary": "Aisiki SMS",
    "description": """
    This plugin is used to overwrite the Odoo default SMS IAP.
    
    To Configure:
        * Go to the Settings > General Settings. 
        * Search for Aisiki Settings. 
    """,
    "version": "1.0",
    "depends": ["sms",],
    "category": "Tools",
    "author": "Babatope Ajepe",
    "data": ["views/res_config_settings.xml",],
    "application": False,
    "installable": True,
    "active": True,
}
