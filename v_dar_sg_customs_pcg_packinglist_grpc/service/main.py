# -*- coding: utf-8 -*-

from v_py3_idl.helloworld.pingpong import pingpong_service_pb2 as pb
from v_py3_idl.helloworld.pingpong import pingpong_service_pb2_grpc as rpc


class PingPongServiceService(rpc.PingPongServiceServicer):
    def __init__(self):
        pass

    def Ping(self, request, context):
        print("Got request: [{}]".format(request))
        return pb.PingRequest(ping="Ping")