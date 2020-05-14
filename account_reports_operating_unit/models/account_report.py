import copy
import ast
from odoo.tools.misc import formatLang
from odoo import models, fields, api, _


class AccountFinancialHtmlReport(models.Model):
    _inherit = "account.financial.html.report"

    operating_unit = fields.Boolean("Show Operating Units")

    def _build_options(self, previous_options=None):
        res = super(AccountFinancialHtmlReport,
                    self)._build_options(previous_options)
        res['operating_unit'] = self.operating_unit
        return res

    def _get_columns_name(self, options):
        columns = [{'name': ''}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number'},
                        {'name': _('Credit'), 'class': 'number'}]
        if self.operating_unit:
            columns = [
                {'name': self.format_date(options)},
                {'name': self.env.user.default_operating_unit_id.name, 'class': 'number'}
            ]
            for ou in self.env.user.operating_unit_ids.filtered(lambda x: x != self.env.user.default_operating_unit_id):
                columns += [{'name': ou.name, 'class': 'number'}]

        else:
            columns += [{'name': self.format_date(options), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                columns += [{'name': period.get('string'), 'class': 'number'}]
            if options['comparison'].get('number_period') == 1 and not options.get('groups'):
                columns += [{'name': '%', 'class': 'number'}]

        if options.get('groups', {}).get('ids'):
            columns_for_groups = []
            for column in columns[1:]:
                for ids in options['groups'].get('ids'):
                    group_column_name = ''
                    for index, id in enumerate(ids):
                        column_name = self._get_column_name(
                            id, options['groups']['fields'][index])
                        group_column_name += ' ' + column_name
                    columns_for_groups.append(
                        {'name': column.get('name') + group_column_name, 'class': 'number'})
            columns = columns[:1] + columns_for_groups

        return columns

    
    def _get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.html.report.line'].search(
                [('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(
                periods=options['comparison']['periods'])
        if options.get('ir_filters'):
            line_obj = line_obj.with_context(periods=options.get('ir_filters'))

        currency_table = self._get_currency_table()
        domain, group_by = self._get_filter_info(options)

        if group_by:
            options['groups'] = {}
            options['groups']['fields'] = group_by
            options['groups']['ids'] = self._get_groups(domain, group_by)

        amount_of_periods = len(
            (options.get('comparison') or {}).get('periods') or []) + 1
        amount_of_group_ids = len(options.get(
            'groups', {}).get('ids') or []) or 1
        amount_of_ous = len(self.env.user.operating_unit_ids or []) or 1
        if self.operating_unit:
            linesDicts = [[{} for _ in range(0, amount_of_group_ids)]
                          for _ in range(0, amount_of_ous)]
        else:
            linesDicts = [[{} for _ in range(0, amount_of_group_ids)]
                          for _ in range(0, amount_of_periods)]

        res = line_obj.with_context(
            cash_basis=options.get('cash_basis'),
            filter_domain=domain,
        )._get_lines(self, currency_table, options, linesDicts)
        return res


class AccountFinancialHtmlReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    
    def _get_lines(self, financial_report, currency_table, options, linesDicts):
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get(
            'comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.user.company_id.currency_id.rounding

        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0

            if financial_report.operating_unit:
                for ou in self.env.user.operating_unit_ids:
                    rs = line.with_context(operating_unit_ids=[ou.id])._eval_formula(financial_report,
                                                                                     debit_credit,
                                                                                     currency_table,
                                                                                     linesDicts[k],
                                                                                     groups=options.get('groups'))
                    debit_credit = False
                    res.extend(rs)
                    for column in rs:
                        domain_ids.update(column)
                    k += 1
            else:
                for period in comparison_table:
                    date_from = period.get('date_from', False)
                    date_to = period.get(
                        'date_to', False) or period.get('date', False)
                    date_from, date_to, strict_range = line.with_context(
                        date_from=date_from, date_to=date_to)._compute_date_range()

                    rs = line.with_context(date_from=date_from,
                                           date_to=date_to,
                                           strict_range=strict_range)._eval_formula(financial_report,
                                                                                    debit_credit,
                                                                                    currency_table,
                                                                                    linesDicts[k],
                                                                                    groups=options.get('groups'))
                    debit_credit = False
                    res.extend(rs)
                    for column in rs:
                        domain_ids.update(column)
                    k += 1

            res = line._put_columns_together(res, domain_ids)

            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'level': line.level,
                'class': 'o_account_reports_totals_below_sections' if self.env.user.company_id.totals_below_sections else '',
                'columns': [{'name': l} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
                'page_break': line.print_on_new_page,
            }

            if financial_report.tax_report and line.domain and not line.action_id:
                vals['caret_options'] = 'tax.report.line'

            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(
                        list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    name = line._get_gb_name(domain_id)
                    if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
                        name = name[:40] + \
                            '...' if name and len(name) >= 45 else name
                    vals = {
                        'id': domain_id,
                        'name': name,
                        'level': line.level,
                        'parent_id': line.id,
                        'columns': [{'name': l} for l in res[domain_id]],
                        'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                        'financial_group_line_id': line.id,
                    }
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse(
                            [domain_id]).trust
                    lines.append(vals)
                if domain_ids and self.env.user.company_id.totals_below_sections:
                    lines.append({
                        'id': 'total_' + str(line.id),
                        'name': _('Total') + ' ' + line.name,
                        'level': line.level,
                        'class': 'o_account_reports_domain_total',
                        'parent_id': line.id,
                        'columns': copy.deepcopy(lines[0]['columns']),
                    })

            for vals in lines:
                if len(comparison_table) == 2 and not options.get('groups'):
                    vals['columns'].append(line._build_cmp(
                        vals['columns'][0]['name'], vals['columns'][1]['name']))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = [line._format(
                        v) for v in vals['columns']]
                if not line.formulas:
                    vals['columns'] = [{'name': ''} for k in vals['columns']]

            if len(lines) == 1:
                new_lines = line.children_ids._get_lines(
                    financial_report, currency_table, options, linesDicts)
                if new_lines and line.formulas:
                    if self.env.user.company_id.totals_below_sections:
                        divided_lines = self._divide_line(lines[0])
                        result = [divided_lines[0]] + \
                            new_lines + [divided_lines[-1]]
                    else:
                        result = [lines[0]] + new_lines
                else:
                    result = lines + new_lines
            else:
                result = lines
            final_result_table += result

        return final_result_table

