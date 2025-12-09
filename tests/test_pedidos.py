from services.pedido_service import PedidoService
from services.corte_service import CorteService
from models.producto import Producto, Categoria, Tamano
from models.usuario import Usuario, Rol


def test_flujo_pedido_reparto_y_corte(db_session):
    rol = Rol(nombre="cajero")
    usuario = Usuario(username="cash", nombre="Caja", pass_hash="x", rol=rol)
    cat = Categoria(nombre="Especiales")
    tam = Tamano(nombre="Familiar", factor_precio=2)
    producto = Producto(nombre="Hawaiana", categoria=cat, tamano=tam, precio_base=120, es_pizza=True)
    db_session.add_all([rol, usuario, cat, tam, producto])
    db_session.commit()

    pedidos = PedidoService(db_session)
    pedido = pedidos.nuevo(usuario.id, canal="DOMICILIO", cliente_id=None, envio=20, propina=10)
    pedidos.agregar_item(pedido.id, producto.id, cantidad=1, tamano_id=tam.id)
    pedidos.calcular_totales(pedido.id)
    reparto = pedidos.asignar_reparto(pedido.id, repartidor="Luis")
    pedidos.marcar_entregado(reparto.id)
    pago, cambio = pedidos.registrar_pago(pedido.id, monto_recibido=200, metodo="EFECTIVO", usuario_id=usuario.id)

    assert float(pedido.total) > 0
    assert cambio >= 0
    assert reparto.estado == "ENTREGADO"
    assert pago.metodo == "EFECTIVO"

    corte_service = CorteService(db_session)
    corte = corte_service.abrir_caja(usuario.id)
    cierre = corte_service.cerrar_caja(corte.id, usuario.id)
    assert float(cierre.total_efectivo) > 0
