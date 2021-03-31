import factory

from cases.models import Case, UserInfo, ClinicInfo


class CaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Case

    class Params:
        username = 'testuser'
        uuid = '1'
        state_choice = Case.STATES[0][0]

    title = 'testtitle'
    author = factory.LazyAttribute(lambda params: UserInfo(name=params.username, uuid=params.uuid))
    state = factory.LazyAttribute(lambda params: params.state_choice)
    clinic = ClinicInfo()

