import factory

from cases.models import Case, UserInfo, ClinicInfo


class CaseFactory(factory.django.DjangoModelFactory):
    """
    Factory class to create a minimal case object.
    """

    class Meta:
        model = Case

    class Params:
        """
        Extra params that can be passed while initializing the object.
        """

        username = 'testuser'
        uuid = '1'
        state_choice = Case.STATES[0][0]

    title = 'testtitle'
    author = factory.LazyAttribute(lambda params: UserInfo(name=params.username, uuid=params.uuid))
    state = factory.LazyAttribute(lambda params: params.state_choice)
    clinic = ClinicInfo()

