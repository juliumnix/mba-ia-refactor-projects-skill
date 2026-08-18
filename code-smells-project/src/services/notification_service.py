import logging

logger = logging.getLogger(__name__)


def notify_pedido_criado(pedido_id, usuario_id):
    logger.info("pedido_created pedido_id=%s usuario_id=%s", pedido_id, usuario_id)


def notify_status_atualizado(pedido_id, novo_status):
    logger.info("pedido_status_updated pedido_id=%s status=%s", pedido_id, novo_status)
