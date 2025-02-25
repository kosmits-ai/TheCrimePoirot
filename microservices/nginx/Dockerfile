FROM nginx:latest

# Copy the NGINX configuration template
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Install envsubst to allow variable substitution
RUN apt-get update && apt-get install -y gettext-base

# Replace the variables and start nginx in one command
CMD envsubst '${API_GATEWAY_IP} ${API_GATEWAY_IP_2} ${UPDATE_DB_IP} ${CLAUDE_IP}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'
