from odoo import models, fields, api, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee',
                                  string='Related Employee', ondelete='restrict', auto_join=True,
                                  help='Employee-related data of the user')
    
class UserFromEmployee(models.Model):
    _inherit = 'hr.employee'
    
    leave_date = fields.Date(string='Allocation Start Date' ,compute="_compute_years_of_experience" )
    manual_allocation = fields.Boolean('Manual Allocation', default=False)    
    years_of_experience = fields.Integer(string='Years of Experience',compute="_compute_years_of_experience" )

    # compute leave date from years of experience
    @api.multi
    @api.depends('job_start_date')
    def _compute_years_of_experience(self):
        for rec in self:
            if rec.job_start_date:
                d1 = rec.job_start_date
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                years_of_experience = rd.years   
                rec.years_of_experience = int(years_of_experience)       
                if int(years_of_experience) > 0:
                    job_start_date = datetime.strptime(str(rec.job_start_date ), '%Y-%m-%d')
                    # leave_date = job_start_date + relativedelta(years=-int(years_of_experience))
                    leave_date =datetime.strftime(job_start_date, "%Y-%m-%d")
                    rec.leave_date = datetime.strptime(str(leave_date), '%Y-%m-%d').date()
                else:
                    job_start_date = datetime.strptime(str(rec.job_start_date), '%Y-%m-%d')
                    leave_date = job_start_date + relativedelta(months=+6)
                    leave_date =datetime.strftime(leave_date, "%Y-%m-%d")
                    rec.leave_date = datetime.strptime(str(leave_date), '%Y-%m-%d').date()

                
    @api.multi
    def create_user(self):
        """This code is to create an user while creating an employee."""
        values = {
            'name': str(self.name),
            'employee_id':self.id,
            'image': self.image,
            'company_id':self.company_id.id,
            'company_ids':[(6, 0, [self.company_id.id])],
            'login': str(self.work_email),
            'email': str(self.work_email),
            'active': True,
        }
        user_id = self.env['res.users'].sudo().create(values)
        self.user_id = user_id.id
        self.address_home_id = user_id.partner_id.id
        return True