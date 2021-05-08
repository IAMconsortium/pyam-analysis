import pandas as pd
import pytest

from pyam import IamDataFrame
from pyam.testing import assert_iamframe_equal
from pyam._ops import _op_data


@pytest.mark.parametrize("append", (False, True))
def test_add_variable(test_df_year, append):
    """Verify that in-dataframe addition works on the default `variable` axis"""

    v = ("Primary Energy", "Primary Energy|Coal", "Sum")
    exp = IamDataFrame(
        pd.DataFrame([1 + 0.5, 6 + 3], index=[2005, 2010]).T,
        model="model_a",
        scenario="scen_a",
        region="World",
        variable=v[2],
        unit="EJ/yr",
        meta=test_df_year.meta,
    )

    if append:
        obs = test_df_year.copy()
        obs.add(*v, append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        assert_iamframe_equal(exp, test_df_year.add(*v))


@pytest.mark.parametrize("append", (False, True))
def test_add_scenario(test_df_year, append):
    """Verify that in-dataframe addition works on a custom axis (`scenario`)"""

    v = ("scen_a", "scen_b", "scen_sum")
    exp = IamDataFrame(
        pd.DataFrame([1 + 2, 6 + 7], index=[2005, 2010]).T,
        model="model_a",
        scenario=v[2],
        region="World",
        variable="Primary Energy",
        unit="EJ/yr",
    )

    if append:
        obs = test_df_year.copy()
        obs.add(*v, axis="scenario", append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        obs = test_df_year.add(*v, axis="scenario")
        assert_iamframe_equal(exp, obs)


@pytest.mark.parametrize("append", (False, True))
def test_subtract_variable(test_df_year, append):
    """Verify that in-dataframe subtraction works on the default `variable` axis"""

    v = ("Primary Energy", "Primary Energy|Coal", "Primary Energy|Other")
    exp = IamDataFrame(
        pd.DataFrame([1 - 0.5, 6 - 3], index=[2005, 2010]).T,
        model="model_a",
        scenario="scen_a",
        region="World",
        variable=v[2],
        unit="EJ/yr",
        meta=test_df_year.meta,
    )

    if append:
        obs = test_df_year.copy()
        obs.subtract(*v, append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        obs = test_df_year.subtract(*v)
        assert_iamframe_equal(exp, obs)


@pytest.mark.parametrize("append", (False, True))
def test_subtract_scenario(test_df_year, append):
    """Verify that in-dataframe subtraction works on a custom axis (`scenario`)"""

    v = ("scen_a", "scen_b", "scen_diff")
    exp = IamDataFrame(
        pd.DataFrame([1 - 2, 6 - 7], index=[2005, 2010]).T,
        model="model_a",
        scenario=v[2],
        region="World",
        variable="Primary Energy",
        unit="EJ/yr",
    )

    if append:
        obs = test_df_year.copy()
        obs.subtract(*v, axis="scenario", append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        obs = test_df_year.subtract(*v, axis="scenario")
        assert_iamframe_equal(exp, obs)


@pytest.mark.parametrize("append", (False, True))
def test_multiply_variable(test_df_year, append):
    """Verify that in-dataframe addition works on the default `variable` axis"""

    v = ("Primary Energy", "Primary Energy|Coal", "Product")
    exp = IamDataFrame(
        pd.DataFrame([1 * 0.5, 6 * 3], index=[2005, 2010]).T,
        model="model_a",
        scenario="scen_a",
        region="World",
        variable=v[2],
        unit="EJ/yr",
        meta=test_df_year.meta,
    )

    if append:
        obs = test_df_year.copy()
        obs.multiply(*v, append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        assert_iamframe_equal(exp, test_df_year.multiply(*v))


@pytest.mark.parametrize("append", (False, True))
def test_multiply_scenario(test_df_year, append):
    """Verify that in-dataframe addition works on a custom axis (`scenario`)"""

    v = ("scen_a", "scen_b", "scen_product")
    exp = IamDataFrame(
        pd.DataFrame([1 * 2, 6 * 7], index=[2005, 2010]).T,
        model="model_a",
        scenario=v[2],
        region="World",
        variable="Primary Energy",
        unit="EJ/yr",
    )

    if append:
        obs = test_df_year.copy()
        obs.multiply(*v, axis="scenario", append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        obs = test_df_year.multiply(*v, axis="scenario")
        assert_iamframe_equal(exp, obs)


@pytest.mark.parametrize("append", (False, True))
def test_divide_variable(test_df_year, append):
    """Verify that in-dataframe addition works on the default `variable` axis"""

    v = ("Primary Energy", "Primary Energy|Coal", "Ratio")
    exp = IamDataFrame(
        pd.DataFrame([1 / 0.5, 6 / 3], index=[2005, 2010]).T,
        model="model_a",
        scenario="scen_a",
        region="World",
        variable=v[2],
        unit="EJ/yr",
        meta=test_df_year.meta,
    )

    if append:
        obs = test_df_year.copy()
        obs.divide(*v, append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        assert_iamframe_equal(exp, test_df_year.divide(*v))


@pytest.mark.parametrize("append", (False, True))
def test_divide_scenario(test_df_year, append):
    """Verify that in-dataframe addition works on a custom axis (`scenario`)"""

    v = ("scen_a", "scen_b", "scen_ratio")
    exp = IamDataFrame(
        pd.DataFrame([1 / 2, 6 / 7], index=[2005, 2010]).T,
        model="model_a",
        scenario=v[2],
        region="World",
        variable="Primary Energy",
        unit="EJ/yr",
    )

    if append:
        obs = test_df_year.copy()
        obs.divide(*v, axis="scenario", append=True)
        assert_iamframe_equal(test_df_year.append(exp), obs)
    else:
        obs = test_df_year.divide(*v, axis="scenario")
        assert_iamframe_equal(exp, obs)


def test_ops_unknown_axis(test_df_year):
    """Using an unknown axis raises an error"""
    with pytest.raises(ValueError, match="Unknown axis: foo"):
        _op_data(test_df_year, "_", "_", "_", "foo")


def test_ops_unknown_method(test_df_year):
    """Using an unknown method raises an error"""
    with pytest.raises(ValueError, match="Unknown method: foo"):
        _op_data(test_df_year, "_", "_", "foo", "variable")
