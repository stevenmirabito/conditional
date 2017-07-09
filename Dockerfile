#######################################
# Production Container for Conditional
#######################################

FROM python:3-alpine3.6
MAINTAINER Computer Science House (evals@csh.rit.edu)

# Expose the application port
EXPOSE 8080

# Add the app user
RUN adduser -S conditional

# Install some additional packages required for dependencies,
# then configure OpenLDAP to use the system trusted CA store
RUN apk add --no-cache \
        ca-certificates \
        gcc \
        libffi-dev \
        libressl-dev \
        musl-dev \
        openldap-dev \
        postgresql-client \
        postgresql-dev \
    && update-ca-certificates \
    && echo "tls_cacertdir /etc/ssl/certs" >> /etc/openldap/ldap.conf

# Install the application
RUN pip install --no-cache-dir -i https://repo.csh.rit.edu/repository/pypi conditional${CONDITIONAL_VERSION:+"=="}${CONDITIONAL_VERSION}

# Add wait-for-postgres
ADD tools/wait-for-postgres.sh /
RUN chmod 755 /wait-for-postgres.sh

# Drop privileges
USER conditional

# Run application with gunicorn
CMD ["/wait-for-postgres.sh", \
     "gunicorn", "--workers=4", "--bind", \
     "${CONDITIONAL_SERVER_IP:-0.0.0.0}:${CONDITIONAL_SERVER_PORT:-8080}", \
     "conditional"]