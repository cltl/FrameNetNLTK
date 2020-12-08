from rdflib.namespace import RDF, RDFS, XSD
from rdflib.namespace import Namespace
from rdflib import URIRef
from rdflib import Literal, BNode
from rdflib import ConjunctiveGraph, Graph


SUPPORTED_LANGUAGES = {
    'eng',
    'nld'
}

LANGUAGE_TO_ADJECTIVE = {
    'eng' : 'English',
    'nld' : 'Dutch'
}

LUTYPE_TO_LU_TYPE_URL = {
    'idiom' : 'http://www.lexinfo.net/ontology/3.0/lexinfo#idiom',
}

LU_TYPE_URL_TO_INFO = {
    'phrasal' : {
        "type" : "http://www.w3.org/2002/07/owl#Thing",
        "label" : "phrasal verb",
        "comment" : "most often the combination of a verb and a verb particle.",
        "seeAlso" : "https://en.wikipedia.org/wiki/Phrasal_verb"
    },
    'endocentric compound' : {
        "type" : "http://www.w3.org/2002/07/owl#Thing",
        "label" : "endocentric compound",
        "comment" : "most often a compound with a head and a modfier.",
        "seeAlso" : "http://www.glottopedia.org/index.php/Endocentric_compound",
        "subtype" : "http://www.lexinfo.net/ontology/3.0/lexinfo#compound"
    },
    'exocentric compound' : {
        "type": "http://www.w3.org/2002/07/owl#Thing",
        "label": "exocentric compound",
        "comment": "a compound that lacks a head",
        "seeAlso": "http://www.glottopedia.org/index.php/Exocentric_compound",
        "subtype": "http://www.lexinfo.net/ontology/3.0/lexinfo#compound"
    }
}


def initialize_graph(namespace):
    """
    initialize graph with our own relationships

    :return:
    """
    g = Graph()

    # TODO: lu types
    for lu_type, lu_type_info in LU_TYPE_URL_TO_INFO.items():
        lu_type_url = f'{namespace}{lu_type.replace(" ","_")}'
        LUTYPE_TO_LU_TYPE_URL[lu_type] = lu_type_url
        lu_type_obj = URIRef(lu_type_url)
        g.add((lu_type_obj, RDF.type, URIRef(lu_type_info['type'])))
        g.add((lu_type_obj, RDFS.label, Literal(lu_type_info['label'])))
        g.add((lu_type_obj, RDFS.comment, Literal(lu_type_info['comment'])))
        g.add((lu_type_obj, RDFS.seeAlso, URIRef(lu_type_info['seeAlso'])))

        if 'subtype' in lu_type_info:
            g.add((lu_type_obj,
                   URIRef('https://www.w3.org/2009/08/skos-reference/skos.html#broader'),
                   URIRef(lu_type_info['subtype'])))

    return g





def get_lexeme_info(lexeme,
                    g,
                    DCT,
                    LEMON):
    """
    generate dictionary of information used per lexem

    :param nltk.corpus.reader.framenet.PrettyDict lexeme: a lexeme

    :rtype: dict
    """
    bn_node = BNode()

    lu_id = lexeme.get('lu_id', None)

    if lu_id is not None:
        le_obj_of_component = get_le_uri(g=g,
                                         DCT=DCT,
                                         LEMON=LEMON,
                                         lu_identifier=lu_id)
    else:
        le_obj_of_component = None

    info = {
        'bn_node' : bn_node,
        'le_obj_of_component' : le_obj_of_component

    }

    return info

def add_decomposition(g,
                      lu,
                      LEMON,
                      DCT,
                      lemon,
                      le_obj):
    """
    add lemon representation of decomposition of terms

    :param rdflib.graph.Graph g: the graph to which we are added information

    :param nltk.corpus.reader.framenet.AttrDict lu: FrameNet NLTK LU object
    :param rdflib.namespace.Namespace LEMON: Lemon namespace
    :param rdflib.graph.Graph lemon: lemon graph
    :param rdflib.URIRef le_obj: uriref of LexicalEntry
    """


    # LE -> : blank node representing first :ComponentList
    assert LEMON.decomposition in lemon.subjects()

    lexeme_order_to_info = {
        lexeme['order'] : get_lexeme_info(lexeme=lexeme,
                                          g=g,
                                          DCT=DCT,
                                          LEMON=LEMON)
        for lexeme in lu.lexemes
    }

    for lexeme_order, lexeme_info in sorted(lexeme_order_to_info.items()):

        # TODO: add complement information in separate function
        comp_uri = le_obj + f'#Component{lexeme_order}'
        comp_obj = URIRef(comp_uri)

        g.add((lexeme_info['bn_node'], RDF.first, comp_obj))
        if lexeme_info['le_obj_of_component'] is not None:
            assert LEMON.element in lemon.subjects()
            g.add((comp_obj, LEMON.element, lexeme_info['le_obj_of_component']))

        # add relationships between :LexicalEntry and :ComponentList(s)
        order_plus_one = lexeme_order + 1

        # first :ComponentList is linked to LexicalEntry
        if lexeme_order == 1:
            g.add((le_obj, LEMON.decomposition, lexeme_info['bn_node']))
        # second: :ComponentList is linked to :ComponentList
        if order_plus_one in lexeme_order_to_info:
            g.add((lexeme_info['bn_node'],
                   RDF.rest,
                   lexeme_order_to_info[order_plus_one]['bn_node']))
        # last: last item in the list is linked to RDF.nil
        else:
            g.add((lexeme_info['bn_node'],
                  RDF.rest,
                  RDF.nil))


def get_le_uri(g,
               DCT,
               LEMON,
               lu_identifier):
    """
    query to obtain LexicalEntry URI
    """
    query = f"""SELECT ?le_obj WHERE {{ 
            ?lu_obj <{RDF.type}> <{LEMON.LexicalSense}> . 
            ?lu_obj <{DCT.identifier}> {lu_identifier} .
            ?lu_obj <{LEMON.isSenseOf}> ?le_obj . }}
    """
    result = g.query(query)

    urirefs = []

    for info in result.bindings:
        for uriref in info.values():
            urirefs.append(uriref)

    assert len(urirefs) == 1

    le_obj = urirefs[0]

    return le_obj


def get_lu_type(lu, language):
    """
    the attribute lu is only defined for Dutch FrameNet.
    this function determines what the lu type is

    :param lu:
    :return:
    """
    if language == 'eng':
        raise NotImplementedError('lu type function not implemented.')
    elif language == 'nld':
        lu_type = lu.lu_type

    if lu_type == 'singleton':
        return lu_type, None

    lu_type_uri = LUTYPE_TO_LU_TYPE_URL[lu_type]
    lu_type_obj = URIRef(lu_type_uri)

    return lu_type, lu_type_obj

def get_word_or_phrase(lu_type, lexemes, LEMON, lemon):
    """

    :param lu_type:
    :param lexemes:
    :return:
    """

    if lu_type is not None:

        if lu_type in {'endocentric compound',
                       'exocentric compound',
                       'singleton'}:
            word_or_phrase = 'word'
        elif lu_type in {'phrasal',
                         'idiom'}:
            word_or_phrase = 'phrase'
        else:
            raise Exception(f'unknown lu type {lu_type}')
    else:
        num_lexemes = len(lexemes)

        if num_lexemes == 1:
            word_or_phrase = 'word'
        elif num_lexemes >= 2:
            word_or_phrase = 'phrase'

    lemon_obj = None

    if word_or_phrase == 'word':
        assert LEMON.Word in lemon.subjects()
        lemon_obj = LEMON.Word
    elif word_or_phrase == 'phrase':
        assert LEMON.Phrase in lemon.subjects()
        lemon_obj = LEMON.Phrase

    return lemon_obj



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
    g = initialize_graph(namespace=namespace)

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

        if verbose >= 3:
            print(f'convert LU {lu.ID} ({lu.name}) to Lemon')

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
        assert LEMON.isSenseOf in lemon.subjects()
        g.add((lu_obj, LEMON.isSenseOf, le_obj))

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

    for lu in your_fn.lus():

        # obtain LE obj
        le_obj = get_le_uri(g=g,
                            DCT=DCT,
                            LEMON=LEMON,
                            lu_identifier=lu.ID)

        # LU type
        lu_type,\
        lu_type_obj = get_lu_type(lu=lu, language=language)

        if lu_type_obj is not None:
            g.add((le_obj, RDF.type, lu_type_obj))

        word_or_phrase = get_word_or_phrase(lu_type=lu_type,
                                            lexemes=lu.lexemes,
                                            LEMON=LEMON,
                                            lemon=lemon)

        g.add((le_obj, RDF.type, word_or_phrase))

        if lu_type == 'singleton':
            continue
        elif lu_type in {'endocentric compound',
                         'exocentric compound',
                         'idiom',
                         'phrasal'}:
            add_decomposition(g=g,
                              lu=lu,
                              DCT=DCT,
                              LEMON=LEMON,
                              lemon=lemon,
                              le_obj=le_obj)
        else:
            raise Exception(f'lu type ({lu_type}) not known')

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


def get_rdf_label(graph, uri):
    query = """SELECT ?o WHERE {
        <%s> rdfs:label ?o
    }"""
    the_query = query % uri

    results = graph.query(the_query)

    labels = set()
    for result in results:
        label = str(result.asdict()['o'])
        labels.add(label)

    assert len(labels) == 1, f'expected one label for {uri}, got {labels}'

    return labels.pop()