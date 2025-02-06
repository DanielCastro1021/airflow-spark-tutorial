FROM quay.io/astronomer/astro-runtime:12.6.0

USER root
RUN apt-get update && apt-get install -y default-jdk