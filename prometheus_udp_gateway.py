# coding=utf8

import json
import sys
import socket

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.logger import Logger, textFileLogObserver, FilteringLogObserver, LogLevel, LogLevelFilterPredicate
import prometheus_client
from prometheus_client.twisted import MetricsResource
import jsonschema

# TODO: change to prometheus_client.METRIC_TYPES
METRIC_TYPES = ['counter', 'gauge', 'histogram']

# TODO
METRIC_METHODS = ['inc', 'dec', 'set', 'observe']


METRIC_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['name', 'method', 'value'],
    'properties': {
        'name': {'type': 'string'},
        'method': {
            'type': 'string',
            'enum': METRIC_METHODS
        },
        'value': {'type': 'number'},
    },
}


class UDPGatewayClient(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        # TODO: catch errors
        json_data = json.dumps(data)
        self._sock.sendto(json_data, (self._host, self._port))


class UDPRegistry(prometheus_client.CollectorRegistry):
    def __init__(self, auto_describe=False, host='127.0.0.1', port=8888):
        super(UDPRegistry, self).__init__(auto_describe)
        self.udp_host = host
        self.udp_port = port
        self._names_to_metrics = {}
        self._metrics_to_names = {}

    def register(self, collector):
        super(UDPRegistry, self).register(collector)
        self._names_to_metrics[collector._name] = collector
        self._metrics_to_names[collector] = collector._name

    def unregister(self, collector):
        super(UDPRegistry, self).unregister(collector)
        metric_name = self._metrics_to_names[collector]
        del self._names_to_metrics[metric_name]
        del self._metrics_to_names[collector]

    def get_names_to_metrics(self):
        return self._names_to_metrics

    def get_normal_metrics(self):
        metrics = {}
        for name, metric in self._names_to_metrics.items():
            metrics[name] = metric.get_metric_instance()
        return metrics

    def collect(self):
        # TODO: raise exception
        pass

    def restricted_registry(self, names):
        # TODO: raise exception
        pass

    def get_sample_value(self, name, labels=None):
        # TODO: raise exception
        pass


class UDPMetricMixin(object):
    """
    TODO
    """

    metric_class = None

    def __init__(
            self,
            name,
            documentation,
            labelnames=(),
            namespace='',
            subsystem='',
            unit='',
            # TODO: registry=None?
            registry=None,
            labelvalues=None,
    ):
        super(UDPMetricMixin, self).__init__(
            name, documentation, labelnames, namespace, subsystem, unit, registry, labelvalues
        )
        self._name = name
        self._gateway_client = UDPGatewayClient(registry.udp_host, registry.udp_port)

        self._kwargs = {
            'name': name,
            'documentation': documentation,
            'labelnames': labelnames,
            'namespace': namespace,
            'unit': unit,
            # TODO: registry?
            'registry': prometheus_client.REGISTRY,
            'labelvalues': labelvalues
        }

    def _send_to_gateway(self, method, value):
        self._gateway_client.send(
            data={'name': self._name, 'method': method, 'value': value},
        )

    def get_metric_instance(self):
        return self.metric_class(**self._kwargs)


class Counter(UDPMetricMixin, prometheus_client.Counter):
    metric_class = prometheus_client.Counter

    def inc(self, amount=1):
        super(Counter, self).inc(amount)
        # TODO: add decorator for method name
        self._send_to_gateway('inc', amount)


class Gauge(UDPMetricMixin, prometheus_client.Gauge):
    metric_class = prometheus_client.Gauge

    def inc(self, amount=1):
        super(Counter, self).inc(amount)
        self._send_to_gateway('inc', amount)

    def dec(self, amount=1):
        super(Gauge, self).dec(amount)
        self._send_to_gateway('dec', amount)

    def set(self, value):
        super(Gauge, self).set(value)
        self._send_to_gateway('set', float(value))


class Summary(UDPMetricMixin, prometheus_client.Summary):
    metric_class = prometheus_client.Summary

    def observe(self, amount):
        super(Summary, self).observe(amount)
        self._send_to_gateway('observe', amount)


class ReceiveMetricProtocol(DatagramProtocol):
    """
    TODO
    """
    def __init__(self, log, metrics):
        self._log = log
        self._metrics = metrics
        self._log.info('Receive Metric Protocol init')

    def _get_metric(self, name):
        # TODO: catch errors
        return self._metrics[name]

    def _update_metric(self, metric_name, method, value):
        metric = self._get_metric(metric_name)
        method = getattr(metric, method)
        method(value)

    def datagramReceived(self, datagram, (host, port)):
        self._log.info('Datagram received')
        try:
            data = json.loads(datagram)
        except ValueError:
            self._log.error(
                u'Received incorrect data from ({host}:{port}): {data}',
                host=host,
                port=port,
                data=datagram
            )
            return
        try:
            jsonschema.validate(instance=data, schema=METRIC_SCHEMA)
        except jsonschema.ValidationError as validation_error:
            # TODO: add error counter
            self._log.error(
                'Received incorrect data format from ({host}:{port}): {data}',
                host=host,
                port=port,
                data=datagram
            )
            self._log.error('{error}', error=str(validation_error))
            return

        # TODO: metric validation (prometheus_client.METRIC_TYPES)

        self._update_metric(
            metric_name=data['name'], method=data['method'], value=data['value']
        )


class PrometheusUdpGateway:
    """
    TODO
    """

    # TODO: find application entity in Twisted

    def __init__(self, udp_registry, prometheus_port=8000, gateway_port=8888, log_level='INFO'):
        # TODO: add available log levels

        # TODO: change name to collector?
        self._metrics = udp_registry.get_normal_metrics()

        self._prometheus_port = prometheus_port
        self._gateway_port = gateway_port

        self._log_level = log_level

        level_predicate = LogLevelFilterPredicate(LogLevel.lookupByName(self._log_level.lower()))
        log_observer = FilteringLogObserver(textFileLogObserver(sys.stdout), predicates=[level_predicate])
        self.log = Logger(observer=log_observer)

    def run(self):
        """
        TODO
        """
        root = Resource()
        # TODO: add error counter
        root.putChild(b'metrics', MetricsResource())
        factory = Site(root)
        reactor.listenTCP(self._prometheus_port, factory, interface='0.0.0.0')
        self.log.info('Start listen Prometheus (port: {prometheus_port})', prometheus_port=self._prometheus_port)

        reactor.listenUDP(
            self._gateway_port,
            ReceiveMetricProtocol(log=self.log, metrics=self._metrics)
        )
        self.log.info(
            'Start listen udp gateway (port: {gateway_port})',
            gateway_port=self._gateway_port
        )
        reactor.run()
