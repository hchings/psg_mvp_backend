"""
The DocType for users app.
DocType is an elasticsearch-dsl abstraction for defining your Elasticsearch mappings,
which is a way to define how your data should be indexed and how the search should behave.

Ref: https://www.freshconsulting.com/how-to-create-a-fuzzy-search-as-you-type-feature-with-elasticsearch-and-django/

"""
from elasticsearch_dsl import DocType, Text, Integer, Completion, analyzer, tokenizer

analyzer_standard = analyzer(
    'standard',
    tokenizer=tokenizer('trigram', 'edge_ngram', min_gram=1, max_gram=20),
    filter=['lowercase']
)

# TODO: validate this is working
analyzer_cn = analyzer(
    'smartcn',
    tokenizer=tokenizer('smartcn_tokenizer'),
    filter=['lowercase']  # TODO: should be useless
)


class ClinicProfileDoc(DocType):
    """
    Elastic Search Document.
    """

    # --------------------
    #    ZH fields
    # --------------------
    display_name = Text(analyzer=analyzer_cn)
    obsolete_name = Text(analyzer=analyzer_cn)

    # --------------------
    #    EN fields
    # --------------------
    english_name = Text(analyzer=analyzer_standard)

    # not query this, so no need analyzer
    id = Text()

    class Meta:
        index = 'clinic_profile'
        using = 'default'
