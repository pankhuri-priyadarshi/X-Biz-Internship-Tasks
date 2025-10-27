FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/html

COPY index.html /var/www/html/index.html

EXPOSE 80

ENTRYPOINT [ "nginx" ]
CMD [ "-g","daemon off;" ]

#ENTRYPOINT [ "nginx","-g","daemon off;" ]
#CMD ["nginx","-g","daemon off;"]

