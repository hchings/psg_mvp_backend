"""
Index cases into Algolia

>> python manage.py index_reviews_algolia

"""
import coloredlogs, logging

from backend.shared.index_model_algolia import Command

from reviews.models import Review
from reviews.serializers import ReviewSerializer

from backend.settings import ALGOLIA_REVIEW_INDEX

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


# class name must be command...
class Command(Command):
    """
    Index published clinics into Algolia.
    """

    help = 'Indexes Reviews in Algolia Search'

    @property
    def index_name(self):
        return ALGOLIA_REVIEW_INDEX

    @property
    def model_serializer(self):
        return ReviewSerializer

    @property
    def model_class(self):
        return Review

    def handle(self, *args, **options):
        super().handle(*args, state="published")
