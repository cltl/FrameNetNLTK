

SUPPORTED_LANGUAGES = {
    'en',
    'nl'
}


def generate_nt_file(your_fn,
                     namespace,
                     language,
                     major_version,
                     minor_version):
    """

    :param your_fn:
    :param namespace:
    :param language:
    :param major_version:
    :param minor_version:
    :return:
    """

    for lu in your_fn.lus():

        # retrieve premon uri

        # TODO: generate lu rdf uri
        pass


def generate_lexicon_rdf_uri(namespace,
                             language,
                             major_version,
                             minor_version):
    error_message = f'the provided language ({language}) is not supported: {SUPPORTED_LANGUAGES}'
    assert language in SUPPORTED_LANGUAGES, error_message

    assert namespace.endswith('/'), 'namespace should end with a forward slash'
    assert namespace.startswith('http'), 'namespace should start with http'

    for version in [major_version, minor_version]:
        error_message = f'expecting an integer for the minor and major version, you provided: {type(version)}'
        assert type(version) == int, error_message

    return f'{namespace}fn_{language}-lexicon-{major_version}.{minor_version}'


def generate_lu_rdf_uri(your_fn,
                        namespace,
                        language,
                        major_version,
                        minor_version,
                        lu_id):
    """

    :param str namespace: the RDF namespace, e.g., http://rdf.cltl.nl/
    :param str language: supported: nl | en
    :param int major_version: the major version
    :param int minor_version: the minor version
    :return:
    """
    error_message = f'there is no lu for the provided lu_id ({lu_id}) in the provided FrameNet'
    assert lu_id in your_fn.lu_ids_and_names(), error_message

    error_message = f'the provided language ({language}) is not supported: {SUPPORTED_LANGUAGES}'
    assert language in SUPPORTED_LANGUAGES, error_message

    assert namespace.endswith('/'), 'namespace should end with a forward slash'
    assert namespace.startswith('http'), 'namespace should start with http'

    for version in [major_version, minor_version]:
        error_message = f'expecting an integer for the minor and major version, you provided: {type(version)}'
        assert type(version) == int, error_message

    lexicon_uri = generate_lexicon_rdf_uri(namespace=namespace,
                                           language=language,
                                           major_version=major_version,
                                           minor_version=minor_version)
    lu_rdf_uri = f'{lexicon_uri}-lu-{lu_id}'
    return lu_rdf_uri