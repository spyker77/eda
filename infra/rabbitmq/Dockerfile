FROM rabbitmq:3.12.4-management

COPY rabbitmq.conf definitions.json /etc/rabbitmq/

RUN rabbitmq-plugins enable --offline rabbitmq_prometheus
