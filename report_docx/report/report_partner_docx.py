from odoo import models


class PartnerDocx(models.AbstractModel):
    _name = 'report.report_docx.partner_docx'
    _description = 'Partner Docx'
    _inherit = 'report.report_docx.abstract'
