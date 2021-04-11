FROM node:13.8

ARG DOCKER_USER_ID

RUN groupadd picture
RUN useradd --create-home -r -o --uid ${DOCKER_USER_ID} -g picture picture

WORKDIR /usr/app

RUN chown -R picture:picture /usr/app

USER picture

VOLUME /usr/app

CMD ["bash"]
