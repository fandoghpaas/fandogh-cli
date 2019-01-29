x = {
    "manifest": {
        "kind": {
            "document": "You should define description"
        },
        "name": {
            "document": "You should define description"
        },
        "internal": {
            "spec": {
                "port": {
                    "document": "port structure should be like this:\n\n"
                                "kind: SERVICE_KIND\n"
                                "name: SERVICE_NAME\n"
                                "spec:\n"
                                "  ...\n"
                                "  port: integer_port_number\n"
                                "for more info visit manifest in: "
                                "https://docs.fandogh.cloud/docs/service-manifest.html\n\n "
                }, "allow_http": {
                    "document": "allow_http helps you to expose your service\n"
                                "on non-ssl protocol http\n"
                                "kind: SERVICE_TYPE\n"
                                "name: SERVICE_NAME\n"
                                "spec:\n"
                                "  ...\n"
                                "  allow_http: [false, true, default=true]\n"
                                "for more info visit manifest in: "
                                "https://docs.fandogh.cloud/docs/service-manifest.html\n\n "
                }, "path": {
                    "document": "\"path\" helps you to response to requests on a\n"
                                "specific path\n"
                                "kind: SERVICE_TYPE\n"
                                "name: SERVICE_NAME\n"
                                "spec:\n"
                                "  ...\n"
                                "  path: PATH_FROM_ROOT\n"
                                "for more info visit manifest in: "
                                "https://docs.fandogh.cloud/docs/service-manifest.html\n\n "
                }
            }
        },
        "external": {
            "spec": {
                "document": "You should define description",
                "domains": {
                    "document": "domains spec is list of domains that you want to add\n"
                                "to your service, below is the sample:\n"
                                "kind: SERVICE_KIND\n"
                                "name:SERVICE_NAME\n"
                                "spec\n"
                                "  ...\n"
                                "  domains:\n"
                                "   - name: DOMAIN_NAME_ONE\n"
                                "   - name: DOMAIN_NAME_TWO\n"
                }
            }
        },
        "managed": {
            "spec": {}
        }
    }
}
