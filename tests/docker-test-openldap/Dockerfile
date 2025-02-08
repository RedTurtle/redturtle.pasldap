# FROM debian:bookworm-slim
FROM debian:buster-slim

# Configuration Env Variables with defaults
ENV DATA_DIR="/opt/openldap/bootstrap/data"
ENV CONFIG_DIR="/opt/openldap/bootstrap/config"
ENV LDAP_DOMAIN=planetexpress.com
ENV LDAP_ORGANISATION="Planet Express, Inc."
ENV LDAP_BINDDN="cn=admin,dc=planetexpress,dc=com"
ENV LDAP_SECRET=GoodNewsEveryone
ENV LDAP_CA_CERT="/etc/ldap/ssl/fullchain.crt"
ENV LDAP_SSL_KEY="/etc/ldap/ssl/ldap.key"
ENV LDAP_SSL_CERT="/etc/ldap/ssl/ldap.crt"
ENV LDAP_FORCE_STARTTLS="false"

# Install slapd and requirements
RUN apt-get update \
	&& apt-get dist-upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get \
        install -y --no-install-recommends \
            xz-utils \
            slapd \
            ldap-utils \
            openssl \
            ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /etc/ldap/ssl /bootstrap

# Add s6-overlay
# ARG S6_OVERLAY_VERSION=3.2.0.2
# ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
# RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
# ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
# RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer /tmp/
RUN chmod +x /tmp/s6-overlay-amd64-installer && /tmp/s6-overlay-amd64-installer /

# ADD rootfs files
ADD ./rootfs /

VOLUME ["/etc/ldap/slapd.d", "/etc/ldap/ssl", "/var/lib/ldap", "/run/slapd"]

EXPOSE 10389 10636

CMD ["/init"]

HEALTHCHECK CMD ["ldapsearch", "-H", "ldap://127.0.0.1:10389", "-D", "${LDAP_BINDDN}", "-w", "${LDAP_SECRET}", "-b", "${LDAP_BINDDN}"]
