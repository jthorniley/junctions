import factory.random
import pytest


@pytest.fixture(autouse=True)
def fixed_seed(request):
    # Set random seed to test function name, so each function is repeatable
    # but different functions will generally be different
    factory.random.reseed_random(request.node.name)
