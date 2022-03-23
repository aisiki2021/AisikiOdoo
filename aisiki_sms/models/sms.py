from odoo import models, fields
import threading
import requests


class AisikiSMS(models.Model):
    _inherit = "sms.sms"

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        overwrite = self.env["ir.config_parameter"].sudo().get_param("aisiki.overwrite.default")
        for batch_ids in self._split_batch():
            if not overwrite:
                self.browse(batch_ids)._send(delete_all=delete_all, raise_exception=raise_exception)
            else:
                self.browse(batch_ids).aisiki_send()
            # auto-commit if asked except in testing mode

            if auto_commit is True and not getattr(threading.currentThread(), "testing", False):
                self._cr.commit()

    def aisiki_send(self, delete_all=False, raise_exception=False):
        # todo: fix send sms option
        param_obj = self.env["ir.config_parameter"]
        url = "http://api.ebulksms.com:8080/sendsms.json"

        username = param_obj.sudo().get_param("aisiki.username")
        api_key = param_obj.sudo().get_param("aisiki.api.key")
        payload = {
            "SMS": {
                "auth": {"username": username, "apikey": api_key,},
                "message": {"sender": "AISIKI", "messagetext": self.body, "flash": "0",},
                "recipients": {"gsm": [{"msidn": self.number, "msgid": self.id},]},
                "dndsender": 1,
            }
        }
        response = requests.post(url, json=payload).json()
        self.write({"state": "sent" if response["response"]["status"].lower() == "success" else "error"})
        return response
