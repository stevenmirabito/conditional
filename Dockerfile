#######################################
# Production Container for Conditional
#######################################

FROM python:3-alpine
MAINTAINER Computer Science House (evals@csh.rit.edu)

# Specify that we expose port 8080
EXPOSE 8080

# Add the app user
RUN adduser -S conditional

# Install additional system packages required for some Python dependencies,
# then configure OpenLDAP to use the system trusted CA store
RUN apk upgrade --no-cache && \
apk add --no-cache postgresql-dev libffi-dev python-dev gcc musl-dev openssl-dev openldap-dev ca-certificates && \
update-ca-certificates && \
echo "tls_cacertdir /etc/ssl/certs" >> /etc/openldap/ldap.conf

# Install the application
RUN pip install --no-cache-dir -i https://repo.csh.rit.edu/repository/pypi conditional${CONDITIONAL_VERSION:+"=="}${CONDITIONAL_VERSION}

# Drop privileges
USER conditional

# Run application with gunicorn
CMD gunicorn --workers=4 --bind ${CONDITIONAL_SERVER_IP:-0.0.0.0}:${CONDITIONAL_SERVER_PORT:-8080} app
