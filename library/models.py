from django.db import models
from django.core.validators import MinValueValidator


class LibroQuerySet(models.QuerySet):
    def disponibles(self):
        return self.filter(disponible=True, copias_disponibles__gt=0)

    def con_relaciones(self):
        return self.select_related("autor", "editorial", "categoria")

    def por_categoria(self, categoria_id=None):
        return self.filter(categoria_id=categoria_id) if categoria_id else self



class Autor(models.Model):
    nombre = models.CharField(max_length=150)
    nacionalidad = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.nombre


class FichaAutor(models.Model):
    """Ficha complementaria del autor: solo existe si existe el Autor,
    y como máximo una por autor. Relación OneToOneField."""
    autor = models.OneToOneField(Autor, on_delete=models.CASCADE, related_name="ficha")
    biografia = models.TextField(blank=True)
    foto_url = models.URLField(blank=True)
    sitio_web = models.URLField(blank=True)

    def __str__(self):
        return f"Ficha de {self.autor.nombre}"


class Editorial(models.Model):
    nombre = models.CharField(max_length=150)
    pais = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Lector(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    objects = LibroQuerySet.as_manager()
    copias_disponibles = models.PositiveIntegerField(default=10)

    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name="libros")
    editorial = models.ForeignKey(
        Editorial, on_delete=models.SET_NULL, null=True, blank=True, related_name="libros"
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name="libros"
    )
    isbn = models.CharField(max_length=20)
    anio = models.IntegerField()
    disponible = models.BooleanField(default=True)
    lectores = models.ManyToManyField(Lector, through="Prestamo", related_name="libros_prestados")

    def __str__(self):
        return self.titulo


class Prestamo(models.Model):
    """Modelo intermedio de la relación N:M entre Lector y Libro.
    Guarda información propia de la relación: fechas y estado del préstamo."""
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    monto = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=10, choices=[("ACTIVO", "Activo"), ("DEVUELTO", "Devuelto")], default="ACTIVO")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    lector = models.ForeignKey(Lector, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.libro.titulo} → {self.lector.nombre}"
