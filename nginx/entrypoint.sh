#!/bin/sh
sed -i "s|__NGINX_VIDEO_SECRET__|${NGINX_VIDEO_SECRET}|g" /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
