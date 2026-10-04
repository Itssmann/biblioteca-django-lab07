from django import forms

from .models import Autor, Categoria, Editorial, FichaAutor, Lector, Libro, Prestamo


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ["nombre", "nacionalidad"]


class FichaAutorForm(forms.ModelForm):
    class Meta:
        model = FichaAutor
        fields = ["biografia", "foto_url", "sitio_web"]


class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = ["nombre", "pais"]


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]


class LectorForm(forms.ModelForm):
    class Meta:
        model = Lector
        fields = ["nombre", "email", "telefono"]


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ["titulo", "autor", "editorial", "categoria", "isbn", "anio", "disponible", "copias_disponibles"]


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ["libro", "lector", "fecha_devolucion_esperada", "cantidad", "monto", "devuelto"]

    def clean(self):
        datos = super().clean()
        libro = datos.get("libro")
        cantidad = datos.get("cantidad")
        if libro and cantidad and not datos.get("devuelto"):
            disponibles = libro.copias_disponibles
            if self.instance.pk:
                anterior = Prestamo.objects.get(pk=self.instance.pk)
                if anterior.libro_id == libro.pk and not anterior.devuelto:
                    disponibles += anterior.cantidad
            if not libro.disponible or cantidad > disponibles:
                raise forms.ValidationError("No hay copias suficientes o el libro está deshabilitado.")
        return datos
