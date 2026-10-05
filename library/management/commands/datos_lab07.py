from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from library.models import Autor, Libro, Lector, Prestamo
from library.services import guardar_prestamo

class Command(BaseCommand):
    help = "Carga datos identificables de laboratorio sin duplicarlos."

    @transaction.atomic
    def handle(self, *args, **options):
        nombres = [
            ("Gabriel García Márquez", "Colombiana"),
            ("Mario Vargas Llosa", "Peruana"),
            ("Isabel Allende", "Chilena"),
        ]
        autores = []
        for i, (nombre, nacionalidad) in enumerate(nombres, start=1):
            autor = Autor.objects.filter(nombre=f"LAB07 Autor {i}").first()
            if autor is None:
                autor, _ = Autor.objects.get_or_create(nombre=nombre)
            autor.nombre = nombre
            autor.nacionalidad = nacionalidad
            autor.save(update_fields=["nombre", "nacionalidad"])
            autores.append(autor)
        lector, _ = Lector.objects.get_or_create(email="lab07@example.com", defaults={"nombre": "LAB07 Lector"})
        libros = []
        catalogo = [
            ("Cien años de soledad", autores[0], 1967),
            ("La ciudad y los perros", autores[1], 1963),
            ("La casa de los espíritus", autores[2], 1982),
            ("El amor en los tiempos del cólera", autores[0], 1985),
            ("La tía Julia y el escribidor", autores[1], 1977),
        ]
        for i, (titulo, autor, anio) in enumerate(catalogo):
            # Mantener la clave de la muestra conserva préstamos y existencias.
            libro, _ = Libro.objects.get_or_create(isbn=f"LAB07-{i}", defaults={"titulo": titulo, "autor": autor, "anio": anio, "copias_disponibles": 20})
            libro.titulo = titulo
            libro.autor = autor
            libro.anio = anio
            libro.save(update_fields=["titulo", "autor", "anio"])
            libros.append(libro)
        if not Prestamo.objects.filter(lector=lector).exists():
            for i in range(8):
                guardar_prestamo(Prestamo(libro=libros[i % 5], lector=lector, cantidad=i % 3 + 1, monto=5+i, devuelto=i % 2 == 0, fecha_devolucion_esperada=date(2026,12,31)))
        self.stdout.write(self.style.SUCCESS("Datos LAB07 disponibles: 5 libros, 3 autores y 8 prestamos."))
