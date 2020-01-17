from odoo import models, fields, api, _

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    resource_calendar_ids = fields.One2many(
        'resource.calendar',
        'company_id',
        string='Working Times',
    )
    
    resource_calendar_count = fields.Integer(
        string='Number of Working',
        compute='_get_working_times_count',
    )
    
    leave_types_ids = fields.One2many(
        'hr.leave.type',
        'company_id',
        string='Leave Types',
    )
    Leaves_count = fields.Integer(
        string='Number of Leaves',
        compute='_get_Leaves_count',
    )
    
    allocation_ids = fields.One2many(
        'hr.holidays.allocation',
        'company_id',
        string='Leaves Allocation',
    )
    allocation_count = fields.Integer(
        string='Number of Allocation',
        compute='_get_allocation_count',
    )
    
    @api.one
    @api.depends('allocation_ids')
    def _get_allocation_count(self):
        self.allocation_count = len(self.allocation_ids)
        
    @api.one
    @api.depends('resource_calendar_ids')
    def _get_working_times_count(self):
        self.resource_calendar_count = len(self.resource_calendar_ids)
        
    @api.one
    @api.depends('leave_types_ids')
    def _get_Leaves_count(self):
        self.Leaves_count = len(self.leave_types_ids)
        
    support_outgoining_mail = fields.Boolean(string="Support Use Outgoining Email",
                                       help="Use to apply website support to use outgoning mail instead of company mail")
    outgoining_mail  = fields.Many2one('ir.mail_server')

    
class SupportInherit(models.Model):
    _inherit = 'website.support.ticket'

    outgoining_mail  = fields.Many2one('ir.mail_server')