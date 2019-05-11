from fandogh_cli.fandogh_client import base_url, get_exception, get_session

base_domains_url = '%sdomains' % base_url


def add_domain(name):
    request = {
        'name': name
    }
    response = get_session().post(base_domains_url,
                                  json=request)
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def list_domains():
    response = get_session().get(base_domains_url)
    if response.status_code != 200:
        raise get_exception(response)
    else:
        result = []
        for domain in response.json():
            cert = domain.get('certificate', None)
            domain['certificate_status'] = " - "
            if cert is None:
                domain['certificate'] = "No Certificate"
            else:
                domain['certificate'] = "Requested"
                domain['certificate_status'] = (cert.get("details", {}) or {}).get('status', ' - ')
            result.append(domain)
        return result


def verify_domain(name):
    response = get_session().post(base_domains_url + '/' + name + '/verifications')
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def details_domain(name):
    response = get_session().get(base_domains_url + '/' + name)
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def create_certificate(name):
    response = get_session().post(base_domains_url + '/' + name + '/certificate')
    if response.status_code != 201:
        raise get_exception(response)
    else:
        return response.json()


def delete_certificate(name):
    response = get_session().delete(base_domains_url + '/' + name + '/certificate')
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def delete_domain(domain_name):
    response = get_session().delete(base_domains_url + '/{}'.format(domain_name))
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
