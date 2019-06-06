# -*- coding: utf-8 -*-
from vconf import Config
import logging

from concurrent import futures
import time
import grpc

from v_py3_idl.helloworld.pingpong import pingpong_service_pb2 as pb
from v_py3_idl.helloworld.pingpong import pingpong_service_pb2_grpc as rpc
from .service.main import PingPongServiceService
import sys
from vconf import Config
from . import about
from . import config
from v_grpc_interceptor.server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

_WAIT_START_DURATION = 10


def serve(ip, gport, hport=None):
    logging.info("start server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=[PromServerInterceptor()])
    rpc.add_PingPongServiceServicer_to_server(PingPongServiceService(), server)
    server.add_insecure_port("{}:{}".format(ip, gport))
    server.start()
    if hport:
        start_http_server(hport)
    try:
        while True:
            time.sleep(_WAIT_START_DURATION)
    except KeyboardInterrupt:
        server.stop(0)
    logging.info("close server")


def run():
    env = "local"
    ip = '127.0.0.1'
    port = '30001'
    hport = None

    if len(sys.argv) > 1:
        env = sys.argv[1]

    if len(sys.argv) > 2:
        ip = sys.argv[2]

    if len(sys.argv) > 3:
        port = sys.argv[3]

    if len(sys.argv) > 4:
        hport = int(sys.argv[4])

    logging.info("Loading Config ...")
    profile = Config(domain=about.domain, app=about.appname, env=env).getConf()

    print("foo.bar={}".format(config.get_foo_bar(profile)))
    print("Start {}, ip={}, grpc port={}, metrics port = {}".format(
        about.appname, ip, port, hport))

    serve(ip, port, hport)
    return 0


if __name__ == "__main__":
    sys.exit(run())