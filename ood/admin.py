from django.contrib import admin

from ood import models


class OodAdminSite(admin.AdminSite):
    site_title = 'OoD Site Administration'
    site_header = 'OoD Administration'


admin_site = OodAdminSite(name='oodadmin')
admin_site.register(models.OodInstance)
admin_site.register(models.MineCraftServerSettings)
admin_site.register(models.ServerPlayerState)
admin_site.register(models.DropletState)
admin_site.register(models.SimpleServerState)
