import os
import logging
import pytest
from mysharelib.tools import setup_logger
from openbb_tdx import project_name


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    setup_logger(project_name)


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


@pytest.fixture
def default_provider():
    return "tdxquant"


@pytest.fixture
def tdxquant_api_key():
    return os.environ.get("TDXQUANT_API_KEY")
