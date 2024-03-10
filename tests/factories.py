"""Module level docstring describing the purpose of this module."""

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from faker import Faker
from service.models import Product, Category

fake = Faker()


class ProductFactory(factory.Factory):  # pylint: disable=R0903
    """Creates fake products for testing."""
    def dummy_method(self):
        """A dummy public method"""

    def dummy_method_one(self):
        """A dummy public method"""

    def dummy_method_two(self):
        """A dummy public method"""

    class Meta:
        """Maps factory to data model."""
        model = Product
    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(
        choices=[
            "Hat",
            "Pants",
            "Shirt",
            "Apple",
            "Banana",
            "Pots",
            "Towels",
            "Ford",
            "Chevy",
            "Hammer",
            "Wrench"
        ]
    )
    description = factory.Faker("text")
    price = FuzzyDecimal(0.5, 2000.0, 2)
    available = FuzzyChoice(choices=[True, False])
    category = FuzzyChoice(
        choices=[
            Category.UNKNOWN,
            Category.CLOTHS,
            Category.FOOD,
            Category.HOUSEWARES,
            Category.AUTOMOTIVE,
            Category.TOOLS,
        ]
    )
