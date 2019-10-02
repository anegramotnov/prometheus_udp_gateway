import prometheus_udp_gateway

udp_registry = prometheus_udp_gateway.UDPRegistry(host='127.0.0.1', port=8888)

example_counter = prometheus_udp_gateway.Counter(
    'example_counter', 'Example Counter', registry=udp_registry)
