import argparse
import prometheus_udp_gateway
import metrics

# TODO: entrypoint in setup.py

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prometheus UDP Gateway'
    )

    parser.add_argument('-p', '--prometheus_port', required=True, type=int)
    parser.add_argument('-g', '--udp_gateway_port', required=True, type=int)
    parser.add_argument('-l', '--log_level', required=False, type=str, default='INFO')

    args = parser.parse_args()

    gateway = prometheus_udp_gateway.PrometheusUdpGateway(
        # TODO: remove udp_registry, add metrics ad-hoc
        udp_registry=metrics.udp_registry,
        prometheus_port=args.prometheus_port,
        gateway_port=args.udp_gateway_port,
        log_level=args.log_level,
    )

    gateway.run()
