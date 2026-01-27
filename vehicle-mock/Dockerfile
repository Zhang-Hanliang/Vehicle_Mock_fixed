# Copyright (c) 2022-2025 Contributors to the Eclipse Foundation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

# syntax=docker/dockerfile:1.2

# Build stage, to create the executable
FROM --platform=$TARGETPLATFORM ghcr.io/eclipse-velocitas/devcontainer-base-images/python:v0.4 AS builder
ARG TARGETARCH

RUN apt-get update && apt-get install -y python3-dev

# COPY ./.velocitas.json /workspace/.velocitas.json
COPY ./app /workspace/app
# COPY specs/spec.json /workspace/specs/spec.json

# Remove this installation for Arm64 once staticx has a prebuilt wheel for Arm64
RUN /bin/bash -c 'set -ex && \
    ARCH=`uname -m` && \
    if [ "$ARCH" == "aarch64" ]; then \
    echo "ARM64" && \
    apt-get install -y gcc && \
    pip3 install --no-cache-dir scons; \
    fi'

RUN pip3 install --no-cache-dir pyinstaller==6.8.0 \
    && pip3 install --no-cache-dir patchelf==0.17.0.0 \
    && pip3 install --no-cache-dir --no-build-isolation staticx \
    && pip3 install --no-cache-dir -r ./workspace/app/requirements.in

# WORKDIR /workspace

# RUN velocitas init

WORKDIR /workspace/app


RUN pyinstaller --clean -F -s --paths=src \
    --hidden-import jaraco \
    --hidden-import jaraco.text \
    --hidden-import jaraco.functools \
    --hidden-import jaraco.context \
    --hidden-import jaraco.classes \
    --hidden-import jaraco.collections \
    --hidden-import jaraco.itertools \
    --hidden-import jaraco.stream \
    --hidden-import jaraco.vcs \
    mockprovider.py

WORKDIR /workspace/app/dist

COPY ./app/mockprovider.py /dist/
RUN staticx mockprovider run-exe

# Runner stage, to copy the executable
FROM scratch AS runner

COPY --from=builder ./workspace/app/dist/run-exe /dist/

#COPY --from=builder ./workspace/app/certs /dist/certs
#COPY --from=builder ./workspace/app/certs /mnt/certs
# COPY --from=builder ./workspace/app/env_var.json /mnt/env_var.json
# COPY --from=builder ./workspace/app/dist/run-exe /dist/

WORKDIR /tmp
WORKDIR /dist

ENV PATH="/dist:$PATH"

LABEL org.opencontainers.image.source="https://github.com/eclipse-velocitas/vehicle-app-python-template"

CMD ["./run-exe"]

