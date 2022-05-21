from distutils.core import setup

setup(
    name='inuits_otel_tracer',
    version='0.0.8',
    description="Otel tracer help for tracing in python applications.",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    author='Yasinthan',
    author_email='yasinthan@inuits.eu',
    license='GPLv2',
    packages=[
        'inuits_otel_tracer'
    ],
    install_requires=[
        "opentelemetry-api==1.9.1",
        "opentelemetry-sdk==1.9.1",
        "opentelemetry-exporter-otlp==1.9.1",
        "opentelemetry-instrumentation-flask==0.28b1",
        "opentelemetry-instrumentation-requests==0.28b1"
    ],
    provides=['inuits_otel_tracer']
)
