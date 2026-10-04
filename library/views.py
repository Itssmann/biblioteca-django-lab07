from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper
from .services import guardar_prestamo, eliminar_prestamo_seguro

from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AutorForm,
    CategoriaForm,
    EditorialForm,
    FichaAutorForm,
    LectorForm,
    LibroForm,
    PrestamoForm,
)
from .models import Autor, Categoria, Editorial, FichaAutor, Lector, Libro, Prestamo


def listado_libros(request):
    libros = Libro.objects.con_relaciones().por_categoria(request.GET.get("categoria")).order_by("titulo")
    return render(request, "library/libro_listado.html", {"libros": libros})


def crear_libro(request):
    form = LibroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_libros")
    return render(request, "library/libro_formulario.html", {"form": form})


def editar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    form = LibroForm(request.POST or None, instance=libro)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_libros")
    return render(request, "library/libro_formulario.html", {"form": form, "editar": True})


def eliminar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.method == "POST":
        libro.delete()
        return redirect("library:listado_libros")
    return render(request, "library/libro_confirmar_eliminar.html", {"libro": libro})


def listado_autores(request):
    autores = Autor.objects.order_by("nombre")
    return render(request, "library/autor_listado.html", {"autores": autores})


def crear_autor(request):
    form = AutorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_autores")
    return render(request, "library/autor_formulario.html", {"form": form})


def editar_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    form = AutorForm(request.POST or None, instance=autor)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_autores")
    return render(request, "library/autor_formulario.html", {"form": form, "editar": True})


def eliminar_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == "POST":
        autor.delete()
        return redirect("library:listado_autores")
    return render(request, "library/autor_confirmar_eliminar.html", {"autor": autor})


# ---------- Ejercicio 6/7: detalle con relaciones (select_related / prefetch_related) ----------

def detalle_autor(request, pk):
    autor = get_object_or_404(Autor.objects.select_related("ficha"), pk=pk)
    libros = autor.libros.all()
    return render(request, "library/autor_detalle.html", {"autor": autor, "libros": libros})


def detalle_libro(request, pk):
    libro = get_object_or_404(
        Libro.objects.select_related("autor", "editorial", "categoria").prefetch_related(
            "prestamo_set__lector"
        ),
        pk=pk,
    )
    prestamos = libro.prestamo_set.all()
    return render(request, "library/libro_detalle.html", {"libro": libro, "prestamos": prestamos})


# ---------- Ficha del autor (1:1) ----------

def crear_ficha_autor(request, autor_pk):
    autor = get_object_or_404(Autor, pk=autor_pk)
    if FichaAutor.objects.filter(autor=autor).exists():
        return redirect("library:editar_ficha_autor", autor_pk=autor.pk)
    form = FichaAutorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ficha = form.save(commit=False)
        ficha.autor = autor
        ficha.save()
        return redirect("library:detalle_autor", pk=autor.pk)
    return render(request, "library/ficha_formulario.html", {"form": form, "autor": autor})


def editar_ficha_autor(request, autor_pk):
    autor = get_object_or_404(Autor, pk=autor_pk)
    ficha = get_object_or_404(FichaAutor, autor=autor)
    form = FichaAutorForm(request.POST or None, instance=ficha)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:detalle_autor", pk=autor.pk)
    return render(request, "library/ficha_formulario.html", {"form": form, "autor": autor, "editar": True})


def eliminar_ficha_autor(request, autor_pk):
    autor = get_object_or_404(Autor, pk=autor_pk)
    ficha = get_object_or_404(FichaAutor, autor=autor)
    if request.method == "POST":
        ficha.delete()
        return redirect("library:detalle_autor", pk=autor.pk)
    return render(request, "library/ficha_confirmar_eliminar.html", {"autor": autor})


# ---------- CRUD Editorial ----------

def listado_editoriales(request):
    editoriales = Editorial.objects.order_by("nombre")
    return render(request, "library/editorial_listado.html", {"editoriales": editoriales})


def crear_editorial(request):
    form = EditorialForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_editoriales")
    return render(request, "library/editorial_formulario.html", {"form": form})


def editar_editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    form = EditorialForm(request.POST or None, instance=editorial)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_editoriales")
    return render(request, "library/editorial_formulario.html", {"form": form, "editar": True})


def eliminar_editorial(request, pk):
    editorial = get_object_or_404(Editorial, pk=pk)
    if request.method == "POST":
        editorial.delete()
        return redirect("library:listado_editoriales")
    return render(request, "library/editorial_confirmar_eliminar.html", {"editorial": editorial})


# ---------- CRUD Categoria ----------

def listado_categorias(request):
    categorias = Categoria.objects.order_by("nombre")
    return render(request, "library/categoria_listado.html", {"categorias": categorias})


def crear_categoria(request):
    form = CategoriaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_categorias")
    return render(request, "library/categoria_formulario.html", {"form": form})


def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_categorias")
    return render(request, "library/categoria_formulario.html", {"form": form, "editar": True})


def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        return redirect("library:listado_categorias")
    return render(request, "library/categoria_confirmar_eliminar.html", {"categoria": categoria})


# ---------- CRUD Lector ----------

def listado_lectores(request):
    lectores = Lector.objects.order_by("nombre")
    return render(request, "library/lector_listado.html", {"lectores": lectores})


def crear_lector(request):
    form = LectorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_lectores")
    return render(request, "library/lector_formulario.html", {"form": form})


def editar_lector(request, pk):
    lector = get_object_or_404(Lector, pk=pk)
    form = LectorForm(request.POST or None, instance=lector)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("library:listado_lectores")
    return render(request, "library/lector_formulario.html", {"form": form, "editar": True})


def eliminar_lector(request, pk):
    lector = get_object_or_404(Lector, pk=pk)
    if request.method == "POST":
        lector.delete()
        return redirect("library:listado_lectores")
    return render(request, "library/lector_confirmar_eliminar.html", {"lector": lector})


# ---------- CRUD Prestamo (modelo intermedio N:M) ----------

def listado_prestamos(request):
    prestamos = Prestamo.objects.select_related("libro", "lector").order_by("-fecha_prestamo")
    return render(request, "library/prestamo_listado.html", {"prestamos": prestamos})


def crear_prestamo(request):
    form = PrestamoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                guardar_prestamo(form.save(commit=False))
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("library:listado_prestamos")
    return render(request, "library/prestamo_formulario.html", {"form": form})


def editar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    form = PrestamoForm(request.POST or None, instance=prestamo)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                guardar_prestamo(form.save(commit=False))
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("library:listado_prestamos")
    return render(request, "library/prestamo_formulario.html", {"form": form, "editar": True})


def eliminar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == "POST":
        eliminar_prestamo_seguro(prestamo.pk)
        return redirect("library:listado_prestamos")
    return render(request, "library/prestamo_confirmar_eliminar.html", {"prestamo": prestamo})


def reporte(request):
    importe = ExpressionWrapper(F("cantidad") * F("monto"), output_field=DecimalField(max_digits=14, decimal_places=2))
    totales = Prestamo.objects.aggregate(unidades=Sum("cantidad", default=0), importe=Sum(importe, default=0))
    ranking = Libro.objects.con_relaciones().por_categoria(request.GET.get("categoria")).annotate(total_prestamos=Count("prestamo")).order_by("-total_prestamos", "titulo")
    estados = Prestamo.objects.values("estado").annotate(total=Count("id"), unidades=Sum("cantidad")).order_by("-total")
    disponibles = Libro.objects.disponibles().con_relaciones()
    return render(request, "library/reporte.html", {"totales": totales, "ranking": ranking, "estados": estados, "disponibles": disponibles})
