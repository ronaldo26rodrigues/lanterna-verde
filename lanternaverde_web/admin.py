from django.contrib import admin
from .models import Usuario, Administrador, Analista, Empresa

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Administrador)
admin.site.register(Analista)
admin.site.register(Empresa)
