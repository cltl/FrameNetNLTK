from rdflib.namespace import RDF, RDFS, XSD
from rdflib.namespace import Namespace
from rdflib import URIRef
from rdflib import Literal
from rdflib import ConjunctiveGraph, Graph


SUPPORTED_LANGUAGES = {
    'eng',
    'nld'
}

LANGUAGE_TO_ADJECTIVE = {
    'eng' : 'English',
    'nld' : 'Dutch'
}


def convert_to_lemon(lemon,
                     premon_nt_path,
                     ontolex,
                     fn_pos_to_lexinfo,
                     your_fn,
                     namespace,
                     language,
                     major_version,
                     minor_version,
                     output_path=None,
                     verbose=0):
    """
    Convert the FrameNet in NLTK format to Lemon
    https://lemon-model.net/lemon#

    :param rdflib.graph.Graph lemon: use FrameNetNLTK.lemon
    :param rdflib.graph.Graph premon: use FrameNetNLTK.premon_nt
    :param rdflib.graph.Graph ontolex: use FrameNetNLTK.ontolex
    :param dict fn_pos_to_lexinfo: use FrameNetNLTK.fn_pos_to_lexinfo
    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: a FrameNet in the NLTK format
    :param str namespace: a namespace.
    for Dutch, we use http://rdf.cltl.nl/dfn/
    for English, we use http://rdf.cltl.nl/efn/
    :param str language: supported: nld | eng
    :param int major_version: the major version
    :param int minor_version: the minor version
    """
    # loading premon
    premon = load_nt_graph(nt_path=premon_nt_path)

    # validate parameters
    error_message = f'{language} not part of supported languages: {SUPPORTED_LANGUAGES}'
    assert language in SUPPORTED_LANGUAGES, error_message

    # query for identifiers
    lexicon_uri = generate_lexicon_rdf_uri(namespace=namespace,
                                           language=language,
                                           major_version=major_version,
                                           minor_version=minor_version)
    if verbose >= 2:
        print(f'lexicon uri: {lexicon_uri}')

    # initialize graph
    g = Graph()

    LEMON = Namespace('http://lemon-model.net/lemon#')
    DCT = Namespace('http://purl.org/dc/terms/')
    LEXINFO = Namespace('http://www.lexinfo.net/ontology/3.0/lexinfo#')
    ONTOLEX = Namespace('http://www.w3.org/ns/lemon/ontolex#')

    g.bind('lemon', LEMON)
    g.bind('dct', DCT)
    g.bind('lexinfo', LEXINFO)
    g.bind('ontolex', ONTOLEX)

    # update lexicon information
    lexicon_uri_obj = URIRef(lexicon_uri)

    assert LEMON.Lexicon in lemon.subjects()
    g.add((lexicon_uri_obj, RDF.type, LEMON.Lexicon))

    assert LEMON.language in lemon.subjects()
    g.add((lexicon_uri_obj, LEMON.language, Literal(language)))

    lexicon_label = f'{LANGUAGE_TO_ADJECTIVE[language]} FrameNet v{major_version}.{minor_version}'
    g.add((lexicon_uri_obj, RDFS.label, Literal(lexicon_label)))

    lexicon_version = float(f'{major_version}.{minor_version}')
    g.add((lexicon_uri_obj, DCT.identifier, Literal(lexicon_version,
                                                    datatype=XSD.decimal)))


    # TODO: lu definition

    # update for each LE and LU
    for lu in your_fn.lus():

        # generate LE and LU rdf uri
        le_uri, leform_uri, lu_uri = generate_le_and_lu_rdf_uri(your_fn=your_fn,
                                                                namespace=namespace,
                                                                language=language,
                                                                major_version=major_version,
                                                                minor_version=minor_version,
                                                                lu_id=lu.ID)

        # update LE information
        le_obj = URIRef(le_uri)
        assert LEMON.LexicalEntry in lemon.subjects()
        g.add((le_obj, RDF.type, LEMON.LexicalEntry))

        g.add((le_obj,
               LEXINFO.partOfSpeech,
               URIRef(fn_pos_to_lexinfo[lu.POS]))
               )


        # update LE form
        lemma, pos = lu.name.rsplit('.', 1)
        le_form_obj = URIRef(leform_uri)
        g.add((le_form_obj, RDFS.isDefinedBy, le_obj))
        assert LEMON.Form in lemon.subjects()
        g.add((le_form_obj, RDF.type, LEMON.Form))
        assert LEMON.writtenRep in lemon.subjects()
        g.add((le_form_obj, LEMON.writtenRep, Literal(lemma, lang=language)))

        assert LEMON.canonicalForm in lemon.subjects()
        g.add((le_obj, LEMON.canonicalForm, le_form_obj))

        # update LU information
        lu_obj = URIRef(lu_uri)
        assert LEMON.sense in lemon.subjects()
        g.add((le_obj, LEMON.sense, lu_obj))
        assert LEMON.LexicalSense in lemon.subjects()
        g.add((lu_obj, RDF.type, LEMON.LexicalSense))
        g.add((lu_obj, DCT.identifier, Literal(lu.ID,
                                              datatype=XSD.integer)))
        # evokes relationship
        frame_uri = get_rdf_uri(premon_nt=premon,
                                frame_label=lu.frame.name)
        frame_obj = URIRef(frame_uri)

        assert frame_obj in premon.subjects()
        assert ONTOLEX.evokes in ontolex.subjects()
        g.add((le_obj, ONTOLEX.evokes, frame_obj))

        assert LEMON.entry in lemon.subjects()
        assert frame_obj
        g.add((lexicon_uri_obj, LEMON.entry, le_obj))

        if verbose >= 5:
            print('QUITTING AFTER FIRST ITERATION')
            break


    if output_path is not None:
        g.serialize(format='turtle', destination=output_path)
        if verbose >= 1:
            print(f'written Lemon representation of FrameNet ({major_version}.{minor_version} in language {language}) to {output_path}')



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


def generate_le_and_lu_rdf_uri(your_fn,
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
    :return: (le_uri, leform_uri, lu_uri)
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

    le_rdf_uri = f'{lexicon_uri}-le-{lu_id}'
    leform_rdf_uri = f'{lexicon_uri}-leform-{lu_id}'
    lu_rdf_uri = f'{lexicon_uri}-lu-{lu_id}'
    return le_rdf_uri, leform_rdf_uri, lu_rdf_uri


def load_nquads_file(path_to_nquad_file):
    """
    load rdf file in nquads format
    :param str path_to_nquad_file: path to rdf file in nquad format
    :rtype: rdflib.graph.ConjunctiveGraph
    :return: nquad
    """
    g = ConjunctiveGraph()
    with open(path_to_nquad_file, "rb") as infile:
        g.parse(infile, format="nquads")
    return g

def convert_nquads_to_nt(g, output_path):
    """
    :param rdflib.graph.ConjunctiveGraph g: a nquad graph
    :rtype:
    :return:
    """
    g.serialize(destination=output_path, format='nt')

def load_nt_graph(nt_path):
    g = Graph()
    with open(nt_path, 'rb') as infile:
        g.parse(file=infile, format='nt')

    return g


def get_rdf_uri(premon_nt, frame_label):
    frame_query = """SELECT ?s WHERE {
        ?s rdf:type <http://premon.fbk.eu/ontology/fn#Frame> .
        ?s rdfs:label "%s" .
    }"""
    the_query = frame_query % frame_label
    results = [result
               for result in premon_nt.query(the_query)]

    assert len(results) == 1, f'query should only have one result: {the_query}\n{results}'

    for result in results:
        frame_rdf_uri = str(result.asdict()['s'])

    return frame_rdf_uri