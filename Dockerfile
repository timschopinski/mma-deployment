FROM prestashop/prestashop:1.7.8

RUN apt-get update && \
    apt-get install -y \
        memcached \
        libmemcached-dev \
        libmemcached11 \
        libmemcachedutil2 \
        systemctl

RUN pecl install memcached && \
    docker-php-ext-enable memcached

CMD ["bash", "-c", "service memcached start && apache2-foreground"]

RUN rm -rf /var/www/html/*

COPY ./psdata /var/www/html

RUN chmod -R 777 /var/www/html
