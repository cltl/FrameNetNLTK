from collections import defaultdict
from datetime import datetime

from rdflib.namespace import RDF, RDFS, XSD
from rdflib.namespace import Namespace
from rdflib import URIRef
from rdflib import Literal, BNode
from rdflib import ConjunctiveGraph, Graph
from graphviz import Digraph



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


COMP_ATTR_TO_URL = {}

COMP_ATTR_TO_INFO = {
    "order" : {
        "type" : "http://www.w3.org/2002/07/owl#Thing",
        "label" : "order",
        "comment": "the order of the lexeme in the lemma (starting from 1)",
        "seeAlso": "http://purl.org/olia/ubyCat.owl#position"
    },
    "headword" : {
        "type": "http://www.w3.org/2002/07/owl#Thing",
        "label" : "headword",
        "comment" : "the lexeme is the head (true or false)",
        "seeAlso": "http://purl.org/olia/ubyCat.owl#isHead"
    },
    "breakBefore" : {
        "type": "http://www.w3.org/2002/07/owl#Thing",
        "label" : "breakBefore",
        "comment": "Can this lexeme be separated from the previous lexeme by another token?",
        "seeAlso": "http://purl.org/olia/ubyCat.owl#isBreakBefore"
    },
    "name" : {
        "type": "http://www.w3.org/2002/07/owl#Thing",
        "label": "name",
        "comment": "the lexeme itself",
        "seeAlso" : "http://www.w3.org/ns/lemon/ontolex#writtenRep"
    },
    "incorporatedFE" : {
        "type": "http://www.w3.org/2002/07/owl#Thing",
        "label" : "incorporatedFE",
        "comment" : "indicates the incorporated Frame Element of an LU, which can be indicated at the level of the lexeme and of the Lexical Unit"
    }
}


def initialize_graph(g, namespace, SKOS):
    """
    initialize graph with our own relationships

    :return:
    """
    # lu types
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
                   SKOS.broader,
                   URIRef(lu_type_info['subtype'])))
    
    # component attributes
    for comp_attr, comp_info in COMP_ATTR_TO_INFO.items():
        comp_attr_url = f'{namespace}{comp_attr}'
        COMP_ATTR_TO_URL[comp_attr] = comp_attr_url

        comp_attr_obj = URIRef(comp_attr_url)
        g.add((comp_attr_obj, RDF.type, URIRef(comp_info['type'])))
        g.add((comp_attr_obj, RDFS.label, Literal(comp_info['label'])))
        g.add((comp_attr_obj, RDFS.comment, Literal(comp_info['comment'])))

        if 'seeAlso' in comp_info:
            g.add((comp_attr_obj, RDFS.seeAlso, URIRef(comp_info['seeAlso'])))


def get_lexeme_info(lexeme,
                    premon,
                    frame_uri,
                    fn_pos_to_lexinfo,
                    g,
                    DCT,
                    LEMON,
                    LEXINFO):
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
        'le_obj_of_component' : le_obj_of_component,
        'attr_to_value' : {
        }

    }


    for attr, string_value in lexeme.items():

        if attr == 'POS':
            attr_obj = LEXINFO.partOfSpeech
            value_obj = URIRef(fn_pos_to_lexinfo[string_value])
        elif attr in {'breakBefore', 'headword', 'name'}:
            attr_obj = URIRef(COMP_ATTR_TO_URL[attr])
            value_obj = Literal(string_value)
        elif attr == 'order':
            attr_obj = URIRef(COMP_ATTR_TO_URL[attr])
            value_obj = Literal(string_value, datatype=XSD.integer)
        elif attr == 'incorporatedFE':
            fe_uri = get_fe_uri(graph=premon, frame_uri=frame_uri, fe_label=string_value)
            attr_obj = URIRef(COMP_ATTR_TO_URL[attr])
            value_obj = URIRef(fe_uri)
        elif attr == 'lu_id':
            pass # this is covered outside of this function
        else:
            raise Exception(f'attr ({attr}) not known. Please inspect.')

        info['attr_to_value'][attr_obj] = value_obj

    return info

def add_complement_attributes(g, lexeme_info, comp_obj):
    """

    :param g:
    :param lexeme_info:
    :return:
    """
    for attr_obj, value_obj in lexeme_info['attr_to_value'].items():
        g.add((comp_obj, attr_obj, value_obj))


def add_decomposition(g,
                      fn_pos_to_lexinfo,
                      frame_uri,
                      lu,
                      LEMON,
                      LEXINFO,
                      DCT,
                      lemon,
                      premon,
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
                                          premon=premon,
                                          frame_uri=frame_uri,
                                          fn_pos_to_lexinfo=fn_pos_to_lexinfo,
                                          g=g,
                                          DCT=DCT,
                                          LEMON=LEMON,
                                          LEXINFO=LEXINFO)
        for lexeme in lu.lexemes
    }

    for lexeme_order, lexeme_info in sorted(lexeme_order_to_info.items()):

        comp_uri = le_obj + f'#Component{lexeme_order}'
        comp_obj = URIRef(comp_uri)
        assert LEMON.Component in lemon.subjects()
        g.add((comp_obj, RDF.type, LEMON.Component))

        g.add((lexeme_info['bn_node'], RDF.first, comp_obj))
        if lexeme_info['le_obj_of_component'] is not None:
            assert LEMON.element in lemon.subjects()
            g.add((comp_obj, LEMON.element, lexeme_info['le_obj_of_component']))
            assert LEMON.Component in lemon.subjects()
            g.add((comp_obj, RDF.type, LEMON.Component))

        add_complement_attributes(g=g, lexeme_info=lexeme_info, comp_obj=comp_obj)

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

    assert len(urirefs) == 1, f'expected to find one uri , found {urirefs}'

    le_obj = urirefs[0]

    return le_obj


def get_lu_type(lu, language):
    """
    the attribute lu is only defined for Dutch FrameNet.
    this function determines what the lu type is

    :param lu:
    :return:
    """
    if language == 'nld':
        lu_type = lu.lu_type

    elif language == 'eng':
        return None, None

    if lu_type == 'singleton':
        return lu_type, None

    lu_type_uri = LUTYPE_TO_LU_TYPE_URL[lu_type]
    lu_type_obj = URIRef(lu_type_uri)

    return lu_type, lu_type_obj

def get_word_or_phrase(lu_type, lexemes, language, LEMON, lemon):
    """

    :param lu_type:
    :param lexemes:
    :return:
    """

    if language == 'eng':

        if len(lexemes) == 1:
            word_or_phrase = 'word'
        elif len(lexemes) >= 2:
            word_or_phrase = 'phrase'
        else:
            raise Exception(f'there should be 1 or more lexemes: {lexemes}')

    if language == 'nld':
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



def get_provenance_uriref(lexicon_uri, cBy, lu):
    provenance_uri = f'{lexicon_uri}#Provenance{cBy}'
    return URIRef(provenance_uri)


def get_date(cDate):
    template = '%m/%d/%Y %H:%M:%S'
    date = datetime.strptime(cDate[:-8], template)
    rdf_string = date.strftime('%Y-%m-%dT%I:%M:%s')

    return rdf_string


def add_agents_and_provenances(your_fn,
                               g,
                               lexicon_uri,
                               PROV,
                               language,
                               verbose=0):
    """

    :param your_fn: your framenet in nltk format
    :param g: the lemon graph of your framenet
    :param verbose:
    :return:
    """
    cby_prov_to_cdates = defaultdict(list)
    for lu in your_fn.lus():
        cby = lu.cBy
        prov = lu.get('provenance')

        if prov is not None:
            key = (cby, prov)
        else:
            key = (cby, None)

        date = datetime.strptime(lu.cDate[:-8], '%m/%d/%Y %H:%M:%S')

        cby_prov_to_cdates[key].append(date)


    cby_prov_to_prov_obj = {}
    for (cby, provenance), dates in cby_prov_to_cdates.items():
        # add software agent
        software_agent_uri = f'{lexicon_uri}#SoftwareAgent#{cby}'
        software_agent_obj = URIRef(software_agent_uri)

        g.add((software_agent_obj, RDF.type, PROV.SoftwareAgent))
        g.add((software_agent_obj, RDFS.label, Literal(cby, lang=language)))

        # add provenance
        if provenance is not None:
            provenance_uri = f'{lexicon_uri}#Provenance#{cby}-{provenance}'
        else:
            provenance_uri = f'{lexicon_uri}#Provenance#{cby}'

        provenance_obj = URIRef(provenance_uri)
        g.add((provenance_obj, RDF.type, PROV.Activity))

        start = min(dates)
        start_rdf_string = start.strftime('%Y-%m-%dT%I:%M:%s')
        end = max(dates)
        end_rdf_string = end.strftime('%Y-%m-%dT%I:%M:%s')

        g.add((provenance_obj, PROV.startedAtTime, Literal(start_rdf_string,
                                                           datatype=XSD.dateTime)))
        g.add((provenance_obj, PROV.endedAtTime, Literal(end_rdf_string,
                                                         datatype=XSD.dateTime)))


        g.add((provenance_obj, PROV.wasAssociatedWith, software_agent_obj))

        cby_prov_to_prov_obj[(cby, provenance)] = provenance_obj

    return cby_prov_to_prov_obj




def convert_to_lemon(lemon,
                     premon_nt_path,
                     ontolex,
                     fn_pos_to_lexinfo,
                     your_fn,
                     namespace,
                     namespace_prefix,
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
    :param str namespace_prefix: e.g., dfn for Dutch FrameNet
    :param str language: supported: nld | eng
    :param int major_version: the major version
    :param int minor_version: the minor version
    """
    from .LexicalDataD2TAnnotationTool import lemmas_from_lu_name

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


    g = Graph()

    LEMON = Namespace('http://lemon-model.net/lemon#')
    DCT = Namespace('http://purl.org/dc/terms/')
    LEXINFO = Namespace('http://www.lexinfo.net/ontology/3.0/lexinfo#')
    ONTOLEX = Namespace('http://www.w3.org/ns/lemon/ontolex#')
    PROV = Namespace('http://www.w3.org/ns/prov#')
    skos_namespace = 'http://www.w3.org/2004/02/skos/core#'
    SKOS =  Namespace(skos_namespace)
    FN = Namespace(namespace)

    g.bind('lemon', LEMON)
    g.bind('dct', DCT)
    g.bind('lexinfo', LEXINFO)
    g.bind('prov', PROV)
    g.bind('ontolex', ONTOLEX)
    g.bind('skos', SKOS)
    g.bind('prov', PROV)
    g.bind(namespace_prefix, FN)

    # initialize graph
    initialize_graph(g=g, namespace=namespace, SKOS=SKOS)

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

    the_lu_iterable = list(your_fn.lus())

    cby_prov_to_prov_obj = add_agents_and_provenances(your_fn=your_fn,
                                                      g=g,
                                                      lexicon_uri=lexicon_uri,
                                                      PROV=PROV,
                                                      language=language,
                                                      verbose=verbose)

    # update for each LE and LU
    for index, lu in enumerate(the_lu_iterable):

        provenance_obj = cby_prov_to_prov_obj[(lu.cBy, lu.get('provenance'))]

        if verbose >= 3:
            print(f'convert LU {lu.ID} ({lu.name}) to Lemon')

        if all([verbose >= 5,
                index == 5]):
            print('QUITTING AFTER FIRST FIVE ITERATIONS TOP')
            break

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

        # provenance LE
        date = get_date(cDate=lu.cDate)
        g.add((le_obj, PROV.generatedAtTime, Literal(date,
                                                     datatype=XSD.dateTime)))
        g.add((le_obj, PROV.wasGeneratedBy, provenance_obj))

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

        for lemma_variant in lemmas_from_lu_name(lemma):
            g.add((le_form_obj, LEMON.writtenRep, Literal(lemma_variant, lang=language)))

        assert LEMON.canonicalForm in lemon.subjects()
        g.add((le_obj, LEMON.canonicalForm, le_form_obj))

        # update LU information


        lu_obj = URIRef(lu_uri)

        # provenance LU
        date = get_date(cDate=lu.cDate)
        g.add((lu_obj, PROV.generatedAtTime, Literal(date,
                                                     datatype=XSD.dateTime)))
        g.add((lu_obj, PROV.wasGeneratedBy, provenance_obj))

        assert LEMON.sense in lemon.subjects()
        g.add((le_obj, LEMON.sense, lu_obj))
        assert LEMON.LexicalSense in lemon.subjects()
        g.add((lu_obj, RDF.type, LEMON.LexicalSense))
        g.add((lu_obj, DCT.identifier, Literal(lu.ID,
                                              datatype=XSD.integer)))
        assert LEMON.isSenseOf in lemon.subjects()
        g.add((lu_obj, LEMON.isSenseOf, le_obj))

        assert LEMON.definition in lemon.subjects()
        g.add((lu_obj, LEMON.definition, Literal(lu.definition,
                                                 lang=language)))


        # update with SKOS relationships to external references
        table = {ord('{'): '', ord('}'): ''}
        for attr_name, attr_value in lu.items():
            if attr_name.startswith('{%s}' % skos_namespace):
                skos_pred_uri = attr_name.translate(table)
                skos_pred_uriref = URIRef(skos_pred_uri)
                value_uriref = URIRef(attr_value)
                g.add((lu_obj, skos_pred_uriref, value_uriref))

        # evokes relationship
        frame_uri = get_rdf_uri(premon_nt=premon,
                                frame_label=lu.frame.name)
        frame_obj = URIRef(frame_uri)

        # add incorporatedFE if it is there
        incorporated_fe_label = lu.get('incorporatedFE', None)

        # mistakes in English FrameNet
        if all([frame_uri == 'http://premon.fbk.eu/resource/fn17-measurable_attributes',
                incorporated_fe_label == 'Dimension']):
            incorporated_fe_label = None

        if incorporated_fe_label is not None:
            fe_uri = get_fe_uri(graph=premon, frame_uri=frame_uri, fe_label=incorporated_fe_label)
            attr_obj = URIRef(COMP_ATTR_TO_URL['incorporatedFE'])
            g.add((lu_obj, attr_obj, URIRef(fe_uri)))

        assert frame_obj in premon.subjects()
        assert ONTOLEX.evokes in ontolex.subjects()
        g.add((le_obj, ONTOLEX.evokes, frame_obj))

        assert LEMON.entry in lemon.subjects()
        assert frame_obj
        g.add((lexicon_uri_obj, LEMON.entry, le_obj))

    for index, lu in enumerate(the_lu_iterable):

        if verbose >= 3:
            print(f'convert LU {lu.ID} ({lu.name}) to Lemon')

        if all([verbose >= 5,
                index >= 5]):
            print('QUITTING AFTER FIRST FIVE ITERATIONS BOTTOM')
            break

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
                                            language=language,
                                            LEMON=LEMON,
                                            lemon=lemon)

        g.add((le_obj, RDF.type, word_or_phrase))

        # evokes relationship
        frame_uri = get_rdf_uri(premon_nt=premon,
                                frame_label=lu.frame.name)


        if language == 'nld':
            if lu_type == 'singleton':
                continue
            elif lu_type in {'endocentric compound',
                             'exocentric compound',
                             'idiom',
                             'phrasal'}:
                add_decomposition(g=g,
                                  fn_pos_to_lexinfo=fn_pos_to_lexinfo,
                                  frame_uri=frame_uri,
                                  lu=lu,
                                  DCT=DCT,
                                  LEMON=LEMON,
                                  LEXINFO=LEXINFO,
                                  lemon=lemon,
                                  premon=premon,
                                  le_obj=le_obj)
            else:
                raise Exception(f'lu type ({lu_type}) not known')

        elif language == 'eng':
            if word_or_phrase == LEMON.Phrase:
                add_decomposition(g=g,
                                  fn_pos_to_lexinfo=fn_pos_to_lexinfo,
                                  frame_uri=frame_uri,
                                  lu=lu,
                                  DCT=DCT,
                                  LEMON=LEMON,
                                  LEXINFO=LEXINFO,
                                  lemon=lemon,
                                  premon=premon,
                                  le_obj=le_obj)


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


def get_fe_uri(graph, frame_uri, fe_label):
    """

    :param graph:
    :param frame_uri:
    :return:
    """
    query = """SELECT ?o WHERE {
             ?o <http://www.w3.org/2000/01/rdf-schema#label> "%s" . 
             <%s> <http://premon.fbk.eu/ontology/core#semRole> ?o
        }"""
    the_query = query % (fe_label, frame_uri)

    results = graph.query(the_query)

    labels = set()
    for result in results:
        label = str(result.asdict()['o'])
        labels.add(label)

    assert len(labels) == 1, f'expected one label for frame ({frame_uri}) with FE label ({fe_label}), got {labels}'

    return labels.pop()



def get_attributes(fn_in_lemon, the_lemon_type):
    """

    :param graph:
    :param the_type:
    :return:
    """
    query = """SELECT ?s ?p ?o WHERE {
                 ?s ?p ?o .
                 ?s <%s> <%s>
            }"""
    the_query = query % (RDF.type, the_lemon_type)

    results = fn_in_lemon.query(the_query)

    s_to_attrs = defaultdict(set)
    for result in results:
        as_dict = result.asdict()
        s = as_dict['s']
        attribute = as_dict['p']
        s_to_attrs[s].add(attribute)

    num_s = len(s_to_attrs)

    attr_to_freq = defaultdict(int)
    for subject, s_attrs in s_to_attrs.items():
        for s_attr in s_attrs:
            attr_to_freq[s_attr] += 1

    attr_to_info = {}
    for attr, freq in attr_to_freq.items():
        ratio = (freq / num_s)
        info = {
            'freq' : freq,
            'ratio' : ratio
        }
        attr_to_info[attr] = info

    return attr_to_info


def get_attributes_between_two(fn_in_lemon, type_one, type_two):
    """

    :param graph:
    :param the_type:
    :return:
    """
    query = """SELECT ?s WHERE {
                 ?s ?p ?o . 
                 ?s <%s> <%s> .
            }"""
    the_query = query % (RDF.type, type_one)
    results = fn_in_lemon.query(the_query)

    all_s = set()
    for result in results:
        as_dict = result.asdict()
        s = as_dict['s']
        all_s.add(s)

    query = """SELECT ?o WHERE {
                 ?s ?p ?o . 
                 ?o <%s> <%s> .
            }"""
    the_query = query % (RDF.type, type_two)
    results = fn_in_lemon.query(the_query)

    all_o = set()
    for result in results:
        as_dict = result.asdict()
        o = as_dict['o']
        all_o.add(o)

    s_p = set()
    for subject, predicate in fn_in_lemon.subject_predicates():
        if subject in all_s:
            s_p.add(predicate)

    p_o = set()
    for predicate, object in fn_in_lemon.predicate_objects():
        if object in all_o:
            p_o.add(predicate)

    result = s_p & p_o

    return result





def shorten_namespaces(fn_in_lemon,
                       uriref):
    uri = uriref.toPython()

    long_to_short = {
        uriref.toPython() : short
        for short, uriref in fn_in_lemon.namespaces()
    }

    for long, short in long_to_short.items():
        uri = uri.replace(long, f'{short}:')

    return uri


def get_id_and_label(fn_in_lemon,
                     uriref,
                     uriref_to_attr_to_info={}):
    """

    :param fn_in_lemon:
    :param uriref:
    :return:
    """
    uri = shorten_namespaces(fn_in_lemon=fn_in_lemon, uriref=uriref)

    attr_to_info = uriref_to_attr_to_info.get(uriref, {})
    attrs_labels = []
    for attr_uriref, attr_info in attr_to_info.items():
        short_attr = shorten_namespaces(fn_in_lemon=fn_in_lemon,
                                        uriref=attr_uriref)
        perc = attr_info['ratio'] * 100
        perc = round(perc, 1)
        attrs_labels.append((perc, f'{short_attr} ({perc}%)'))

    node_id = uri.replace(':', "_")

    if attr_to_info:
        the_labels = sorted(attrs_labels, reverse=True)
        attr_part = '{' + '|'.join([label[1] for label in the_labels]) + '}'
        node_label = '|'.join([uri, attr_part])
    else:
        node_label = uri

    return node_id, node_label


def derive_model(fn_in_lemon, output_path=None, verbose=0):
    """

    :param fn_in_lemon:
    :return:
    """
    LEMON = Namespace('http://lemon-model.net/lemon#')
    PROV = Namespace('http://www.w3.org/ns/prov#')

    the_types = [LEMON.LexicalEntry,
                 LEMON.LexicalSense,
                 LEMON.Form,
                 LEMON.Component,
                 PROV.Activity,
                 PROV.SoftwareAgent]

    type_to_attr_to_info = {}
    for a_type in the_types:
        attr_to_info = get_attributes(fn_in_lemon=fn_in_lemon,
                                      the_lemon_type=a_type)
        type_to_attr_to_info[a_type] = attr_to_info
        if verbose >= 4:
            print(a_type, len(attr_to_info))

    type1_type2_to_attr = {}
    for type_one in the_types:
        for type_two in the_types:
            if type_one != type_two:

                if verbose >= 4:
                    print(f'computing between {type_one} and {type_two}')
                attrs = get_attributes_between_two(fn_in_lemon=fn_in_lemon,
                                                   type_one=type_one,
                                                   type_two=type_two)

                if attrs:
                    assert len(attrs) == 1
                    type1_type2_to_attr[(type_one, type_two)] = attrs.pop()

    g = Digraph()

    # add relationships between lemon types
    for (type_one, type_two), attr in type1_type2_to_attr.items():
        one_id, one_label = get_id_and_label(fn_in_lemon=fn_in_lemon,
                                              uriref=type_one,
                                              uriref_to_attr_to_info=type_to_attr_to_info)

        two_id, two_label = get_id_and_label(fn_in_lemon=fn_in_lemon,
                                              uriref=type_two,
                                              uriref_to_attr_to_info=type_to_attr_to_info)

        attr_id, attr_label = get_id_and_label(fn_in_lemon=fn_in_lemon,
                                                uriref=attr)

        g.node(name=one_id, label=one_label, _attributes={'shape' : 'record'})
        g.node(name=two_id, label=two_label, _attributes={'shape' : 'record'})

        g.edge(tail_name=one_id,
               head_name=two_id,
               label=attr_label)

    # write to disk if preferred
    g.format = 'svg'
    if output_path is not None:
        g.render(output_path)
        if verbose >= 1:
            print(f'written FN in Lemon to {output_path}')

    return g
