from odoo import models
import uuid


class RestCr(models.Model):
    _name = 'rest.cr'
    _description = 'rest handler'

    def login(self, uid):
        result = {}
        res_user_doc = self.env['res.users'].browse(uid)
        # Supaya returnya hanya satu User
        res_user = res_user_doc.read(['name'])[0]
        result['res_user'] = res_user
        search_list = [['user_id', '=', uid], ['state', '=', 'granted']]
        refresh_token_doc = self.env['refresh.token'].sudo().search(
            search_list, limit=1)
        if not refresh_token_doc.exists():
            refresh_token = uuid.uuid1().hex
            self.env['refresh.token'].sudo().create(
                {"name": refresh_token, "user_id": uid})
        else:
            refresh_token = refresh_token_doc.name

        result['refresh_token'] = refresh_token
        return result

    def get_refresh_token(self, uid, refresh_token):
        uid = int(uid)
        search_list = [['user_id', '=', uid], [
            'name', '=', refresh_token], ['state', '=', 'granted']]
        refresh_token_doc = self.env['refresh.token'].search(
            search_list, limit=1)
        if not refresh_token_doc.exists():
            return False
        return (refresh_token_doc.user_id.id, refresh_token_doc.user_id.name)

    def api_get_model(self, model_name, field_list, model_id=False, limit=False, offset=False):
        if model_id:
            model_ids = self.env[model_name].sudo().browse(model_id)
        else:
            model_ids = self.env[model_name].sudo().search(
                [], limit=limit, offset=offset)
        result = model_ids.read(field_list, load=False)
        count_result = len(result)
        return result, count_result
