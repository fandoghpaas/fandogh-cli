from .django import wsgi_name_hint, requirements_hint, build_manifest as django_build_manifest

key_hints = {
    'wsgi': wsgi_name_hint,
    'django': requirements_hint
}

manifest_builders = {
    'django': django_build_manifest
}
