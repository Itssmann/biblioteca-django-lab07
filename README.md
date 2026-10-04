# Biblioteca Django — Semana 7

Aplicación de biblioteca con Django 5, ORM y SQLite. Los datos persisten al reiniciar el servidor. Incluye `core` (inicio y plantilla base) y `library` (gestión de la biblioteca).

## Instalación y ejecución en Windows

Requiere Python 3.10 o superior. Desde la carpeta que contiene `manage.py`, ejecuta en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py datos_lab07
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

`createsuperuser` crea la cuenta para el Admin. Las pantallas públicas no requieren esa cuenta.

## Entidades y pantallas

| Entidad | URL pública | Operaciones |
| --- | --- | --- |
| Autor | `/library/autores/` | Listar, crear, ver detalle, editar y eliminar |
| FichaAutor | Desde `/library/autores/<id>/` | Consultar, crear, editar y eliminar la ficha |
| Libro | `/library/libros/` | Listar, crear, ver detalle, editar y eliminar |
| Editorial | `/library/editoriales/` | Listar, crear, editar y eliminar |
| Categoria | `/library/categorias/` | Listar, crear, editar y eliminar |
| Lector | `/library/lectores/` | Listar, crear, editar y eliminar |
| Prestamo | `/library/prestamos/` | Listar, crear, editar y eliminar |

Inicio: `http://127.0.0.1:8000/`. Catálogo: `http://127.0.0.1:8000/library/libros/`. Administración: `http://127.0.0.1:8000/admin/`.

Las siete entidades están registradas en el Admin. Autor incorpora su ficha como inline y Libro incorpora los préstamos como inline.

Relaciones implementadas:

- **1:1:** Autor y FichaAutor mediante `OneToOneField`.
- **1:N:** Autor, Editorial y Categoria con Libro mediante `ForeignKey`.
- **N:M:** Libro y Lector mediante `Prestamo`, que guarda fechas y estado de devolución.

La ficha se consulta desde el detalle del autor. Eliminarla conserva al autor y sus libros. Eliminar un autor también elimina sus libros y los registros dependientes por las relaciones en cascada.

## Refactorización de plantillas — Semana 7

`core/templates/base.html` centraliza encabezado, navegación, estilos y pie de página; define un bloque `content` vacío. Las pantallas completas usan `{% extends "base.html" %}` y `{% block content %}`. Los fragmentos incluidos se insertan dentro de esas pantallas y no necesitan heredar de la base.

| Plantillas en `library/templates/library/` | Cambios y entidades |
| --- | --- |
| `libro_listado.html`, `libro_formulario.html`, `libro_confirmar_eliminar.html` | Herencia para Libro; `upper` sobre el autor y comentarios en el listado |
| `autor_listado.html`, `autor_formulario.html`, `autor_confirmar_eliminar.html` | Herencia para Autor; `length` sobre sus libros y `default` sobre nacionalidad |
| `autor_detalle.html`, `ficha_formulario.html` | Herencia y relación 1:1; comentarios, `default`, `length` y `pluralize` |
| `libro_detalle.html`, `prestamo_listado.html` | Herencia, relaciones e historial de préstamos; filtro `date:"d/m/Y"` y estado compartido |
| `editorial_*`, `categoria_*`, `lector_*`, `prestamo_formulario.html`, `prestamo_confirmar_eliminar.html` | Herencia en listados, formularios y confirmaciones de las demás entidades |

La nueva confirmación `ficha_confirmar_eliminar.html` completa la eliminación pública de FichaAutor y también hereda de la base. El inicio en `core/templates/core/inicio.html` usa la misma estructura.

Fragmentos reutilizados con `{% include %}`:

- `_acciones_cell.html`: acciones en `libro_listado.html`, `autor_listado.html` y `prestamo_listado.html`.
- `_prestamo_estado.html`: estado Devuelto/Pendiente en `libro_detalle.html` y `prestamo_listado.html`.

Los comentarios `{# ... #}` explican las relaciones y la reutilización y no aparecen en el HTML renderizado. Las plantillas antiguas `listado.html` y `formulario.html` se conservan, pero las vistas actuales utilizan `libro_listado.html` y `libro_formulario.html`.

Esta organización permite mantener una presentación común y modificar los fragmentos compartidos en un solo lugar. El Admin ofrece gestión interna de los modelos; las vistas y plantillas propias ofrecen navegación y presentación adaptadas a la biblioteca mediante sus URLs públicas.

## Comprobación funcional y autoescape

Estas son instrucciones de verificación; no representan pruebas ya ejecutadas.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

1. Crea un autor, su ficha, una editorial, una categoría y un lector. Crea un libro con esas relaciones y registra un préstamo.
2. Revisa los listados y los detalles del autor y del libro. Comprueba la ficha, los libros asociados, las fechas y el estado del préstamo.
3. Edita los registros y verifica los cambios. Prueba cancelar una eliminación y luego confirmarla. Elimina primero los préstamos y la ficha, después el libro y finalmente los registros restantes. Comprueba que eliminar una ficha conserva su autor.
4. En un autor de prueba, introduce `<script>alert('prueba')</script>` como nombre y guarda. Abre el listado o su detalle y consulta el código fuente del navegador: las etiquetas deben aparecer como `&lt;script&gt;` y `&lt;/script&gt;`, y no debe ejecutarse ninguna alerta. Repite en la biografía de una ficha para comprobar la pantalla con relación.
5. Comprueba que las pantallas siguen bajo `/library/` y que los formularios permiten crear, editar y eliminar después de la refactorización.

Se mantiene el autoescape predeterminado de Django y los formularios POST incorporan `{% csrf_token %}`. Para la entrega, documenta las pruebas con capturas del código antes/después, las páginas renderizadas y el código fuente con el valor escapado.

Repositorio: https://github.com/Itssmann/biblioteca-django-lab07


## Laboratorio 07: ORM avanzado (biblioteca)

- Libro.copias_disponibles es el entero descontable. Prestamo incorpora cantidad, monto y estado; conserva devuelto para compatibilidad con el CRUD.
- `/library/prestamos/nuevo/` ejecuta una transaccion atomic mediante guardar_prestamo: guarda el prestamo y descuenta copias con F(), condicionado a existencias suficientes. El error revierte todo y se muestra en el formulario; el exito redirige (PRG). Editar, devolver y eliminar ajustan las copias en la misma transaccion.
- `/library/reporte/` muestra suma de cantidad por monto (aggregate), numero de prestamos por libro (annotate/Count) y agrupacion por estado (values/annotate). Hereda base.html y aplica floatformat.
- LibroQuerySet usa as_manager(); disponibles(), con_relaciones() y por_categoria() son encadenables. Listado y reporte reutilizan estos metodos.
- `python manage.py datos_lab07` carga cinco libros, tres autores y ocho prestamos identificados como LAB07. Es repetible y no borra datos anteriores. Tambien se pueden registrar desde el Admin.
- `python manage.py medir_consultas` mide connection.queries despues de reset_queries con DEBUG=True. En la copia actual: 6 libros, FK 7 -> 1 consultas; N:M 7 -> 2. select_related usa JOIN para FK/1:1; prefetch_related hace consultas separadas y agrupa las colecciones N:M/inversas en Python.
- `python manage.py test library` comprueba exito, rollback de alta y edicion, devolucion, eliminacion, PRG, reporte y optimizacion.

Las copias iniciales de los libros anteriores se fijan en 10 mediante migracion: representan existencias disponibles al iniciar Semana07. Los prestamos historicos mantienen cantidad=1 y monto=0; la migracion 0003 sincroniza su estado con devuelto.

### Consultas para el shell y justificacion

```python
from django.db.models import Sum, F, Count
from library.models import Prestamo, Libro
Prestamo.objects.aggregate(total=Sum(F("cantidad") * F("monto"), default=0))
Libro.objects.annotate(total=Count("prestamo")).order_by("-total")
Prestamo.objects.values("estado").annotate(total=Count("id")).order_by("-total")
```

aggregate devuelve un diccionario porque resume toda la consulta en valores, sin representar una lista de objetos. annotate conserva los objetos o grupos y agrega un calculo a cada uno. atomic evita operaciones parciales; F hace el descuento en la base de datos y el filtro de existencias evita valores negativos. El QuerySet concentra consultas reutilizables.

### Entrega

Las partes 1 y 2 del laboratorio corresponden a este mismo proyecto de biblioteca. La investigación propia contiene las cinco entidades originales (Autor, Libro, Editorial, Categoria y Lector), FichaAutor (1:1) y Prestamo (intermedio N:M). Los ejercicios 9-13 usan estas siete entidades: descuento de Libro.copias_disponibles con F() dentro de transaction.atomic(), estado de Prestamo, total de cantidad × monto, reportes por libro y estado, LibroQuerySet reutilizado en listado y reporte, y medición de consultas antes y después de optimizar.

La entrega del laboratorio incluye además el documento Word con respuestas, justificaciones y capturas de ambas partes sobre esta biblioteca. Capturar migraciones, datos en el Admin, formulario exitoso/fallido, conteos antes/después del rollback, reporte y salida de medir_consultas. El comando de datos permite reproducir la muestra, pero no acredita por sí solo la carga manual desde el Admin solicitada en el ejercicio 2.


### Verificacion ejecutada el 4 de octubre de 2026

Django 5.2.17: cinco pruebas aprobadas (transacciones, rollback, PRG, reportes y N+1). `manage.py check` sin incidencias; `makemigrations --check --dry-run` sin cambios. Base local: seis libros, cuatro autores y nueve prestamos. Medicion real: FK 7 -> 1 consultas; N:M 7 -> 2 consultas. La base SQLite local y las cuentas de usuario se excluyen del repositorio; ejecutar `datos_lab07` para reproducir los datos de ejemplo.
