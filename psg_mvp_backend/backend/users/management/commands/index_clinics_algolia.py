"""
Index cases into Algolia

>> python manage.py index_clinics_algolia

"""
import coloredlogs, logging

from backend.shared.index_model_algolia import Command

from users.clinics.models import ClinicProfile
from users.clinics.serializers import ClinicCardSerializer

from backend.settings import ALGOLIA_APP_ID, ALGOLIA_SECRET, \
    ALGOLIA_CLINIC_INDEX

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


# class name must be command...
class Command(Command):
    """
    Index published clinics into Algolia.
    """

    help = 'Indexes Clinics in Algolia Search'

    @property
    def index_name(self):
        return ALGOLIA_CLINIC_INDEX

    @property
    def model_serializer(self):
        return ClinicCardSerializer

    @property
    def model_class(self):
        return ClinicProfile

    def handle(self, *args, **options):
        super().handle(*args, is_oob=False)
