###############################
# Dockerfile for Conditional
###############################

FROM python:3-alpine
MAINTAINER Computer Science House

# Specify that we expose port 8080
EXPOSE 8080

# Add the app user
RUN adduser -S conditional

# Create the directory for the app and drop privileges
RUN mkdir -p /opt/conditional

# Copy files into the container
ADD . /opt/conditional
RUN chown -R conditional /opt/conditional
WORKDIR /opt/conditional

# Install additional system packages required for some Python dependencies
RUN apk upgrade --no-cache && \
apk add --no-cache postgresql-dev libffi-dev python-dev gcc musl-dev openssl-dev openldap-dev ca-certificates && \
update-ca-certificates

# Configure OpenLDAP to use the system trusted CA store
RUN echo "tls_cacertdir /etc/ssl/certs" >> /etc/openldap/ldap.conf

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Drop privileges
USER conditional

# Run application with gunicorn
CMD gunicorn --workers=4 --bind ${CONDITIONAL_SERVER_IP:-0.0.0.0}:${CONDITIONAL_SERVER_PORT:-8080} app

