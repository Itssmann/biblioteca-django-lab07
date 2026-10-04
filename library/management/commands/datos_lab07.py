from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from library.models import Autor, Libro, Lector, Prestamo
from library.services import guardar_prestamo

class Command(BaseCommand):
    help = "Carga datos identificables de laboratorio sin duplicarlos."

    @transaction.atomic
    def handle(self, *args, **options):
        autores = [Autor.objects.get_or_create(nombre=f"LAB07 Autor {i}")[0] for i in range(1, 4)]
        lector, _ = Lector.objects.get_or_create(email="lab07@example.com", defaults={"nombre": "LAB07 Lector"})
        libros = []
        for i in range(5):
            libro, _ = Libro.objects.get_or_create(isbn=f"LAB07-{i}", defaults={"titulo": f"LAB07 Libro {i+1}", "autor": autores[i % 3], "anio": 2026, "copias_disponibles": 20})
            libros.append(libro)
        if not Prestamo.objects.filter(lector=lector).exists():
            for i in range(8):
                guardar_prestamo(Prestamo(libro=libros[i % 5], lector=lector, cantidad=i % 3 + 1, monto=5+i, devuelto=i % 2 == 0, fecha_devolucion_esperada=date(2026,12,31)))
        self.stdout.write(self.style.SUCCESS("Datos LAB07 disponibles: 5 libros, 3 autores y 8 prestamos."))
