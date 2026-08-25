from datetime import date

from models.ingredient import Ingredient
from utils.pandas_utils import inventory_to_freshness_df, kitchen_insight_frames


def _ingredient(name, category, shelf_life):
    # The freshness engine deliberately uses today's date, so the fixture must
    # be relative to today rather than becoming stale as calendar time passes.
    return Ingredient(1, 7, name, category, 1, "pcs", "FRESH", shelf_life, "", 1.0, date.today().isoformat(), "", shelf_life)


def test_kitchen_insights_are_derived_from_real_inventory_dataframe():
    inventory = inventory_to_freshness_df([
        _ingredient("Tomato", "Produce", 0), _ingredient("Milk", "Dairy", 1), _ingredient("Rice", "Pantry", 7),
    ])
    insights = kitchen_insight_frames(inventory)
    freshness = dict(zip(insights["freshness"]["Freshness"], insights["freshness"]["Ingredients"]))
    categories = dict(zip(insights["categories"]["Category"], insights["categories"]["Ingredients"]))
    assert freshness == {"USE TODAY": 1, "USE SOON": 1, "FRESH": 1}
    assert categories == {"Produce": 1, "Dairy": 1, "Pantry": 1}


def test_empty_inventory_has_no_fabricated_chart_values():
    insights = kitchen_insight_frames(inventory_to_freshness_df([]))
    assert insights["freshness"].empty and insights["categories"].empty
