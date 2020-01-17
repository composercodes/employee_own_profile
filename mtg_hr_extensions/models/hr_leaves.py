# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import math
import logging
_logger = logging.getLogger(__name__)

class leaveTypeExt(models.Model):
    _inherit = "hr.leave.type"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,required=True)  

class leaveExt(models.Model):
    _inherit = "hr.leave"

    @api.onchange('company_id')
    def fill_company_id(self):
        for rec in self:
            print("3333333333333333333")
            rec.holiday_status_id = False
            domain = {'holiday_status_id': [('company_id', '=', rec.company_id.id)]}
            return {'domain': domain}
        
class globalLeaves(models.Model):
    _name = "hr.global.leaves"
    _description = "Global Leaves"
    
    name = fields.Char(string='Name')
    year = fields.Selection([(num, str(num)) for num in range(2018, (datetime.now().year)+20 )], 'Year',required=True)
    date_from = fields.Date('From Date',required=True)
    date_to = fields.Date('To Date',required=True)

    @api.model
    def update_global_leaves(self):
        this_year = datetime.now().year
        global_leaves = self.env["hr.global.leaves"].search([('year', '=',this_year)])
        resource_leaves = self.env["resource.calendar.leaves"]
        resource_calendars = self.env["resource.calendar"]
        for calendar in resource_calendars:
            resource_calender_ids = resource_leaves.search([('calendar_id', '=',calendar.id),('resource_id', '=', None)])
            for leave in global_leaves:
                vals = {
                        'calendar_id': calendar.id,
                        'date_from': leave.date_from,
                        'date_to': leave.date_to,
                        }
                resource_calender = resource_leaves.search([('calendar_id', '=', calendar.id), ('date_from', '=', leave.date_from), ('date_to', '=', leave.date_to), ('resource_id', '=', None)])
                if resource_calender:
                    resource_calender.write(vals)
                else:
                    resource_leaves.create(vals)
                
class HolidayAllocationExtention(models.Model):
    _name = "hr.holidays.allocation"
    _description = "Holidays Allocation"
    
    leave_id = fields.Many2one('hr.leave.type', string='Leave Type',required=True)
    experience_from = fields.Char(required=True)
    experience_to = fields.Char(required=True)
    leaves_count = fields.Integer(required=True)
    company_id = fields.Many2one('res.company',string='Company',required=True)
    year = fields.Selection([(num, str(num)) for num in range(2010, (datetime.now().year)+20 )], 'Year',required=True)
    
    @api.onchange('company_id')
    def fill_company_id(self):
        for rec in self:
            rec.leave_id = False
            domain = {'leave_id': [('company_id', '=', rec.company_id.id)]}
            return {'domain': domain}
            
    def compute_holidays_values(self):
         #Get Employees List
        Contract = self.sudo().env['hr.contract']
        emplist= self.env['hr.employee'].sudo().search([])
        for employee in emplist :
            emp_id =employee.id
            emp_name = employee.name
            now = datetime.now().date()#+ relativedelta(years=+1)
            emp_contract = Contract.search([('employee_id', '=',emp_id),('state', '=','open')], order='date_start desc', limit=1)        
            if emp_contract:
                print(employee.years_of_experience)
                # if int(employee.years_of_experience) > 0:
                #     date_start = datetime.strptime(str(employee.job_start_date), '%Y-%m-%d')
                #     leave_date = date_start + relativedelta(years=-int(employee.years_of_experience))
                # else:
                #     date_start = datetime.strptime(str(employee.job_start_date), '%Y-%m-%d')
                #     leave_date = date_start + relativedelta(months=+6)
                #     print(leave_date)    
                # try : 
                #     date_from  = datetime.strptime(str(leave_date), '%Y-%m-%d %H:%M:%S').date()
                #     leave_date =datetime.strftime(date_from, "%Y-%m-%d")
                #     leave_date = datetime.strptime(str(leave_date), '%Y-%m-%d').date()
                # except:
                leave_date  = datetime.strptime(str(employee.leave_date), '%Y-%m-%d').date()
                print(leave_date)
                ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
                experiecneYears = 0
                experiecneMonths = 0
                experiodres = ending_day_of_current_year - leave_date
                experiodress= str(str(experiodres).split('days')[0])
                try:
                   experiecneYears = (float(experiodress)/365)
                   experiecneMonths = (float(experiodress)/30)
                except:
                   experiecneYears = 0
                   experiecneMonths = 0                           
                holidays_status_extention = self.sudo().env['hr.holidays.allocation'].search([('year', '=',now.year),('company_id', '=',employee.company_id.id)])
                for gcount in holidays_status_extention:
                    leavesCount = 0
                    if(float(experiecneYears) >=float(gcount.experience_from)):
                        if(float(experiecneYears) <=float(gcount.experience_to)):
                            leave_type = (gcount.leave_id.id)
                            if experiecneMonths >= 12 :  
                                leavesCount = (gcount.leaves_count)
                                
                            elif experiecneMonths < 12 :
                                if leave_date <= now  :
                                    leavesCount = int((gcount.leaves_count))
                                    print(leavesCount)
                                    monthly= leavesCount/12
                                    print(monthly)
                                    leavesCount = math.ceil(monthly * (experiecneMonths))
                            elif experiecneMonths < 0 :
                                leavesCount = 0
                            # if emp_contract.is_intern:
                            #     leavesCount = 0
                            #return False
                            hr_holidays = self.sudo().env['hr.leave.allocation'].search([('employee_id', '=',emp_id),('state', '=','validate'),('holiday_status_id', '=',leave_type)])
                            if hr_holidays :
                                print("yes")
                                print(leavesCount)
                                hr_holidays.sudo().write({'number_of_days':leavesCount})
                            else:
                                self.sudo().env['hr.leave.allocation'].create({
                                    'name': ("Allocation for "+str(emp_name)),
                                    'state': "validate",
                                    'employee_id': emp_id,
                                    'number_of_days':leavesCount,
                                    'type':"add",
                                    'holiday_type':"employee",
                                    'allocation_year':str(now.year),
                                    'holiday_status_id' : leave_type,
                                    # 'company_id':employee.company_id.id,
                                })   
                                    