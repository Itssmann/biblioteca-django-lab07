from django.db import migrations

def estados(apps, schema_editor):
    Prestamo = apps.get_model("library", "Prestamo")
    Prestamo.objects.filter(devuelto=True).update(estado="DEVUELTO")

class Migration(migrations.Migration):
    dependencies = [("library", "0002_libro_copias_disponibles_prestamo_cantidad_and_more")]
    operations = [migrations.RunPython(estados, migrations.RunPython.noop)]
