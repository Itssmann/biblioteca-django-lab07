from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    path("reporte/", views.reporte, name="reporte"),
    path("libros/", views.listado_libros, name="listado_libros"),
    path("libros/nuevo/", views.crear_libro, name="crear_libro"),
    path("libros/<int:pk>/", views.detalle_libro, name="detalle_libro"),
    path("libros/<int:pk>/editar/", views.editar_libro, name="editar_libro"),
    path("libros/<int:pk>/eliminar/", views.eliminar_libro, name="eliminar_libro"),
    path("autores/", views.listado_autores, name="listado_autores"),
    path("autores/nuevo/", views.crear_autor, name="crear_autor"),
    path("autores/<int:pk>/", views.detalle_autor, name="detalle_autor"),
    path("autores/<int:pk>/editar/", views.editar_autor, name="editar_autor"),
    path("autores/<int:pk>/eliminar/", views.eliminar_autor, name="eliminar_autor"),
    path("autores/<int:autor_pk>/ficha/nueva/", views.crear_ficha_autor, name="crear_ficha_autor"),
    path("autores/<int:autor_pk>/ficha/editar/", views.editar_ficha_autor, name="editar_ficha_autor"),
    path("autores/<int:autor_pk>/ficha/eliminar/", views.eliminar_ficha_autor, name="eliminar_ficha_autor"),
    path("editoriales/", views.listado_editoriales, name="listado_editoriales"),
    path("editoriales/nueva/", views.crear_editorial, name="crear_editorial"),
    path("editoriales/<int:pk>/editar/", views.editar_editorial, name="editar_editorial"),
    path("editoriales/<int:pk>/eliminar/", views.eliminar_editorial, name="eliminar_editorial"),
    path("categorias/", views.listado_categorias, name="listado_categorias"),
    path("categorias/nueva/", views.crear_categoria, name="crear_categoria"),
    path("categorias/<int:pk>/editar/", views.editar_categoria, name="editar_categoria"),
    path("categorias/<int:pk>/eliminar/", views.eliminar_categoria, name="eliminar_categoria"),
    path("lectores/", views.listado_lectores, name="listado_lectores"),
    path("lectores/nuevo/", views.crear_lector, name="crear_lector"),
    path("lectores/<int:pk>/editar/", views.editar_lector, name="editar_lector"),
    path("lectores/<int:pk>/eliminar/", views.eliminar_lector, name="eliminar_lector"),
    path("prestamos/", views.listado_prestamos, name="listado_prestamos"),
    path("prestamos/nuevo/", views.crear_prestamo, name="crear_prestamo"),
    path("prestamos/<int:pk>/editar/", views.editar_prestamo, name="editar_prestamo"),
    path("prestamos/<int:pk>/eliminar/", views.eliminar_prestamo, name="eliminar_prestamo"),
]
