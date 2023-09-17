import logging

from quart import Quart
from quart_schema import QuartSchema

from .config import Config
from .extensions.rabbitmq import ChannelPool
from .healthcheck.views import health
from .order.views import order


def create_app():
    app = Quart(__name__)
    QuartSchema(app, info={"title": Config.API_TITLE, "version": Config.API_VERSION})

    app.config.from_object(Config)

    log_level = logging.DEBUG if app.config["DEBUG"] else logging.WARNING
    app.logger.setLevel(log_level)

    app.register_blueprint(order)
    app.register_blueprint(health)

    @app.before_serving
    async def setup_channel_pool():
        app.channel_pool = ChannelPool()  # type: ignore
        await app.channel_pool.initialize(Config.RABBITMQ_URL)  # type: ignore

    return app


app = create_app()
