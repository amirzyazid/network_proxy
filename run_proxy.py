from network_proxy import NetworkProxy

config = {
    'HOST_NAME': 'localhost',
    'BIND_PORT': 8080,
    'MAX_REQUEST_LEN': 1024,
    'CONNECTION_TIMEOUT': 5
}

proxy = NetworkProxy(config)