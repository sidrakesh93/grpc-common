#!/bin/bash

# Runs the protoc with gRPC plugin to generate protocol messages and gRPC stubs.
protoc -I ../../protos --python_out=. ../../protos/qpstest.proto
protoc -I ../../protos --python_out=. --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_python_plugin` ../../protos/user_data.proto