import logging
import pytest
import re
import datetime

import numpy as np
import pandas as pd
from numpy import testing as npt
from pandas import testing as pdt

from pyam import IamDataFrame, filter_by_meta, META_IDX, IAMC_IDX, sort_data, compare
from pyam.core import _meta_idx, concat
from pyam.utils import isstr
from pyam.testing import assert_iamframe_equal


df_filter_by_meta_matching_idx = pd.DataFrame(
    [
        ["model_a", "scen_a", "region_1", 1],
        ["model_a", "scen_a", "region_2", 2],
        ["model_a", "scen_b", "region_3", 3],
    ],
    columns=["model", "scenario", "region", "col"],
)


df_filter_by_meta_nonmatching_idx = pd.DataFrame(
    [
        ["model_a", "scen_c", "region_1", 1, 2],
        ["model_a", "scen_c", "region_2", 2, 3],
        ["model_a", "scen_b", "region_3", 3, 4],
    ],
    columns=["model", "scenario", "region", 2010, 2020],
).set_index(["model", "region"])

META_DF = pd.DataFrame(
    [
        ["model_a", "scen_a", 1, False],
        ["model_a", "scen_b", np.nan, False],
        ["model_a", "scen_c", 2, False],
    ],
    columns=META_IDX + ["foo", "exclude"],
).set_index(META_IDX)


df_empty = pd.DataFrame([], columns=IAMC_IDX + [2005, 2010])


def test_init_df_with_index(test_pd_df):
    df = IamDataFrame(test_pd_df.set_index(META_IDX))
    pd.testing.assert_frame_equal(df.timeseries().reset_index(), test_pd_df)


def test_init_from_iamdf(test_df_year):
    # casting an IamDataFrame instance again works
    df = IamDataFrame(test_df_year)

    # inplace-operations on the new object have effects on the original object
    df.rename(scenario={"scen_a": "scen_foo"}, inplace=True)
    assert test_df_year.scenario == ["scen_b", "scen_foo"]

    # overwrites on the new object do not have effects on the original object
    df = df.rename(scenario={"scen_foo": "scen_bar"})
    assert df.scenario == ["scen_b", "scen_bar"]
    assert test_df_year.scenario == ["scen_b", "scen_foo"]


def test_init_from_iamdf_raises(test_df_year):
    # casting an IamDataFrame instance again with extra args fails
    match = "Invalid arguments \['model'\] for initializing from IamDataFrame"
    with pytest.raises(ValueError, match=match):
        IamDataFrame(test_df_year, model="foo")


def test_init_df_with_float_cols_raises(test_pd_df):
    _test_df = test_pd_df.rename(columns={2005: 2005.5, 2010: 2010.0})
    pytest.raises(ValueError, IamDataFrame, data=_test_df)


def test_init_df_with_duplicates_raises(test_df):
    _df = test_df.timeseries()
    _df = _df.append(_df.iloc[0]).reset_index()
    match = "3  model_a   scen_a  World  Primary Energy  EJ/yr"
    with pytest.raises(ValueError, match=match):
        IamDataFrame(_df)


def test_init_df_with_na_scenario(test_pd_df):
    # missing values in an index dimension raises an error
    test_pd_df.loc[1, "scenario"] = np.nan
    pytest.raises(ValueError, IamDataFrame, data=test_pd_df)


def test_init_df_with_float_cols(test_pd_df):
    _test_df = test_pd_df.rename(columns={2005: 2005.0, 2010: 2010.0})
    obs = IamDataFrame(_test_df).timeseries().reset_index()
    pd.testing.assert_series_equal(obs[2005], test_pd_df[2005])


def test_init_df_from_timeseries(test_df):
    df = IamDataFrame(test_df.timeseries())
    pd.testing.assert_frame_equal(df.timeseries(), test_df.timeseries())


def test_init_df_with_extra_col(test_pd_df):
    tdf = test_pd_df.copy()

    extra_col = "climate model"
    extra_value = "scm_model"
    tdf[extra_col] = extra_value

    df = IamDataFrame(tdf)

    # check that timeseries data is as expected
    obs = df.timeseries().reset_index()
    exp = tdf[obs.columns]  # get the columns into the right order
    pd.testing.assert_frame_equal(obs, exp)


def test_init_df_with_meta(test_pd_df):
    # pass explicit meta dataframe with a scenario that doesn't exist in data
    df = IamDataFrame(test_pd_df, meta=META_DF.iloc[[0, 2]][["foo"]])

    # check that scenario not existing in data is removed during initialization
    pd.testing.assert_frame_equal(df.meta, META_DF.iloc[[0, 1]])


def test_init_df_with_meta_incompatible_index(test_pd_df):
    # define a meta dataframe with a non-standard index
    index = ["source", "scenario"]
    meta = pd.DataFrame(
        [False, False, False], columns=["exclude"], index=META_DF.index.rename(index)
    )

    # assert that using an incompatible index for the meta arg raises
    match = "Incompatible `index=\['model', 'scenario'\]` with `meta` *."
    with pytest.raises(ValueError, match=match):
        IamDataFrame(test_pd_df, meta=meta)


def test_init_df_with_custom_index(test_pd_df):
    # rename 'model' column and add a version column to the dataframe
    test_pd_df.rename(columns={"model": "source"}, inplace=True)
    test_pd_df["version"] = [1, 2, 3]

    # initialize with custom index columns, check that index is set correctly
    index = ["source", "scenario", "version"]
    df = IamDataFrame(test_pd_df, index=index)
    assert df.index.names == index

    # check that index attributes were set correctly and that df.model fails
    assert df.source == ["model_a"]
    assert df.version == [1, 2, 3]
    with pytest.raises(KeyError, match="Index `model` does not exist!"):
        df.model


def test_init_empty_message(caplog):
    IamDataFrame(data=df_empty)
    drop_message = "Formatted data is empty!"
    message_idx = caplog.messages.index(drop_message)
    assert caplog.records[message_idx].levelno == logging.WARNING


def test_init_with_column_conflict(test_pd_df):
    # add a column to the timeseries data with a conflict to the meta attribute
    test_pd_df["meta"] = "foo"

    # check that initialising an instance with an extra-column `meta` raises
    msg = re.compile(r"Column name \['meta'\] is illegal for timeseries data.")
    with pytest.raises(ValueError, match=msg):
        IamDataFrame(test_pd_df)

    # check that recommended fix works
    df = IamDataFrame(test_pd_df, meta_1="meta")
    assert df.meta_1 == ["foo"]


def test_set_meta_with_column_conflict(test_df_year):
    # check that setting a `meta` column with a name conflict raises
    msg = "Column model already exists in `data`!"
    with pytest.raises(ValueError, match=msg):
        test_df_year.set_meta(name="model", meta="foo")

    msg = "Name meta is illegal for meta indicators!"
    with pytest.raises(ValueError, match=msg):
        test_df_year.set_meta(name="meta", meta="foo")


def test_print(test_df_year):
    """Assert that `print(IamDataFrame)` (and `info()`) returns as expected"""
    exp = "\n".join(
        [
            "<class 'pyam.core.IamDataFrame'>",
            "Index dimensions:",
            " * model    : model_a (1)",
            " * scenario : scen_a, scen_b (2)",
            "Timeseries data coordinates:",
            "   region   : World (1)",
            "   variable : Primary Energy, Primary Energy|Coal (2)",
            "   unit     : EJ/yr (1)",
            "   year     : 2005, 2010 (2)",
            "Meta indicators:",
            "   exclude (bool) False (1)",
            "   number (int64) 1, 2 (2)",
            "   string (object) foo, nan (2)",
        ]
    )
    obs = test_df_year.info()
    assert obs == exp


def test_print_empty(test_df_year):
    """Assert that `print(IamDataFrame)` (and `info()`) returns as expected"""
    exp = "\n".join(
        [
            "<class 'pyam.core.IamDataFrame'>",
            "Index dimensions:",
            " * model    : (0)",
            " * scenario : (0)",
            "Timeseries data coordinates:",
            "   region   : (0)",
            "   variable : (0)",
            "   unit     : (0)",
            "   year     : (0)",
            "Meta indicators:",
            "   exclude (bool) (0)",
            "   number (int64) (0)",
            "   string (object) (0)",
        ]
    )
    obs = test_df_year.filter(model="foo").info()
    assert obs == exp


def test_as_pandas(test_df):
    # test that `as_pandas()` returns the right columns
    df = test_df.copy()
    df.set_meta(["foo", "bar"], name="string")
    df.set_meta([1, 2], name="number")

    # merge all columns (default)
    obs = df.as_pandas()
    cols = ["string", "number"]
    assert all(i in obs.columns for i in cols)  # assert relevant columns exist

    exp = pd.concat([pd.DataFrame([["foo", 1]] * 4), pd.DataFrame([["bar", 2]] * 2)])
    npt.assert_array_equal(obs[cols], exp)  # assert meta columns are merged

    # merge only one column
    obs = df.as_pandas(["string"])
    assert "string" in obs.columns
    assert "number" not in obs.columns
    npt.assert_array_equal(obs["string"], ["foo"] * 4 + ["bar"] * 2)

    # do not merge any columns
    npt.assert_array_equal(df.as_pandas(False), df.data)


def test_empty_attribute(test_df_year):
    assert not test_df_year.empty
    assert test_df_year.filter(model="foo").empty


def test_equals(test_df_year):
    test_df_year.set_meta([1, 2], name="test")

    # assert that a copy (with changed index-sort) is equal
    df = test_df_year.copy()
    df.data = df.data.sort_values(by="value")
    assert test_df_year.equals(df)

    # assert that adding a new timeseries is not equal
    df = test_df_year.rename(variable={"Primary Energy": "foo"}, append=True)
    assert not test_df_year.equals(df)

    # assert that adding a new meta indicator is not equal
    df = test_df_year.copy()
    df.set_meta(["foo", " bar"], name="string")
    assert not test_df_year.equals(df)


def test_equals_raises(test_pd_df):
    df = IamDataFrame(test_pd_df)
    pytest.raises(ValueError, df.equals, test_pd_df)


def test_get_item(test_df):
    assert test_df["model"].unique() == ["model_a"]


def test_index(test_df_year):
    # assert that the correct index is shown for the IamDataFrame
    exp = pd.MultiIndex.from_arrays(
        [["model_a"] * 2, ["scen_a", "scen_b"]], names=["model", "scenario"]
    )
    pd.testing.assert_index_equal(test_df_year.index, exp)


def test_index_attributes(test_df):
    # assert that the index and data column attributes are set correcty
    assert test_df.model == ["model_a"]
    assert test_df.scenario == ["scen_a", "scen_b"]
    assert test_df.region == ["World"]
    assert test_df.variable == ["Primary Energy", "Primary Energy|Coal"]
    assert test_df.unit == ["EJ/yr"]
    if test_df.time_col == "year":
        assert test_df.year == [2005, 2010]
    else:
        assert test_df.time.equals(pd.Index(test_df.data.time.unique()))


def test_index_attributes_extra_col(test_pd_df):
    test_pd_df["subannual"] = ["summer", "summer", "winter"]
    df = IamDataFrame(test_pd_df)
    assert df.subannual == ["summer", "winter"]


def test_model(test_df):
    exp = pd.Series(data=["model_a"], name="model")
    pd.testing.assert_series_equal(test_df.models(), exp)


def test_scenario(test_df):
    exp = pd.Series(data=["scen_a", "scen_b"], name="scenario")
    pd.testing.assert_series_equal(test_df.scenarios(), exp)


def test_region(test_df):
    exp = pd.Series(data=["World"], name="region")
    pd.testing.assert_series_equal(test_df.regions(), exp)


def test_variable(test_df):
    exp = pd.Series(data=["Primary Energy", "Primary Energy|Coal"], name="variable")
    pd.testing.assert_series_equal(test_df.variables(), exp)


def test_variable_unit(test_df):
    exp = pd.DataFrame(
        [["Primary Energy", "EJ/yr"], ["Primary Energy|Coal", "EJ/yr"]],
        columns=["variable", "unit"],
    )
    pd.testing.assert_frame_equal(test_df.variables(include_units=True), exp)


def test_filter_empty_df():
    # test for issue seen in #254
    df = IamDataFrame(data=df_empty)
    obs = df.filter(variable="foo")
    assert len(obs) == 0


def test_filter_variable_and_depth(test_df):
    obs = list(test_df.filter(variable="*rimary*C*", level=0).variables())
    exp = ["Primary Energy|Coal"]
    assert obs == exp

    obs = list(test_df.filter(variable="*rimary*C*", level=1).variables())
    assert len(obs) == 0


def test_variable_depth_0_keep_false(test_df):
    obs = list(test_df.filter(level=0, keep=False)["variable"].unique())
    exp = ["Primary Energy|Coal"]
    assert obs == exp


def test_variable_depth_raises(test_df):
    pytest.raises(ValueError, test_df.filter, level="1/")


def test_filter_error_illegal_column(test_df):
    # filtering by column `foo` is not valid
    pytest.raises(ValueError, test_df.filter, foo="test")


def test_filter_error_keep(test_df):
    # string or non-starred dict was mis-interpreted as `keep` kwarg, see #253
    pytest.raises(ValueError, test_df.filter, model="foo", keep=1)
    pytest.raises(ValueError, test_df.filter, dict(model="foo"))


def test_filter_year(test_df):
    obs = test_df.filter(year=2005)
    if "year" in test_df.data.columns:
        npt.assert_equal(obs["year"].unique(), 2005)
    else:
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


@pytest.mark.parametrize("test_month", [6, "June", "Jun", "jun", ["Jun", "jun"]])
def test_filter_month(test_df, test_month):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `month` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            obs = test_df.filter(month=test_month)
    else:
        obs = test_df.filter(month=test_month)
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


@pytest.mark.parametrize("test_month", [6, "Jun", "jun", ["Jun", "jun"]])
def test_filter_year_month(test_df, test_month):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `month` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            obs = test_df.filter(year=2005, month=test_month)
    else:
        obs = test_df.filter(year=2005, month=test_month)
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


@pytest.mark.parametrize("test_day", [17, "Fri", "Friday", "friday", ["Fri", "fri"]])
def test_filter_day(test_df, test_day):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `day` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            obs = test_df.filter(day=test_day)
    else:
        obs = test_df.filter(day=test_day)
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


def test_filter_with_numpy_64_date_vals(test_df):
    dates = test_df[test_df.time_col].unique()
    key = "year" if test_df.time_col == "year" else "time"
    res_0 = test_df.filter(**{key: dates[0]})
    res = test_df.filter(**{key: dates})
    assert np.equal(res_0.data[res_0.time_col].values, dates[0]).all()
    assert res.equals(test_df)


@pytest.mark.parametrize("test_hour", [0, 12, [12, 13]])
def test_filter_hour(test_df, test_hour):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `hour` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            test_df.filter(hour=test_hour)
    else:
        obs = test_df.filter(hour=test_hour)
        test_hour = [test_hour] if isinstance(test_hour, int) else test_hour
        expected_rows = test_df.data["time"].apply(lambda x: x.hour).isin(test_hour)
        expected = test_df.data["time"].loc[expected_rows].unique()

        unique_time = np.array(obs["time"].unique(), dtype=np.datetime64)
        npt.assert_array_equal(unique_time, expected)


def test_filter_time_exact_match(test_df):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `year` requires integers!")
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(year=datetime.datetime(2005, 6, 17))
    else:
        obs = test_df.filter(time=datetime.datetime(2005, 6, 17))
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = np.array(obs["time"].unique(), dtype=np.datetime64)
        assert len(unique_time) == 1
        assert unique_time[0] == expected


def test_filter_time_range(test_df):
    error_msg = r".*datetime.datetime.*"
    with pytest.raises(TypeError, match=error_msg):
        test_df.filter(
            year=range(datetime.datetime(2000, 6, 17), datetime.datetime(2009, 6, 17))
        )


def test_filter_time_range_year(test_df):
    obs = test_df.filter(year=range(2000, 2008))

    if "year" in test_df.data.columns:
        unique_time = obs["year"].unique()
        expected = np.array([2005])
    else:
        unique_time = obs["time"].unique()
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )

    assert len(unique_time) == 1
    assert unique_time[0] == expected


@pytest.mark.parametrize("month_range", [range(1, 7), "Mar-Jun"])
def test_filter_time_range_month(test_df, month_range):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `month` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            obs = test_df.filter(month=month_range)
    else:
        obs = test_df.filter(month=month_range)
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )

        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


@pytest.mark.parametrize("month_range", [["Mar-Jun", "Nov-Feb"]])
def test_filter_time_range_round_the_clock_error(test_df, month_range):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `month` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            test_df.filter(month=month_range)
    else:
        error_msg = re.escape(
            "string ranges must lead to increasing integer ranges, "
            "Nov-Feb becomes [11, 2]"
        )
        with pytest.raises(ValueError, match=error_msg):
            test_df.filter(month=month_range)


@pytest.mark.parametrize("day_range", [range(14, 20), "Thu-Sat"])
def test_filter_time_range_day(test_df, day_range):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `day` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            test_df.filter(day=day_range)
    else:
        obs = test_df.filter(day=day_range)
        expected = np.array(
            pd.to_datetime("2005-06-17T00:00:00.0"), dtype=np.datetime64
        )
        unique_time = obs["time"].unique()
        assert len(unique_time) == 1
        assert unique_time[0] == expected


@pytest.mark.parametrize("hour_range", [range(10, 14)])
def test_filter_time_range_hour(test_df, hour_range):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `hour` not supported!")
        with pytest.raises(ValueError, match=error_msg):
            test_df.filter(hour=hour_range)
    else:
        obs = test_df.filter(hour=hour_range)

        expected_rows = test_df.data["time"].apply(lambda x: x.hour).isin(hour_range)
        expected = test_df.data["time"].loc[expected_rows].unique()

        unique_time = np.array(obs["time"].unique(), dtype=np.datetime64)
        npt.assert_array_equal(unique_time, expected)


def test_filter_time_no_match(test_df):
    if "year" in test_df.data.columns:
        error_msg = re.escape("Filter by `year` requires integers!")
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(year=datetime.datetime(2004, 6, 18))
    else:
        obs = test_df.filter(time=datetime.datetime(2004, 6, 18))
        assert obs.data.empty


def test_filter_time_not_datetime_error(test_df):
    if "year" in test_df.data.columns:
        with pytest.raises(ValueError, match=re.escape("`time`")):
            test_df.filter(time=datetime.datetime(2004, 6, 18))
    else:
        error_msg = re.escape("`time` can only be filtered by datetimes")
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(time=2005)
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(time="summer")


def test_filter_time_not_datetime_range_error(test_df):
    if "year" in test_df.data.columns:
        with pytest.raises(ValueError, match=re.escape("`time`")):
            test_df.filter(time=range(2000, 2008))
    else:
        error_msg = re.escape("`time` can only be filtered by datetimes")
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(time=range(2000, 2008))
        with pytest.raises(TypeError, match=error_msg):
            test_df.filter(time=["summer", "winter"])


def test_filter_year_with_time_col(test_pd_df):
    test_pd_df["time"] = ["summer", "summer", "winter"]
    df = IamDataFrame(test_pd_df)
    obs = df.filter(time="summer").timeseries()

    exp = test_pd_df.set_index(IAMC_IDX + ["time"])
    exp.columns = list(map(int, exp.columns))
    pd.testing.assert_frame_equal(obs, exp[0:2])


def test_filter_as_kwarg(test_df):
    _df = test_df.filter(variable="Primary Energy|Coal")
    assert _df.scenario == ["scen_a"]


def test_filter_keep_false(test_df):
    df = test_df.filter(variable="Primary Energy|Coal", year=2005, keep=False)
    obs = df.data[df.data.scenario == "scen_a"].value
    npt.assert_array_equal(obs, [1, 6, 3])


def test_filter_by_regexp(test_df):
    obs = test_df.filter(scenario="sce._a$", regexp=True)
    assert obs["scenario"].unique() == "scen_a"


def test_timeseries(test_df):
    dct = {
        "model": ["model_a"] * 2,
        "scenario": ["scen_a"] * 2,
        "years": [2005, 2010],
        "value": [1, 6],
    }
    exp = pd.DataFrame(dct).pivot_table(
        index=["model", "scenario"], columns=["years"], values="value"
    )
    obs = test_df.filter(scenario="scen_a", variable="Primary Energy").timeseries()
    npt.assert_array_equal(obs, exp)


def test_timeseries_empty_raises(test_df_year):
    """Calling `timeseries()` on an empty IamDataFrame raises"""
    _df = test_df_year.filter(model="foo")
    with pytest.raises(ValueError, match="This IamDataFrame is empty!"):
        _df.timeseries()


def test_timeseries_time_iamc_raises(test_df_time):
    """Calling `timeseries(iamc_index=True)` on a continuous-time IamDataFrame raises"""
    match = "Cannot use IAMC-index with continuous-time data format!"
    with pytest.raises(ValueError, match=match):
        test_df_time.timeseries(iamc_index=True)


def test_timeseries_to_iamc_index(test_pd_df, test_df_year):
    """Reducing timeseries() of an IamDataFrame with extra-columns to IAMC-index"""
    test_pd_df["foo"] = "bar"
    exta_col_df = IamDataFrame(test_pd_df)
    assert exta_col_df.extra_cols == ["foo"]

    # assert that reducing to IAMC-columns (dropping extra-columns) with timeseries()
    obs = exta_col_df.timeseries(iamc_index=True)
    exp = test_df_year.timeseries()
    pdt.assert_frame_equal(obs, exp)


def test_timeseries_to_iamc_index_duplicated_raises(test_pd_df):
    """Assert that using `timeseries(iamc_index=True)` raises if there are duplicates"""
    test_pd_df = pd.concat([test_pd_df, test_pd_df])
    # adding an extra-col creates a unique index
    test_pd_df["foo"] = ["bar", "bar", "bar", "baz", "baz", "baz"]
    exta_col_df = IamDataFrame(test_pd_df)
    assert exta_col_df.extra_cols == ["foo"]

    # dropping the extra-column by setting `iamc_index=True` creates duplicated index
    match = "Index contains duplicate entries, cannot reshape"
    with pytest.raises(ValueError, match=match):
        exta_col_df.timeseries(iamc_index=True)


def test_pivot_table(test_df):
    dct = {
        "model": ["model_a"] * 2,
        "scenario": ["scen_a"] * 2,
        "years": [2005, 2010],
        "value": [1, 6],
    }
    args = dict(index=["model", "scenario"], columns=["years"], values="value")
    exp = pd.DataFrame(dct).pivot_table(**args)
    obs = test_df.filter(scenario="scen_a", variable="Primary Energy").pivot_table(
        index=["model", "scenario"], columns=test_df.time_col, aggfunc="sum"
    )
    npt.assert_array_equal(obs, exp)


def test_pivot_table_raises(test_df):
    # using the same dimension in both index and columns raises an error
    pytest.raises(
        ValueError,
        test_df.pivot_table,
        index=["model", "scenario"] + [test_df.time_col],
        columns=test_df.time_col,
    )


def test_filter_meta_index(test_df):
    obs = test_df.filter(scenario="scen_b").meta.index
    exp = pd.MultiIndex(
        levels=[["model_a"], ["scen_b"]], codes=[[0], [0]], names=["model", "scenario"]
    )
    pd.testing.assert_index_equal(obs, exp)


def test_meta_idx(test_df):
    # assert that the `drop_duplicates()` in `_meta_idx()` returns right length
    assert len(_meta_idx(test_df.data)) == 2


def test_interpolate(test_pd_df):
    _df = test_pd_df.copy()
    _df["foo"] = ["bar", "baz", 2]  # add extra_col (check for #351)
    df = IamDataFrame(_df)
    df.interpolate(2007)
    obs = df.filter(year=2007).data["value"].reset_index(drop=True)
    exp = pd.Series([3, 1.5, 4], name="value")
    print(obs)
    print(exp)
    pd.testing.assert_series_equal(obs, exp)

    # redo the interpolation and check that no duplicates are added
    df.interpolate(2007)
    assert not df.filter().data.duplicated().any()

    # assert that extra_col does not have nan's (check for #351)
    assert all([True if isstr(i) else ~np.isnan(i) for i in df.data.foo])


def test_interpolate_time_exists(test_df_year):
    df = test_df_year
    df.interpolate(2005)
    obs = df.filter(year=2005).data["value"].reset_index(drop=True)
    exp = pd.Series([1.0, 0.5, 2.0], name="value")
    pd.testing.assert_series_equal(obs, exp)


def test_interpolate_with_list(test_df_year):
    df = test_df_year
    df.interpolate([2007, 2008])
    obs = df.filter(year=[2007, 2008]).data["value"].reset_index(drop=True)
    exp = pd.Series([3, 4, 1.5, 2, 4, 5], name="value")
    pd.testing.assert_series_equal(obs, exp)


def test_interpolate_with_numpy_list(test_df_year):
    test_df_year.interpolate(np.r_[2007 : 2008 + 1], inplace=True)
    obs = test_df_year.filter(year=[2007, 2008])._data.reset_index(drop=True)
    exp = pd.Series([3, 4, 1.5, 2, 4, 5], name="value")
    pd.testing.assert_series_equal(obs, exp)


def test_interpolate_full_example():
    cols = ["model_a", "scen_a", "World"]
    df = IamDataFrame(
        pd.DataFrame(
            [
                cols + ["all", "EJ/yr", 0, 1, 6.0, 10],
                cols + ["last", "EJ/yr", 0, 0.5, 3, np.nan],
                cols + ["first", "EJ/yr", 0, np.nan, 2, 7],
                cols + ["middle", "EJ/yr", 0, 1, np.nan, 7],
                cols + ["first two", "EJ/yr", 0, np.nan, np.nan, 7],
                cols + ["last two", "EJ/yr", 0, 1, np.nan, np.nan],
            ],
            columns=IAMC_IDX + [2000, 2005, 2010, 2017],
        )
    )
    exp = IamDataFrame(
        pd.DataFrame(
            [
                cols + ["all", "EJ/yr", 0, 1, 6.0, 7.142857, 10],
                cols + ["last", "EJ/yr", 0, 0.5, 3, np.nan, np.nan],
                cols + ["first", "EJ/yr", 0, 1.0, 2, 3.428571, 7],
                cols + ["middle", "EJ/yr", 0, 1, np.nan, 4.5, 7],
                cols + ["first two", "EJ/yr", 0, 2.058824, np.nan, 4.941176, 7],
                cols + ["last two", "EJ/yr", 0, 1, np.nan, np.nan, np.nan],
            ],
            columns=IAMC_IDX + [2000, 2005, 2010, 2012, 2017],
        )
    )
    obs = df.interpolate([2005, 2012], inplace=False)
    assert_iamframe_equal(obs, exp)


def test_interpolate_extra_cols():
    # check that interpolation with non-matching extra_cols has no effect
    # (#351)
    EXTRA_COL_DF = pd.DataFrame(
        [
            ["foo", 2005, 1],
            ["foo", 2010, 2],
            ["bar", 2005, 2],
            ["bar", 2010, 3],
        ],
        columns=["extra_col", "year", "value"],
    )
    df = IamDataFrame(
        EXTRA_COL_DF,
        model="model_a",
        scenario="scen_a",
        region="World",
        variable="Primary Energy",
        unit="EJ/yr",
    )

    # create a copy, interpolate
    df2 = df.copy()
    df2.interpolate(2007)

    # interpolate should work as if extra_cols is in the _data index
    assert_iamframe_equal(df, df2.filter(year=2007, keep=False))
    obs = df2.filter(year=2007)["value"]
    exp = pd.Series([2.4, 1.4], name="value")
    pd.testing.assert_series_equal(obs, exp)


def test_interpolate_datetimes(test_df):
    # test that interpolation also works with date-times.
    some_date = datetime.datetime(2007, 7, 1)
    if test_df.time_col == "year":
        pytest.raises(ValueError, test_df.interpolate, time=some_date)
    else:
        test_df.interpolate(some_date)
        obs = test_df.filter(time=some_date).data["value"].reset_index(drop=True)
        exp = pd.Series([3, 1.5, 4], name="value")
        pd.testing.assert_series_equal(obs, exp, check_less_precise=True)
        # redo the interpolation and check that no duplicates are added
        test_df.interpolate(some_date)
        assert not test_df.filter().data.duplicated().any()


def test_filter_by_bool(test_df):
    test_df.set_meta([True, False], name="exclude")
    obs = test_df.filter(exclude=True)
    assert obs["scenario"].unique() == "scen_a"


def test_filter_by_int(test_df):
    test_df.set_meta([1, 2], name="test")
    obs = test_df.filter(test=[1, 3])
    assert obs["scenario"].unique() == "scen_a"


def _r5_regions_exp(df):
    df = df.filter(region="World", keep=False)
    data = df.data
    data["region"] = "R5MAF"
    return sort_data(data, df._LONG_IDX)


def test_map_regions_r5(reg_df):
    obs = reg_df.map_regions("r5_region").data
    exp = _r5_regions_exp(reg_df)
    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_map_regions_r5_region_col(reg_df):
    df = reg_df.filter(model="MESSAGE-GLOBIOM")
    obs = df.map_regions("r5_region", region_col="MESSAGE-GLOBIOM.REGION").data
    exp = _r5_regions_exp(df)
    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_map_regions_r5_inplace(reg_df):
    exp = _r5_regions_exp(reg_df)
    reg_df.map_regions("r5_region", inplace=True)
    obs = reg_df.data
    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_map_regions_r5_agg(reg_df):
    columns = reg_df.data.columns
    obs = reg_df.map_regions("r5_region", agg="sum").data

    exp = _r5_regions_exp(reg_df)
    grp = list(columns)
    grp.remove("value")
    exp = exp.groupby(grp).sum().reset_index()
    exp = exp[columns]
    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_48a():
    # tests fix for #48 mapping many->few
    df = IamDataFrame(
        pd.DataFrame(
            [
                ["model", "scen", "SSD", "var", "unit", 1, 6],
                ["model", "scen", "SDN", "var", "unit", 2, 7],
                ["model", "scen1", "SSD", "var", "unit", 2, 7],
                ["model", "scen1", "SDN", "var", "unit", 2, 7],
            ],
            columns=["model", "scenario", "region", "variable", "unit", 2005, 2010],
        )
    )

    exp = _r5_regions_exp(df)
    columns = df.data.columns
    grp = list(columns)
    grp.remove("value")
    exp = exp.groupby(grp).sum().reset_index()
    exp = exp[columns]

    obs = df.map_regions("r5_region", region_col="iso", agg="sum").data

    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_48b():
    # tests fix for #48 mapping few->many

    exp = IamDataFrame(
        pd.DataFrame(
            [
                ["model", "scen", "SSD", "var", "unit", 1, 6],
                ["model", "scen", "SDN", "var", "unit", 1, 6],
                ["model", "scen1", "SSD", "var", "unit", 2, 7],
                ["model", "scen1", "SDN", "var", "unit", 2, 7],
            ],
            columns=["model", "scenario", "region", "variable", "unit", 2005, 2010],
        )
    ).data

    df = IamDataFrame(
        pd.DataFrame(
            [
                ["model", "scen", "R5MAF", "var", "unit", 1, 6],
                ["model", "scen1", "R5MAF", "var", "unit", 2, 7],
            ],
            columns=["model", "scenario", "region", "variable", "unit", 2005, 2010],
        )
    )
    obs = df.map_regions("iso", region_col="r5_region").data
    obs = sort_data(obs[obs.region.isin(["SSD", "SDN"])], df._LONG_IDX)

    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_48c():
    # tests fix for #48 mapping few->many, dropping duplicates

    exp = IamDataFrame(
        pd.DataFrame(
            [
                ["model", "scen", "AGO", "var", "unit", 1, 6],
                ["model", "scen1", "AGO", "var", "unit", 2, 7],
            ],
            columns=["model", "scenario", "region", "variable", "unit", 2005, 2010],
        )
    ).data.reset_index(drop=True)

    df = IamDataFrame(
        pd.DataFrame(
            [
                ["model", "scen", "R5MAF", "var", "unit", 1, 6],
                ["model", "scen1", "R5MAF", "var", "unit", 2, 7],
            ],
            columns=["model", "scenario", "region", "variable", "unit", 2005, 2010],
        )
    )
    obs = df.map_regions("iso", region_col="r5_region", remove_duplicates=True).data
    pd.testing.assert_frame_equal(obs, exp, check_index_type=False)


def test_pd_filter_by_meta(test_df):
    data = df_filter_by_meta_matching_idx.set_index(["model", "region"])

    test_df.set_meta([True, False], "boolean")
    test_df.set_meta(0, "integer")

    obs = filter_by_meta(data, test_df, join_meta=True, boolean=True, integer=None)
    obs = obs.reindex(columns=["scenario", "col", "boolean", "integer"])

    exp = data.iloc[0:2].copy()
    exp["boolean"] = True
    exp["integer"] = 0

    pd.testing.assert_frame_equal(obs, exp)


def test_pd_filter_by_meta_no_index(test_df):
    data = df_filter_by_meta_matching_idx

    test_df.set_meta([True, False], "boolean")
    test_df.set_meta(0, "int")

    obs = filter_by_meta(data, test_df, join_meta=True, boolean=True, int=None)
    obs = obs.reindex(columns=META_IDX + ["region", "col", "boolean", "int"])

    exp = data.iloc[0:2].copy()
    exp["boolean"] = True
    exp["int"] = 0

    pd.testing.assert_frame_equal(obs, exp)


def test_pd_filter_by_meta_nonmatching_index(test_df):
    data = df_filter_by_meta_nonmatching_idx
    test_df.set_meta(["a", "b"], "string")

    obs = filter_by_meta(data, test_df, join_meta=True, string="b")
    obs = obs.reindex(columns=["scenario", 2010, 2020, "string"])

    exp = data.iloc[2:3].copy()
    exp["string"] = "b"

    pd.testing.assert_frame_equal(obs, exp)


def test_pd_join_by_meta_nonmatching_index(test_df):
    data = df_filter_by_meta_nonmatching_idx
    test_df.set_meta(["a", "b"], "string")

    obs = filter_by_meta(data, test_df, join_meta=True, string=None)
    obs = obs.reindex(columns=["scenario", 2010, 2020, "string"])

    exp = data.copy()
    exp["string"] = [np.nan, np.nan, "b"]

    pd.testing.assert_frame_equal(obs.sort_index(level=1), exp)


def test_concat_fails_iterable(test_pd_df):
    """Check that calling concat with a non-iterable raises"""
    msg = "First argument must be an iterable, you passed an object of type '{}'!"

    for dfs, type_ in [(1, "int"), ("foo", "str"), (test_pd_df, "DataFrame")]:
        with pytest.raises(TypeError, match=msg.format(type_)):
            concat(dfs)


def test_concat_single_item(test_df):
    """Check that calling concat on a single-item list returns identical object"""
    obs = concat([test_df])
    assert_iamframe_equal(obs, test_df)


def test_concat_incompatible_time(test_df_year, test_df_time):
    """Check that calling concat with incompatible time formats raises"""
    match = re.escape("Items have incompatible time format ('year' vs. 'time')!")
    with pytest.raises(ValueError, match=match):
        concat([test_df_year, test_df_time])


def test_concat_incompatible_cols(test_pd_df):
    """Check that calling concat on a single-item list returns identical object"""
    df1 = IamDataFrame(test_pd_df)
    test_pd_df["extra_col"] = "foo"
    df2 = IamDataFrame(test_pd_df)

    match = "Items have incompatible timeseries data index dimensions!"
    with pytest.raises(ValueError, match=match):
        concat([df1, df2])


def test_concat(test_df):
    left = IamDataFrame(test_df.data.copy())
    right = left.data.copy()
    right["model"] = "not left"
    right = IamDataFrame(right)

    result = concat([left, right])

    obs = result.data.reset_index(drop=True)
    exp = pd.concat([left.data, right.data]).reset_index(drop=True)
    pd.testing.assert_frame_equal(obs, exp)

    obs = result.meta.reset_index(drop=True)
    exp = pd.concat([left.meta, right.meta]).reset_index(drop=True)
    pd.testing.assert_frame_equal(obs, exp)


def test_normalize(test_df):
    exp = test_df.data.copy().reset_index(drop=True)
    exp.loc[1::2, "value"] /= exp["value"][::2].values
    exp.loc[::2, "value"] /= exp["value"][::2].values
    if "year" in test_df.data:
        obs = test_df.normalize(year=2005).data.reset_index(drop=True)
    else:
        obs = test_df.normalize(time=datetime.datetime(2005, 6, 17)).data.reset_index(
            drop=True
        )
    pd.testing.assert_frame_equal(obs, exp)


def test_normalize_not_time(test_df):
    pytest.raises(ValueError, test_df.normalize, variable="foo")
    pytest.raises(ValueError, test_df.normalize, year=2015, variable="foo")


@pytest.mark.parametrize("inplace", [True, False])
def test_swap_time_to_year(test_df, inplace):
    if "year" in test_df.data:
        return  # year df not relevant for this test

    exp = test_df.data.copy()
    exp["year"] = exp["time"].apply(lambda x: x.year)
    exp = exp.drop("time", axis="columns")
    exp = IamDataFrame(exp)

    obs = test_df.swap_time_for_year(inplace=inplace)

    if inplace:
        assert obs is None
        obs = test_df

    assert compare(obs, exp).empty
    assert obs.year == [2005, 2010]
    with pytest.raises(AttributeError):
        obs.time


@pytest.mark.parametrize("inplace", [True, False])
def test_swap_time_to_year_errors(test_df, inplace):
    if "year" in test_df.data:
        with pytest.raises(ValueError):
            test_df.swap_time_for_year(inplace=inplace)
        return

    tdf = test_df.data.copy()
    tdf["time"] = tdf["time"].apply(lambda x: datetime.datetime(2005, x.month, x.day))

    with pytest.raises(ValueError):
        IamDataFrame(tdf).swap_time_for_year(inplace=inplace)
