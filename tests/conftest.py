import random
from datetime import datetime

import pytest

from testrail_api import TestRailAPI


def pytest_addoption(parser):
    group = parser.getgroup('TestRailAPI')
    group.addoption(
        "--tr-url",
        action="store",
        metavar="URL",
        help="TestRail address",
        type=str,
        required=True
    )
    group.addoption(
        "--tr-email",
        action="store",
        metavar="EMAIL",
        help="Email for the account on the TestRail",
        type=str,
        required=True
    )
    group.addoption(
        "--tr-password",
        action="store",
        metavar="PASSWORD",
        help="Password for the account on the TestRail",
        type=str,
        required=True
    )


@pytest.fixture('session')
def config(request):
    return (
        request.config.getoption('--tr-url'),
        request.config.getoption('--tr-email'),
        request.config.getoption('--tr-password')
    )


@pytest.fixture('session')
def api(config):
    return TestRailAPI(*config)


@pytest.fixture('session')
def time_out_api(config):
    return TestRailAPI(*config, timeout=.001)


@pytest.fixture('function')
def suites_project(api):
    r = api.projects.add_project(name=datetime.now().isoformat(), suite_mode=3)
    yield api, r['id']
    api.projects.delete_project(r['id'])


@pytest.fixture('function')
def default_project(api):
    r = api.projects.add_project(name=datetime.now().isoformat(), suite_mode=1)
    yield api, r['id']
    api.projects.delete_project(r['id'])


@pytest.fixture('function')
def default_project_case(default_project):
    api, project_id = default_project
    r = api.sections.add_section(project_id, 'test')
    sections_id = r['id']
    r = api.case_types.get_case_types()
    type_id = random.choice(r)['id']
    r = api.priorities.get_priorities()
    priority_id = random.choice(r)['id']

    case_ids = []
    for i in range(3):
        r = api.cases.add_case(
            sections_id,
            f'test case {i}',
            template_id=1,
            type_id=type_id,
            priority_id=priority_id,
            custom_mission='qwe',
            custom_goals='qwe1',
        )
        case_ids.append(r['id'])
    return api, project_id, case_ids
