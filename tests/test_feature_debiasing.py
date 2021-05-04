from pyam import IamDataFrame
from numpy.testing import assert_array_equal


def test_debiasing_count(test_pd_df):
    """Check computing bias weights counting the number of scenarios by scenario name"""

    # modify the default test data to have three distinct scenarios
    test_pd_df.loc[1, "model"] = "model_b"
    df = IamDataFrame(test_pd_df)
    df.compute_bias(method="count", name="bias", axis="scenario")

    assert_array_equal(df["bias"].values, [2, 2, 1])
