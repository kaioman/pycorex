import pytest

def pytest_addoption(parser):
    parser.addoption("--persona-name", action="store", default="Lotta")

@pytest.fixture
def persona_name(request):
    return request.config.getoption("--persona-name")