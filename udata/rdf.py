# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
'''
This module centralize udata-wide RDF helpers and configuration
'''
from flask import request, url_for

from rdflib import Graph
from rdflib.namespace import (
    Namespace, NamespaceManager, DCTERMS, SKOS, FOAF, XSD, RDFS
)
from rdflib.util import SUFFIX_FORMAT_MAP, guess_format as raw_guess_format
from rdflib_jsonld.context import Context

# Extra Namespaces
ADMS = Namespace('http://www.w3.org/ns/adms#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
SCHEMA = Namespace('http://schema.org/')
SPDX = Namespace('http://spdx.org/rdf/terms#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
DCT = DCTERMS  # More common usage

namespace_manager = NamespaceManager(Graph())
namespace_manager.bind('foaf', FOAF)
namespace_manager.bind('dct', DCT)
namespace_manager.bind('skos', SKOS)
namespace_manager.bind('dcat', DCAT)
namespace_manager.bind('foaf', FOAF)
namespace_manager.bind('hydra', HYDRA)
namespace_manager.bind('vcard', VCARD)
namespace_manager.bind('rdfs', RDFS)
namespace_manager.bind('xsd', XSD)

# Support JSON-LD in format detection
FORMAT_MAP = SUFFIX_FORMAT_MAP.copy()
FORMAT_MAP['json'] = 'json-ld'
FORMAT_MAP['jsonld'] = 'json-ld'
FORMAT_MAP['xml'] = 'xml'

# Map serialization formats to MIME types
RDF_MIME_TYPES = {
    'xml': 'application/rdf+xml',
    'n3': 'text/n3',
    'turtle': 'application/x-turtle',
    'nt': 'application/n-triples',
    'json-ld': 'application/ld+json',
    'trig': 'application/trig',
    # Available but no activated
    # 'nquads': 'application/n-quads',
    # 'trix': 'text/xml',
}

# Map accepted MIME types to known formats
ACCEPTED_MIME_TYPES = {
    'application/rdf+xml': 'xml',
    'application/xml': 'xml',
    'text/n3': 'n3',
    'application/x-turtle': 'turtle',
    'text/turtle': 'turtle',
    'application/n-triples': 'nt',
    'application/ld+json': 'json-ld',
    'application/json': 'json-ld',
    'application/trig': 'trig',
    # Available but no activated
    # 'application/n-quads': 'nquads',
    # 'text/xml': 'trix',
}

# Map formats to default used extensions
RDF_EXTENSIONS = {
    'xml': 'xml',
    'n3': 'n3',
    'turtle': 'ttl',
    'nt': 'nt',
    'trig': 'trig',
    'json-ld': 'json',
    # Available but no activated
    # 'nquads': 'nq',
    # 'trix': 'trix',
}


def guess_format(string):
    '''Guess format given an extension or a mime-type'''
    return raw_guess_format(string, FORMAT_MAP)


def negociate_content(default='json-ld'):
    '''Perform a content negociation on the format given the Accept header'''
    mimetype = request.accept_mimetypes.best_match(ACCEPTED_MIME_TYPES.keys())
    return ACCEPTED_MIME_TYPES.get(mimetype, default)


def want_rdf():
    '''Check wether client prefer RDF over the default HTML'''
    mimetype = request.accept_mimetypes.best
    return mimetype in ACCEPTED_MIME_TYPES


# JSON-LD context used for udata DCAT representation
CONTEXT = {
    # Namespaces
    '@vocab': 'http://www.w3.org/ns/dcat#',
    'dcat': 'http://www.w3.org/ns/dcat#',
    'dct': 'http://purl.org/dc/terms/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'org': 'http://www.w3.org/ns/org#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'spdx': 'http://spdx.org/rdf/terms#',
    'vcard': 'http://www.w3.org/2006/vcard/ns#',
    # Aliased field
    'downloadURL': {
        '@id': 'dcat:downloadURL',
        '@type': '@id'
    },
    'accessURL': {
        '@id': 'dcat:accessURL',
        '@type': '@id'
    },
    'title': 'dct:title',
    'description': 'dct:description',
    'issued': {
        '@id': 'dct:issued',
        '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
    },
    'modified': {
        '@id': 'dct:modified',
        '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
    },
    'language': 'dct:language',
    'license': 'dct:license',
    'rights': 'dct:rights',
    'spatial': 'dct:spatial',
    'publisher': 'dct:publisher',
    'identifier': 'dct:identifier',
    'temporal': 'dct:temporal',
    'format': 'dct:format',
    'accrualPeriodicity': 'dct:accrualPeriodicity',
    'homepage': {
        '@id': 'foaf:homepage',
        '@type': '@id'
    },
    'fn': 'vcard:fn',
    'hasEmail': 'vcard:email',
    'name': 'skos:prefLabel',
    'subOrganizationOf': 'org:subOrganizationOf',
    'checksum': 'spdx:checksum',
    'algorithm': {
        '@id': 'spdx:algorithm',
        '@type': '@id'
    },
    'checksumValue': 'spdx:checksumValue',
    'label': 'rdfs:label',
    'name': 'foaf:name',
}


class UDataContext(Context):
    '''
    An hackish way to serialize context as a root relative URL.

    Exploit this issue https://github.com/RDFLib/rdflib-jsonld/issues/37
    and the fact that this method is used to render the context in the
    resulting JSON-LD.

    See: https://github.com/RDFLib/rdflib-jsonld/blob/master/rdflib_jsonld/serializer.py#L101-L103
    '''

    def to_dict(self):
        '''Hackish way to provide the site context URL'''
        return url_for('site.jsonld_context', _external=True)


context = UDataContext(CONTEXT)
