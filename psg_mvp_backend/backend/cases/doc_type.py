"""
The DocType for cases app.
DocType is an elasticsearch-dsl abstraction for defining your Elasticsearch mappings,
which is a way to define how your data should be indexed and how the search should behave.

Note that DocType has been deprecated.

Ref: https://www.freshconsulting.com/how-to-create-a-fuzzy-search-as-you-type-feature-with-elasticsearch-and-django/

"""
from elasticsearch_dsl import DocType, Text, \
        analyzer, tokenizer, HalfFloat, Boolean, Keyword, Date

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


class CaseDoc(DocType):
    """
    Elastic Search Document for Case model.
    search on
    gender -- boolean v
    tag search --
        end level  v
        higher level
    title -- free text v
    is_official -- boolean v
    sorting -- by day posted (or by surgery date?)
    by clinic name v  (TODO: need to remove suffix)
    number views or likes or whatever

    """

    # --------------------
    #    ZH fields
    # --------------------
    title = Text(analyzer=analyzer_cn)
    clinic_name = Text(analyzer=analyzer_cn)
    gender = Keyword()
    is_official = Boolean()
    interest = HalfFloat()  # interestingness
    categories = Keyword()
    surgeries = Text(analyzer=analyzer_cn, multi=True)  # unsure?
    skip = Boolean()
    posted = Date()

    # not query this, so no need analyzer
    id = Text()  # TODO: maybe a number or a more suitable field?

    class Meta:
        index = 'cases'
        using = 'default'
