from datetime import date
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Autor, Libro, Lector, Prestamo
from .services import guardar_prestamo, eliminar_prestamo_seguro

class LaboratorioTests(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nombre="Autor")
        self.libro = Libro.objects.create(titulo="Libro", autor=self.autor, isbn="123", anio=2026, copias_disponibles=3)
        self.lector = Lector.objects.create(nombre="Lector", email="lector@example.com")

    def nuevo(self, cantidad=2):
        return Prestamo(libro=self.libro, lector=self.lector, cantidad=cantidad, monto=5, fecha_devolucion_esperada=date(2026,12,31))

    def test_exito_edicion_devolucion_eliminacion(self):
        prestamo = guardar_prestamo(self.nuevo())
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.copias_disponibles, 1)
        prestamo.cantidad = 3
        guardar_prestamo(prestamo)
        prestamo.devuelto = True
        guardar_prestamo(prestamo)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.copias_disponibles, 3)
        self.assertEqual(prestamo.estado, "DEVUELTO")
        eliminar_prestamo_seguro(prestamo.pk)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.copias_disponibles, 3)

    def test_rollback_completo(self):
        antes = (Libro.objects.count(), Prestamo.objects.count(), self.libro.copias_disponibles)
        with self.assertRaises(ValidationError):
            guardar_prestamo(self.nuevo(4))
        self.libro.refresh_from_db()
        self.assertEqual(antes, (Libro.objects.count(), Prestamo.objects.count(), self.libro.copias_disponibles))

    def test_edicion_fallida_restaura_registro_y_stock(self):
        prestamo = guardar_prestamo(self.nuevo())
        prestamo.cantidad = 4
        with self.assertRaises(ValidationError):
            guardar_prestamo(prestamo)
        prestamo.refresh_from_db()
        self.libro.refresh_from_db()
        self.assertEqual((prestamo.cantidad, self.libro.copias_disponibles), (2, 1))

    def test_vista_prg_error_y_reporte(self):
        url = reverse("library:crear_prestamo")
        datos = {"libro": self.libro.pk, "lector": self.lector.pk, "cantidad": 2, "monto": "5.00", "fecha_devolucion_esperada": "2026-12-31"}
        self.assertEqual(self.client.post(url, datos).status_code, 302)
        respuesta = self.client.post(url, datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "No hay copias suficientes")
        respuesta = self.client.get(reverse("library:reporte"))
        self.assertEqual(respuesta.context["totales"]["importe"], 10)
        for nombre in ("listado_libros", "listado_autores", "listado_editoriales", "listado_categorias", "listado_lectores", "listado_prestamos"):
            self.assertEqual(self.client.get(reverse("library:" + nombre)).status_code, 200)

    def test_consultas(self):
        for i in range(4):
            Libro.objects.create(titulo=str(i), autor=self.autor, isbn=str(i), anio=2026)
        with self.assertNumQueries(6):
            antes = [(l.titulo, l.autor.nombre) for l in Libro.objects.all()]
        with self.assertNumQueries(1):
            despues = [(l.titulo, l.autor.nombre) for l in Libro.objects.con_relaciones()]
        self.assertEqual(antes, despues)
