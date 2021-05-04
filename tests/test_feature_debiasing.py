from pyam import IamDataFrame
import pytest
from numpy.testing import assert_array_equal


@pytest.mark.parametrize(
    "axis, exp",
    (["scenario", [0.5, 0.5, 1]], [["model", "scenario"], [1, 1, 1]]),
)
def test_debiasing_count(test_pd_df, axis, exp):
    """Check computing bias weights counting the number of scenarios by scenario name"""

    # modify the default test data to have three distinct scenarios
    test_pd_df.loc[1, "model"] = "model_b"
    df = IamDataFrame(test_pd_df)
    df.compute_bias(method="count", name="bias", axis=axis)

    assert_array_equal(df["bias"].values, exp)


def test_debiasing_unknown_method(test_df_year):
    """Check computing bias weights counting the number of scenarios by scenario name"""
    msg = "Unknown method foo for computing bias weights!"
    with pytest.raises(ValueError, match=msg):
        test_df_year.compute_bias(method="foo", name="bias", axis="scenario")
