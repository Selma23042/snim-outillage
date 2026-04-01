FROM odoo:19.0

USER root

COPY ./snim_outillage /mnt/extra-addons/snim_outillage

COPY ./config/odoo.conf /etc/odoo/odoo.conf

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

USER odoo

EXPOSE 8069
