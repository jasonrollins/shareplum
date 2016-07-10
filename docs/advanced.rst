========
Advanced
========

SSL Version
===========

Some Linux distributions using OpenSSL 1.0f or older can not use the TLS1.2 protocal as outlined `here <https://rt.openssl.org/Ticket/Display.html?user=guest&pass=guest&id=2771>`_.  You can change the SSL/TLS protocol version by passing in the ssl_version parameter for Site like so: ::

    site = Site(SITE, auth=auth, verify_ssl=True, ssl_version='TLSv1')
