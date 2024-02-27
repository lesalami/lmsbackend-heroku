"""
Admin view for the Financial models
"""
from django.contrib import admin

from finance import models


class IncomeAdmin(admin.ModelAdmin):
    """Admin view for the income model"""
    list_display = ["income_type", "amount"]
    list_per_page = 10


class ExpenditureAdmin(admin.ModelAdmin):
    """Admin view for the expenditure model"""
    list_display = ["expenditure_type", "payment_type", "amount"]
    list_per_page = 10


admin.site.register(models.Supplier)
admin.site.register(models.TaxConfig)
admin.site.register(models.Tax)
admin.site.register(models.Payroll)
admin.site.register(models.PaymentDetail)
admin.site.register(models.SalaryBand)
admin.site.register(models.IncomeType)
admin.site.register(models.Income, IncomeAdmin)
admin.site.register(models.ExpenditureType)
admin.site.register(models.Expenditure, ExpenditureAdmin)
admin.site.register(models.Receipt)
admin.site.register(models.PayrollRun)
