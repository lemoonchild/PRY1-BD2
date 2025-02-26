import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Obtener el directorio base del proyecto (donde se está ejecutando el script)
base_dir = os.getcwd()  # Ruta absoluta del directorio actual
csv_dir = os.path.join(base_dir, "src", "csvData")  # Ruta absoluta para los CSVs


# Función para generar fechas aleatorias
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

start_date = datetime(2015, 1, 1)
end_date = datetime(2025, 1, 1)

# Definir categorías principales y subcategorías
category_groups = ["Gaming", "Audio", "Peripherals", "PC Components", "Networking", "Storage", "Cooling", "Power Supplies"]
subcategories = {
    "Gaming": ["Gaming Chair", "Gaming Mouse", "Gaming Keyboard", "Gaming Headset"],
    "Audio": ["Speakers", "Headphones", "Microphones", "Sound Cards"],
    "Peripherals": ["Mouse", "Keyboard", "Monitor", "Printer"],
    "PC Components": ["GPU", "CPU", "Motherboard", "RAM", "SSD", "HDD"],
    "Networking": ["Router", "Switch", "Network Card", "Modem"],
    "Storage": ["External HDD", "External SSD", "Flash Drive", "NAS"],
    "Cooling": ["CPU Cooler", "Case Fan", "Liquid Cooling", "Thermal Paste"],
    "Power Supplies": ["500W PSU", "750W PSU", "1000W PSU", "Modular PSU"]
}

# Generar componentes con categorías relacionadas

"""
Componente  

- Modelo (Texto) 

- Nombre (Texto) 

- Tipo (Texto) 

- Precio (Float) 

- Disponible (Boolean) 

- Especificaciones (Lista) 

- Fecha de lanzamiento (Fechas) 

- Mercado Principal (Texto) 

- Popularidad del producto (Número) 
"""

component_data = []
component_names = [f"Component {i+1}" for i in range(10)]

for i, name in enumerate(component_names):
    # Seleccionar una categoría primero
    main_category = random.choice(list(subcategories.keys()))
    # Seleccionar un tipo dentro de la categoría elegida
    component_type = random.choice(subcategories[main_category])

    component_data.append([
        name,
        f"Model-{random.randint(1000,9999)}",
        component_type,
        round(random.uniform(50, 2000), 2),
        random.choice([True, False]),
        [random.choice(["Feature A", "Feature B", "Feature C", "Feature D"]) for _ in range(3)],
        random_date(start_date, end_date).strftime('%Y-%m-%d'),
        main_category,
        random.randint(1, 100)
    ])

component_df = pd.DataFrame(component_data, columns=[
    "name", "model", "type", "price", "available", "specifications", 
    "release_date", "main_market", "popularity"
])

# Generar categorías

"""
Categoría  

- Nombre (Texto) 

- Popularidad (Número) 

- Activa (Booleano) 

- Destacada (Booleano)  

- Fecha de Actualización (Fechas) 
"""
category_data = []
for main_category in category_groups:
    category_data.append([
        main_category,
        random.randint(1, 100),
        random.choice([True, False]),
        random.choice([True, False]),
        random_date(start_date, end_date).strftime('%Y-%m-%d')
    ])

category_df = pd.DataFrame(category_data, columns=[
    "name", "popularity", "active", "featured", "last_update"
])

# Generar proveedores
"""
Proveedor: 

- Nombre (Texto) 

- Calificación (Número) 

- Garantía Ofrecida (Booleano) 

- Productos Ofrecidos (Listas) 

- Tiempo Promedio de Entrega (Texto) 
"""

provider_data = []
for i in range(10):
    provider_data.append([
        f"Provider {i+1}",
        random.randint(1, 5),
        random.choice([True, False]),
        random.sample(component_names, k=5),
        random.choice(["1-3 days", "3-7 days", "7-14 days"])
    ])

provider_df = pd.DataFrame(provider_data, columns=[
    "name", "rating", "warranty_offered", "products_offered", "avg_delivery_time"
])

# Generar usuarios

"""
Usuario  

- Nombre (Texto) 

- Presupuesto (Float) 

- Buscando Ofertas (Booleano) 

- Marcas Preferidas (Lista) 

- Última Visita (Fechas) 
"""
provider_names = provider_df["name"].tolist()
user_data = []
for i in range(10):
    user_data.append([
        f"User {i+1}",
        round(random.uniform(500, 5000), 2),
        random.choice([True, False]),
        random.sample(provider_names, k=10),
        random_date(start_date, end_date).strftime('%Y-%m-%d')
    ])

user_df = pd.DataFrame(user_data, columns=[
    "name", "budget", "looking_for_offers", "preferred_brands", "last_visit"
])

# Generar reseñas
"""
Reseña: 

- Título (Texto) 

- Valoración (Número) 

- Verificado (Booleano)  

- Recomendación de Compra (Booleano)  

- Fecha de Reseña (Fechas) 
"""
review_data = []
for i in range(10):
    review_data.append([
        f"Review Title {i+1}",
        random.randint(1, 5),
        random.choice([True, False]),
        random.choice([True, False]),
        random_date(start_date, end_date).strftime('%Y-%m-%d')
    ])

review_df = pd.DataFrame(review_data, columns=[
    "title", "rating", "verified", "purchase_recommendation", "review_date"
])


# Guardar los archivos finales
component_df.to_csv(os.path.join(csv_dir, "components.csv"), index=False)
category_df.to_csv(os.path.join(csv_dir, "categories.csv"), index=False)
user_df.to_csv(os.path.join(csv_dir, "users.csv"), index=False)
review_df.to_csv(os.path.join(csv_dir, "reviews.csv"), index=False)
provider_df.to_csv(os.path.join(csv_dir, "providers.csv"), index=False)

# Mostrar los DataFrames para revisión
print("Component Data")
print(component_df.head())
print("\nCategory Data")
print(category_df.head())
print("\nUser Data")
print(user_df.head())
print("\nReview Data")
print(review_df.head())
print("\nProvider Data")
print(provider_df.head())


# Recargar los datos generados anteriormente
component_names = component_df["name"].tolist()
category_names = category_df["name"].tolist()
user_names = user_df["name"].tolist()
provider_names = provider_df["name"].tolist()
review_titles = review_df["title"].tolist()

# Listas para cada tipo de relación
purchase_data = []
categorize_data = []
supply_data = []
review_data = []
promote_data = []
associate_data = []
search_data = []
wishlist_data = []
write_data = []
complement_data = []

# Función para obtener un segundo componente dentro de la misma categoría
def get_related_component(main_component_name, component_df):
    # Obtener la categoría del componente principal
    main_category = component_df.loc[component_df["name"] == main_component_name, "main_market"].values[0]

    # Filtrar componentes que pertenezcan a la misma categoría
    valid_components = component_df[component_df["main_market"] != main_category]

    if len(valid_components) > 1:
        return random.choice(valid_components["name"].tolist())

    return None  # Si no hay otro componente en la misma categoría, retorna None

# Usar diccionario para almacenar conjuntos de relaciones únicas para cada tipo
unique_relations = {
    "purchase": set(),
    "categorize": set(),
    "supply": set(),
    "review": set(),
    "promote": set(),
    "associate": set(),
    "search": set(),
    "wishlist": set(),
    "write": set(),
    "complement": set()
}

# Número deseado de relaciones por tipo y límite de intentos por cada generación
num_relations = 10
attempts_limit = 10

# PURCHASE (Usuario → Componente)
purchase_data = []
generated = 0
while generated < num_relations:
    user_name = random.choice(user_names)
    component_name = random.choice(component_names)
    entry = (user_name, component_name)
    if entry not in unique_relations["purchase"]:
        unique_relations["purchase"].add(entry)
        purchase_data.append([
            user_name,
            component_name,
            random_date(start_date, end_date).strftime('%Y-%m-%d'),
            random.randint(1, 3),
            round(random.uniform(50, 2000), 2),
            random.choice(["Credit Card", "PayPal", "Bank Transfer"])
        ])
        generated += 1
    else:
        # Si ya existe, se intenta nuevamente
        continue

# CATEGORIZE (Componente → Categoría)
categorize_data = []
generated = 0
while generated < num_relations:
    component_name = random.choice(component_names)
    category_name = random.choice(category_names)
    entry = (component_name, category_name)
    if entry not in unique_relations["categorize"]:
        unique_relations["categorize"].add(entry)
        categorize_data.append([
            component_name,
            category_name,
            random_date(start_date, end_date).strftime('%Y-%m-%d'),
            random.randint(1, 10),
            random.randint(1, 50)
        ])
        generated += 1
    else:
        continue

# SUPPLY (Proveedor → Componente)
supply_data = []
generated = 0
while generated < num_relations:
    provider_name = random.choice(provider_names)
    component_name = random.choice(component_names)
    entry = (provider_name, component_name)
    if entry not in unique_relations["supply"]:
        unique_relations["supply"].add(entry)
        supply_data.append([
            provider_name,
            component_name,
            random.choice(["Standard", "Express", "Economy"]),
            random.choice(["Prepaid", "Postpaid"]),
            random.randint(1, 500)
        ])
        generated += 1
    else:
        continue

# REVIEW (Reseña → Componente)
review_rel_data = []
generated = 0
while generated < num_relations:
    review_title = random.choice(review_titles)
    component_name = random.choice(component_names)
    entry = (review_title, component_name)
    if entry not in unique_relations["review"]:
        unique_relations["review"].add(entry)
        review_rel_data.append([
            review_title,
            component_name,
            random.choice(["Online", "In-store"]),
            random.choice(["Good", "Neutral", "Bad"]),
            random.randint(1, 10)
        ])
        generated += 1
    else:
        continue

# PROMOTE (Proveedor → Usuario)
promote_data = []
generated = 0
while generated < num_relations:
    provider_name = random.choice(provider_names)
    user_name = random.choice(user_names)
    entry = (provider_name, user_name)
    if entry not in unique_relations["promote"]:
        unique_relations["promote"].add(entry)
        promote_data.append([
            provider_name,
            user_name,
            round(random.uniform(5, 50), 2),
            random_date(start_date, end_date).strftime('%Y-%m-%d'),
            random.choice(["Seasonal", "Clearance", "Flash Sale"])
        ])
        generated += 1
    else:
        continue

# ASSOCIATE (Proveedor → Categoría) con regeneración si es duplicado
associate_data = []
generated = 0
while generated < num_relations:
    attempts = 0
    while attempts < attempts_limit:
        provider_name = random.choice(provider_names)
        category_name = random.choice(category_names)
        entry = (provider_name, category_name)
        if entry not in unique_relations["associate"]:
            unique_relations["associate"].add(entry)
            associate_data.append([
                provider_name,
                category_name,
                random.randint(1, 11),
                random_date(start_date, end_date).strftime('%Y-%m-%d'),
                random.choice(["Exclusive Distributor", "Limited Partnership", "Official Supplier"])
            ])
            generated += 1
            break  # Salir del loop interno al haber generado la relación
        else:
            attempts += 1
    if attempts == attempts_limit:
        print("⚠️ Se alcanzó el límite de intentos para generar una nueva relación 'associate' sin duplicados.")
        break

# SEARCH (Usuario → Componente)
search_data = []
generated = 0
while generated < num_relations:
    user_name = random.choice(user_names)
    component_name = random.choice(component_names)
    entry = (user_name, component_name)
    if entry not in unique_relations["search"]:
        unique_relations["search"].add(entry)
        search_data.append([
            user_name,
            component_name,
            random.choice(["Gaming", "Budget", "High Performance"]),
            random_date(start_date, end_date).strftime('%Y-%m-%d'),
            random.randint(5, 100)
        ])
        generated += 1
    else:
        continue

# WISHLIST (Usuario → Componente)
wishlist_data = []
generated = 0
while generated < num_relations:
    user_name = random.choice(user_names)
    component_name = random.choice(component_names)
    entry = (user_name, component_name)
    if entry not in unique_relations["wishlist"]:
        unique_relations["wishlist"].add(entry)
        wishlist_data.append([
            user_name,
            component_name,
            random_date(start_date, end_date).strftime('%Y-%m-%d'),
            random.randint(1, 5),
            random.choice(["Upgrade", "Gift", "Replacement"])
        ])
        generated += 1
    else:
        continue

# WRITE (Usuario → Reseña)
write_data = []
generated = 0
while generated < num_relations:
    user_name = random.choice(user_names)
    review_title = random.choice(review_titles)
    entry = (user_name, review_title)
    if entry not in unique_relations["write"]:
        unique_relations["write"].add(entry)
        write_data.append([
            user_name,
            review_title,
            random.randint(1, 100),
            random.choice([True, False]),
            random.choice(["Text Review", "Video Review"])
        ])
        generated += 1
    else:
        continue

# COMPLEMENT (Componente → Componente)
complement_data = []
generated = 0
while generated < num_relations:
    component1 = random.choice(component_names)
    component2 = random.choice([c for c in component_names if c != component1])
    entry = (component1, component2)
    if entry not in unique_relations["complement"]:
        unique_relations["complement"].add(entry)
        complement_data.append([
            component1,
            component2,
            random.randint(1, 10),
            random.choice(["Same Brand", "Compatible Chipset", "Recommended by Users"]),
            random_date(start_date, end_date).strftime('%Y-%m-%d')
        ])
        generated += 1
    else:
        continue

# Crear DataFrames para cada tipo de relación
purchase_df = pd.DataFrame(purchase_data, columns=["user", "component", "purchase_date", "quantity", "total_price", "payment_method"])
categorize_df = pd.DataFrame(categorize_data, columns=["component", "category", "assign_date", "relevance", "position"])
supply_df = pd.DataFrame(supply_data, columns=["provider", "component", "shipping_mode", "payment_terms", "stock"])
review_df_rel = pd.DataFrame(review_rel_data, columns=["review", "component", "purchase_location", "satisfaction", "detail_level"])
promote_df = pd.DataFrame(promote_data, columns=["provider", "user", "discount_percentage", "promotion_date", "promotion_type"])
associate_df = pd.DataFrame(associate_data, columns=["provider", "category", "association_level", "start_date", "association_terms"])
search_df = pd.DataFrame(search_data, columns=["user", "component", "keyword", "search_date", "results_count"])
wishlist_df = pd.DataFrame(wishlist_data, columns=["user", "component", "added_date", "priority", "reason"])
write_df = pd.DataFrame(write_data, columns=["user", "review", "trust_index", "verified_purchase", "review_type"])
complement_df = pd.DataFrame(complement_data, columns=["component1", "component2", "compatibility_level", "compatibility_reason", "relation_date"])

# Guardar cada relación en un archivo CSV separado
purchase_df.to_csv(os.path.join(csv_dir, "relations_purchase.csv"), index=False)
categorize_df.to_csv(os.path.join(csv_dir, "relations_categorize.csv"), index=False)
supply_df.to_csv(os.path.join(csv_dir, "relations_supply.csv"), index=False)
review_df_rel.to_csv(os.path.join(csv_dir, "relations_review.csv"), index=False)
promote_df.to_csv(os.path.join(csv_dir, "relations_promote.csv"), index=False)
associate_df.to_csv(os.path.join(csv_dir, "relations_associate.csv"), index=False)
search_df.to_csv(os.path.join(csv_dir, "relations_search.csv"), index=False)
wishlist_df.to_csv(os.path.join(csv_dir, "relations_wishlist.csv"), index=False)
write_df.to_csv(os.path.join(csv_dir, "relations_write.csv"), index=False)
complement_df.to_csv(os.path.join(csv_dir, "relations_complement.csv"), index=False)

# Mostrar los DataFrames generados para revisión de relaciones
print("\nPurchase Data")
print(purchase_df.head())
print("\nCategorize Data")
print(categorize_df.head())
print("\nSupply Data")
print(supply_df.head())
print("\nReview Data")
print(review_df_rel.head())
print("\nPromote Data")
print(promote_df.head())
print("\nAssociate Data")
print(associate_df.head())
print("\nSearch Data")
print(search_df.head())
print("\nWishlist Data")
print(wishlist_df.head())
print("\nWrite Data")
print(write_df.head())
print("\nComplement Data")
print(complement_df.head())