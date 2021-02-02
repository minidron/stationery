from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Index, KeywordField, IntegerField
from elasticsearch_dsl import analyzer
from odinass.models import Offer, Category
from transliterate import translit

# Создание индекса
OfferDocument = Index('offer')

# конфигурация + настройка анализаторов
OfferDocument.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "filter": {
            "autocomplete_filter": {
                "type": "edge_ngram",
                "min_gram": 4,
                "max_gram": 10
            },
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        },
        "analyzer": {
            "autocomplete": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "autocomplete_filter",
                ],
            },

            "with_morphology": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_stemmer",
                    "russian_morphology",
                ]
            }
        },

    }
)


@OfferDocument.doc_type
class OfferDocType(DocType):
    fullname = fields.TextField(
        analyzer='with_morphology'
    )

    category_name = fields.TextField(
        analyzer='with_morphology'
    )

    fullname_translit = fields.TextField(
        analyzer='autocomplete'
    )

    is_published = fields.BooleanField()

    views = fields.IntegerField()

    def prepare_fullname(self, instance):
        return f'{instance.product.article} {instance.product.search_title} {instance.product.title}'

    def prepare_category_name(self, instance):
        return f'{instance.product.category.title}'

    def prepare_fullname_translit(self, instance):
        return translit(f'{instance.product.article} {instance.product.search_title} {instance.product.title}', 'ru')

    def prepare_is_published(self, instance):
        return instance.product.category.is_published

    def prepare_views(self, instance):
        return instance.product.category.views

    class Django:
        model = Offer


# Всё тож самое, ток для разделов
CategoryDocument = Index('category')
CategoryDocument.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "filter": {
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        },
        "analyzer": {
            "with_morphology": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "russian_stop",
                    "russian_stemmer",
                    "russian_morphology",
                ]
            }
        },
    }
)


@CategoryDocument.doc_type
class CategoryDocType(DocType):
    category_name = fields.TextField(
        analyzer='with_morphology'
    )

    is_published = fields.BooleanField()

    views = fields.IntegerField()

    def prepare_category_name(self, instance):
        return f'{instance.title}'

    def prepare_is_published(self, instance):
        return instance.is_published

    def prepare_views(self, instance):
        return instance.views

    class Django:
        model = Category