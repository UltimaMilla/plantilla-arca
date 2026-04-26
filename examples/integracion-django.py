"""
Ejemplo de integración ARCA en Django.

Caso de uso: Aplicación Django que gestiona facturas de clientes.
Auto-genera CAE al crear comprobantes con handlers de Django signals.

Uso:
    from invoices.models import Comprobante

    # Crear comprobante - auto-genera CAE
    comprobante = Comprobante.objects.create(
        cliente="Acme Corp",
        monto=1500.00,
        fecha=date.today()
    )

    # El signal handler llama automáticamente a generar_cae()
    print(comprobante.cae)  # Obtiene CAE desde ARCA
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings

logger = logging.getLogger(__name__)


class Comprobante(models.Model):
    """
    Modelo Django para gestionar comprobantes con integración ARCA.
    """

    # Opciones
    TIPO_CHOICES = [
        (1, "Factura A"),
        (6, "Factura B"),
        (11, "Factura C"),
    ]

    STATUS_CHOICES = [
        ("borrador", "Borrador"),
        ("pendiente_cae", "Pendiente CAE"),
        ("aprobado", "Aprobado (CAE)"),
        ("error", "Error"),
    ]

    # Campos básicos
    cliente = models.CharField(max_length=255, help_text="Razón social del cliente")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=date.today)
    descripcion = models.TextField(blank=True, null=True)

    # Campos ARCA
    tipo_comprobante = models.IntegerField(choices=TIPO_CHOICES, default=1)
    cae = models.CharField(max_length=14, blank=True, null=True, unique=True)
    vencimiento_cae = models.DateField(blank=True, null=True)
    numero_comprobante = models.IntegerField(blank=True, null=True)
    punto_venta = models.IntegerField(default=1)

    # Control
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="borrador"
    )
    mensaje_error = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]
        indexes = [
            models.Index(fields=["cliente"]),
            models.Index(fields=["cae"]),
            models.Index(fields=["status"]),
            models.Index(fields=["fecha"]),
        ]

    def __str__(self):
        return f"Comprobante {self.tipo_comprobante}/{self.punto_venta}/{self.numero_comprobante} - {self.cliente}"

    def generar_cae(self) -> bool:
        """
        Genera CAE solicitando a ARCA.

        Returns:
            bool: True si fue exitoso, False si falló.
        """
        if self.cae:
            logger.warning(f"Comprobante {self.id} ya tiene CAE: {self.cae}")
            return True

        try:
            # Importar dinámicamente para evitar dependencias circulares
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

            from arca.client import ArcaClient

            logger.info(f"Generando CAE para comprobante {self.id}")

            # Usar configuración de Django
            client = ArcaClient(
                cuit=settings.ARCA_CUIT,
                cert_path=settings.ARCA_CERT_PATH,
                key_path=settings.ARCA_KEY_PATH,
                homologacion=getattr(settings, "ARCA_HOMOLOGACION", True)
            )

            # Solicitar CAE
            response = client.solicitar_cae(
                tipo_comprobante=self.get_tipo_comprobante_display(),
                importe_total=float(self.monto)
            )

            # Guardar datos
            self.cae = response["cae"]
            self.numero_comprobante = int(response["numero"])
            self.vencimiento_cae = datetime.strptime(
                response["vencimiento"], "%Y%m%d"
            ).date()
            self.status = "aprobado"
            self.mensaje_error = None
            self.save(update_fields=[
                "cae", "numero_comprobante", "vencimiento_cae",
                "status", "mensaje_error"
            ])

            logger.info(
                f"CAE generado para comprobante {self.id}: {self.cae}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error generando CAE para comprobante {self.id}: {str(e)}",
                exc_info=True
            )
            self.status = "error"
            self.mensaje_error = str(e)
            self.save(update_fields=["status", "mensaje_error"])
            return False

    def puede_emitirse(self) -> bool:
        """Verificar si el comprobante puede ser emitido (tiene CAE válido)."""
        if not self.cae:
            return False
        if not self.vencimiento_cae:
            return False
        return self.vencimiento_cae >= date.today()


@receiver(post_save, sender=Comprobante)
def auto_generar_cae(sender, instance: Comprobante, created: bool, **kwargs):
    """
    Signal handler: Auto-genera CAE al crear comprobante.

    Se ejecuta automáticamente después de guardar un comprobante nuevo
    si está en estado 'borrador' y tiene monto > 0.
    """
    if created and instance.status == "borrador" and instance.monto > 0:
        logger.info(f"Signal: Auto-generando CAE para comprobante {instance.id}")
        instance.generar_cae()


# ============================================================================
# Ejemplos de uso en Django shell o vistas
# ============================================================================

"""
# En Django shell: python manage.py shell

# 1. Crear comprobante (dispara signal -> auto-genera CAE)
from invoices.models import Comprobante
from datetime import date

comprobante = Comprobante.objects.create(
    cliente="Acme Corp",
    monto=2500.00,
    fecha=date.today(),
    descripcion="Servicio de consultoría mes 04/2026",
    tipo_comprobante=1  # Factura A
)

print(f"CAE: {comprobante.cae}")
print(f"Status: {comprobante.status}")
print(f"Vencimiento: {comprobante.vencimiento_cae}")

# 2. Filtrar por status
aprobados = Comprobante.objects.filter(status="aprobado")
print(f"Comprobantes aprobados: {aprobados.count()}")

# 3. Filtrar por CAE (ej: verificar si existe)
existente = Comprobante.objects.filter(cae="12345678901234").first()
if existente:
    print(f"Encontrado: {existente.cliente}")

# 4. Obtener comprobantes emitibles
emitibles = [c for c in Comprobante.objects.all() if c.puede_emitirse()]
print(f"Comprobantes emitibles: {len(emitibles)}")

# 5. Re-intentar generar CAE para comprobantes en error
con_error = Comprobante.objects.filter(status="error")
for comp in con_error:
    if comp.generar_cae():
        print(f"✓ {comp.id} - CAE generado exitosamente")
    else:
        print(f"✗ {comp.id} - Falló: {comp.mensaje_error}")
"""
