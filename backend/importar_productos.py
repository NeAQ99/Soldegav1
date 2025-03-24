import os
import django
import pandas as pd

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SolDega.settings')
django.setup()

from bodega.models import Producto

# Nombre del archivo Excel
archivo = 'INVENTARIO A B.xlsx' # Se debe cambiar el nombre del archivo a importar y registrar en la carpeta backend, no tocar el script si no sabe, no sea aweonao

# Leer el archivo sin encabezados
df = pd.read_excel(archivo, header=None)

print(df.head(3))  # Solo para verificar que todo esté bien

# Iterar e importar productos
for index, row in df.iterrows():
    try:
        producto = Producto.objects.create(   #se leen los productos por fila, a partir de la columna A + 1 por cada fila para leer los datos
            codigo=str(row[3]).strip(),       # Columna D 
            nombre=str(row[4]).strip(),       # Columna E
            descripcion='n/a',
            categoria='pieza-equipo',
            tipo='inv',
            precio_compra=1000,
            stock_actual=int(row[5]),         # Columna F
            stock_minimo=3,
            consignacion=False,
            ubicacion=str(row[7]).strip()     # Columna H
        )
        print(f"✔ Producto creado: {producto.codigo}")
    except Exception as e:
        print(f"❌ Error en fila {index + 2}: {type(e).__name__} - {e}")
