from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, reset_queries
from library.models import Libro

class Command(BaseCommand):
    help = "Compara consultas sobre exactamente los mismos datos."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Esta medicion requiere DEBUG=True")
        for etiqueta, consulta in [("Antes FK", Libro.objects.all()), ("Despues FK", Libro.objects.select_related("autor"))]:
            reset_queries()
            filas = [(l.titulo, l.autor.nombre) for l in consulta]
            self.stdout.write(f"{etiqueta}: {len(connection.queries)} consultas; {len(filas)} libros")
        for etiqueta, consulta in [("Antes N:M", Libro.objects.all()), ("Despues N:M", Libro.objects.prefetch_related("lectores"))]:
            reset_queries()
            filas = [(l.titulo, [r.nombre for r in l.lectores.all()]) for l in consulta]
            self.stdout.write(f"{etiqueta}: {len(connection.queries)} consultas; {len(filas)} libros")
