from django.contrib import admin

from django.contrib import admin
from django.contrib.sessions.models import Session # <-- Importa el modelo Session

# Opcional: Clase para personalizar cómo se muestra Session en el admin
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data'] # Para que no puedas editar los datos serializados directamente
    search_fields = ['session_key']

    def _session_data(self, obj):
        # Decodifica los datos para mostrarlos legibles
        return obj.get_decoded()

# REGISTRA el modelo Session con Django Admin
admin.site.register(Session, SessionAdmin)
