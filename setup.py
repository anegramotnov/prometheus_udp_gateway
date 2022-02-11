from setuptools import setup

setup(
    name="prometheus_udp_gateway",
    version="0.0.1",
    author="Alexey Negramotnov",
    author_email="anegramotnov@gmail.com",
    description="Python Prometheus UDP Gateway and Client",
    license="WTFPL",
    keywords="prometheus monitoring instrumentation client udp gateway",
    py_modules=[
        'prometheus_udp_gateway',
    ],
    install_requires=[
        'prometheus-client==0.7.1',
        'Twisted==22.1.0',
        'jsonschema==3.0.2'
    ],
)