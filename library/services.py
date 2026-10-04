from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from .models import Libro, Prestamo


@transaction.atomic
def guardar_prestamo(prestamo):
    # Restaurar el stock anterior permite editar libro, cantidad o devolución.
    if prestamo.pk:
        anterior = Prestamo.objects.select_for_update().get(pk=prestamo.pk)
        if not anterior.devuelto:
            Libro.objects.filter(pk=anterior.libro_id).update(
                copias_disponibles=F("copias_disponibles") + anterior.cantidad)
    prestamo.estado = "DEVUELTO" if prestamo.devuelto else "ACTIVO"
    prestamo.full_clean()
    # Se guarda primero para demostrar que el error revierte también el registro.
    prestamo.save()
    if not prestamo.devuelto:
        actualizados = Libro.objects.filter(
            pk=prestamo.libro_id, disponible=True,
            copias_disponibles__gte=prestamo.cantidad,
        ).update(copias_disponibles=F("copias_disponibles") - prestamo.cantidad)
        if not actualizados:
            raise ValidationError("No hay copias suficientes o el libro está deshabilitado.")
    return prestamo


@transaction.atomic
def eliminar_prestamo_seguro(pk):
    prestamo = Prestamo.objects.select_for_update().get(pk=pk)
    if not prestamo.devuelto:
        Libro.objects.filter(pk=prestamo.libro_id).update(
            copias_disponibles=F("copias_disponibles") + prestamo.cantidad)
    prestamo.delete()
