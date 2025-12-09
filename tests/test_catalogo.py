## tests/test_catalogo.py
# Prueba los modelos de catálogo asegurando relaciones entre productos e ingredientes.
from models.producto import Categoria, Tamano, Producto, Ingrediente, ProductoIngrediente


def test_catalogo_pizza(db_session):
    cat = Categoria(nombre="Pizzas")
    chico = Tamano(nombre="Chica", factor_precio=1)
    grande = Tamano(nombre="Grande", factor_precio=1.5)
    queso = Ingrediente(nombre="Queso", costo_unitario=10)
    pizza = Producto(nombre="Margarita", categoria=cat, tamano=chico, precio_base=100, es_pizza=True)
    pizza.ingredientes.append(ProductoIngrediente(ingrediente=queso, cantidad=2))

    db_session.add_all([cat, chico, grande, queso, pizza])
    db_session.commit()

    stored = db_session.query(Producto).filter_by(nombre="Margarita").first()
    assert stored.categoria.nombre == "Pizzas"
    assert stored.tamano.nombre == "Chica"
    assert stored.ingredientes[0].ingrediente.nombre == "Queso"
