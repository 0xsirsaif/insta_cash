from django.contrib import admin

from .models import Customer, Task, Transaction, User


class TransactionAdmin(admin.ModelAdmin):
	list_display = ("id", "collector", "manager", "amount", "timestamp", "deleted")


class TaskAdmin(admin.ModelAdmin):
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "manager":
			kwargs["queryset"] = User.objects.filter(is_manager=True)
		if db_field.name == "collector":
			kwargs["queryset"] = User.objects.filter(is_manager=False)

		return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Task, TaskAdmin)
admin.site.register(Transaction, TransactionAdmin)
