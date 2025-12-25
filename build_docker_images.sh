#!/bin/bash

# Build Python Image
echo "Building compilemate-python..."
docker build -t compilemate-python ./docker/python

# Build C++ Image
echo "Building compilemate-cpp..."
docker build -t compilemate-cpp ./docker/cpp

# Build Java Image
echo "Building compilemate-java..."
docker build -t compilemate-java ./docker/java

# Build JavaScript Image
echo "Building compilemate-js..."
docker build -t compilemate-js ./docker/javascript

echo "✅ All Docker images built successfully!"
