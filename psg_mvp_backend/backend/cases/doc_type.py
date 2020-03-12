"""
The DocType for cases app.
DocType is an elasticsearch-dsl abstraction for defining your Elasticsearch mappings,
which is a way to define how your data should be indexed and how the search should behave.

Note that DocType has been deprecated.

Ref: https://www.freshconsulting.com/how-to-create-a-fuzzy-search-as-you-type-feature-with-elasticsearch-and-django/

"""
from elasticsearch_dsl import DocType, Text, Integer, \
        analyzer, tokenizer, HalfFloat, Boolean

analyzer_standard = analyzer(
    'standard',
    tokenizer=tokenizer('trigram', 'edge_ngram', min_gram=1, max_gram=20),
    filter=['lowercase']
)

analyzer_cn = analyzer(
    'smartcn',
    tokenizer=tokenizer('smartcn_tokenizer'),
    filter=['lowercase']  # TODO: should be useless
)

# TODO: WIP
# search on
    # gender -- boolean
    # tag search --
        # end level
        # higher level
    # title -- free text
    # is_official -- boolean
    # sorting -- by day posted (or by surgery date?)
    # location of clinic branch
    # by clinic name
    # number views or likes or whatever


class CaseDoc(DocType):
    """
    Elastic Search Document for Case model.
    """

    # --------------------
    #    ZH fields
    # --------------------
    title = Text(analyzer=analyzer_cn)
    is_official = Boolean()

    # not query this, so no need analyzer
    id = Text()  # TODO: maybe a number or a more suitable field?

    class Meta:
        index = 'cases'
        using = 'default'
