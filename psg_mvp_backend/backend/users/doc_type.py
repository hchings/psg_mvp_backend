"""
The DocType for users app.
DocType is an elasticsearch-dsl abstraction for defining your Elasticsearch mappings,
which is a way to define how your data should be indexed and how the search should behave.

Ref: https://www.freshconsulting.com/how-to-create-a-fuzzy-search-as-you-type-feature-with-elasticsearch-and-django/

"""
from elasticsearch_dsl import DocType, Text, Integer, \
        analyzer, tokenizer, HalfFloat, Boolean, Keyword

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


# unused for now as we change to branch level search
class ClinicProfileDoc(DocType):
    """
    Elastic Search Document.
    """

    # --------------------
    #    ZH fields
    # --------------------
    display_name = Text(analyzer=analyzer_cn)
    rating = HalfFloat()
    services = Text(analyzer=analyzer_cn, multi=True)
    regions = Keyword(multi=True)
    num_cases = Integer()
    num_reviews = Integer()
    logo_thumbnail = Text()

    # not query this, so no need analyzer
    id = Text()

    class Meta:
        index = 'clinic_profile'
        using = 'default'


class ClinicBranchDoc(DocType):
    """
    Elastic Search Document.
    """

    display_name = Text(analyzer=analyzer_cn)  # zh fields
    rating = HalfFloat()
    services = Text(analyzer=analyzer_cn)
    open_sunday = Boolean()

    # not query these, so no need analyzer
    # TODO: make sure these fields won't be search
    id = Text()
    branch_name = Text()
    address = Text()
    open_info = Text()

    class Meta:
        index = 'clinic_profile'
        using = 'default'
