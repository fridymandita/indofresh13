# from datetime import date
# from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# from odoo.tools.safe_eval import safe_eval as eval
# from odoo.tools.translate import _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    entry = fields.Boolean(string='Available for Entry', default=True)

