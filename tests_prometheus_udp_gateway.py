import pytest
import mock

import json

from prometheus_udp_gateway import (
    ReceiveMetricProtocol, UDPRegistry, Counter
)


@pytest.fixture()
def udp_registry():
    return UDPRegistry(host='invalid', port=0000)


@pytest.fixture()
def counter(udp_registry):
    counter = Counter('test_counter', 'Test', registry=udp_registry)
    counter._gateway_client.send = mock.MagicMock()
    return counter


def test_udp_counter_inc(counter):
    counter.inc()
    counter._gateway_client.send.assert_called_with(
        data={
            'name': 'test_counter',
            'method': 'inc',
            'value': 1
    })


def test_udp_counter_inc_value(counter):
    counter.inc(2)
    counter._gateway_client.send.assert_called_with(
        data={
            'name': 'test_counter',
            'method': 'inc',
            'value': 2
    })


@pytest.fixture()
def receive_metric_protocol():
    receive_metric_protocol = ReceiveMetricProtocol(
        log=mock.Mock(),
        metrics={
            'test_counter': mock.Mock(),
        }
    )
    return receive_metric_protocol


def test_receive_incorrect_format(receive_metric_protocol):
    receive_metric_protocol.datagramReceived(b'{test', ('invalid_host', 0000))
    receive_metric_protocol._log.error.assert_called()


def test_receive_incorrect_json(receive_metric_protocol):
    receive_metric_protocol.datagramReceived(b'{"t": "est"}', ('invalid_host', 0000))
    receive_metric_protocol._log.error.assert_called()


def test_receive_incorrect_method(receive_metric_protocol):
    receive_metric_protocol.datagramReceived(
        json.dumps({'name': 'test_counter', 'method': 'incorrect', 'value': 1}),
        ('invalid_host', 000)
    )
    receive_metric_protocol._log.error.assert_called()


def test_receive_counter_inc(receive_metric_protocol):
    receive_metric_protocol.datagramReceived(
        json.dumps({'name': 'test_counter', 'method': 'inc', 'value': 1}),
        ('invalid_host', 0000)
    )
    receive_metric_protocol._metrics['test_counter'].inc.assert_called_with(1)


def test_receive_counter_inc_value(receive_metric_protocol):
    receive_metric_protocol.datagramReceived(
        json.dumps({'name': 'test_counter', 'method': 'inc', 'value': 5}),
        ('invalid_host', 0000)
    )
    receive_metric_protocol._metrics['test_counter'].inc.assert_called_with(5)
