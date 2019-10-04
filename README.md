[![Build Status](https://travis-ci.org/anegramotnov/prometheus_udp_gateway.svg?branch=master)](https://travis-ci.org/anegramotnov/prometheus_udp_gateway)

# WIP: Prometheus UDP Gateway

Prometheus-шлюз для агрегации метрик по UDP и клиентская библиотека для отправки
в него по UDP метрик, копирующая API
[prometheus_client](https://github.com/prometheus/client_python).

В отличие от [Pushgateway](https://github.com/prometheus/pushgateway):
* Написан на Python
* Работает по UDP

**Находится в процессе разработки**

## Зависимости

* Python 2.7+
* prometheus-client==0.7.1
* Twisted==19.7.0
* jsonschema==3.0.2

## Установка пакета

```
python setup.py install
```

## Использование

[Пример](/examples)

## Тесты

```
python setup.py develop
pytest tests_prometheus_udp_gateway.py
```
