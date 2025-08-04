FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

COPY ssl/cert.pem  /etc/nginx/ssl/cert.pem
COPY ssl/key.pem   /etc/nginx/ssl/key.pem

COPY frontend/static /usr/share/nginx/html

EXPOSE 80 443
