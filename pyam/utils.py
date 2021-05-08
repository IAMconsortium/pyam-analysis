from pathlib import Path
import itertools
import logging
import string
import six
import re
import datetime
import dateutil
import time

import numpy as np
import pandas as pd
from collections.abc import Iterable

try:
    import seaborn as sns
except ImportError:
    pass

logger = logging.getLogger(__name__)

# common indices
DEFAULT_META_INDEX = ["model", "scenario"]
META_IDX = ["model", "scenario"]
YEAR_IDX = ["model", "scenario", "region", "year"]
IAMC_IDX = ["model", "scenario", "region", "variable", "unit"]
SORT_IDX = ["model", "scenario", "variable", "year", "region"]
LONG_IDX = IAMC_IDX + ["year"]

# required columns
REQUIRED_COLS = ["region", "variable", "unit"]

# illegal terms for data/meta column names to prevent attribute conflicts
ILLEGAL_COLS = ["data", "meta"]

# dictionary to translate column count to Excel column names
NUMERIC_TO_STR = dict(
    zip(
        range(0, 702),
        [i for i in string.ascii_uppercase]
        + [
            "{}{}".format(i, j)
            for i, j in itertools.product(
                string.ascii_uppercase, string.ascii_uppercase
            )
        ],
    )
)

KNOWN_FUNCS = {
    "min": np.min,
    "max": np.max,
    "avg": np.mean,
    "mean": np.mean,
    "sum": np.sum,
}


def requires_package(pkg, msg, error_type=ImportError):
    """Decorator when a function requires an optional dependency

    Parameters
    ----------
    pkg : imported package object
    msg : string
        Message to show to user with error_type
    error_type : python error class
    """

    def _requires_package(func):
        def wrapper(*args, **kwargs):
            if pkg is None:
                raise error_type(msg)
            return func(*args, **kwargs)

        return wrapper

    return _requires_package


def isstr(x):
    """Returns True if x is a string"""
    return isinstance(x, six.string_types)


def isscalar(x):
    """Returns True if x is a scalar"""
    return not isinstance(x, Iterable) or isstr(x)


def islistable(x):
    """Returns True if x is a list but not a string"""
    return isinstance(x, Iterable) and not isstr(x)


def to_list(x):
    """Return x as a list"""
    return x if islistable(x) else [x]


def write_sheet(writer, name, df, index=False):
    """Write a pandas.DataFrame to an ExcelWriter

    The function applies formatting of the column width depending on maxwidth
    of values and column header

    Parameters
    ----------
    writer: pandas.ExcelWriter
        an instance of a :class:`pandas.ExcelWriter`
    name: string
        name of the sheet to be written
    df: pandas.DataFrame
        a :class:`pandas.DataFrame` to be written to the sheet
    index: boolean, default False
        should the index be written to the sheet
    """
    if index:
        df = df.reset_index()
    df.to_excel(writer, name, index=False)
    worksheet = writer.sheets[name]
    for i, col in enumerate(df.columns):
        if df.dtypes[col].name.startswith(("float", "int")):
            width = len(str(col)) + 2
        else:
            width = (
                max([df[col].map(lambda x: len(str(x or "None"))).max(), len(col)]) + 2
            )
        # this line fails if using an xlsx-engine other than openpyxl
        try:
            worksheet.column_dimensions[NUMERIC_TO_STR[i]].width = width
        except AttributeError:
            pass


def read_pandas(path, sheet_name="data*", *args, **kwargs):
    """Read a file and return a pandas.DataFrame"""
    if isinstance(path, Path) and path.suffix == ".csv":
        return pd.read_csv(path, *args, **kwargs)
    else:
        xl = pd.ExcelFile(path)
        sheet_names = pd.Series(xl.sheet_names)

        # reading multiple sheets
        if len(sheet_names) > 1:
            sheets = kwargs.pop("sheet_name", sheet_name)
            # apply pattern-matching for sheet names (use * as wildcard)
            sheets = sheet_names[pattern_match(sheet_names, values=sheets)]
            if sheets.empty:
                raise ValueError(f"No sheets {sheet_name} in file {path}!")

            df = pd.concat([xl.parse(s, *args, **kwargs) for s in sheets])

        # read single sheet (if only one exists in file) ignoring sheet name
        else:
            df = pd.read_excel(path, *args, **kwargs)

        # remove unnamed and empty columns, and rows were all values are nan
        def is_empty(name, s):
            if str(name).startswith("Unnamed: "):
                if len(s) == 0 or all(np.isnan(s)):
                    return True
            return False

        empty_cols = [c for c in df.columns if is_empty(c, df[c])]
        return df.drop(columns=empty_cols).dropna(axis=0, how="all")


def read_file(path, *args, **kwargs):
    """Read data from a file"""
    # extract kwargs that are intended for `format_data`
    format_kwargs = dict(index=kwargs.pop("index"))
    for c in [i for i in IAMC_IDX + ["year", "time", "value"] if i in kwargs]:
        format_kwargs[c] = kwargs.pop(c)
    return format_data(read_pandas(path, *args, **kwargs), **format_kwargs)


def format_data(df, index, **kwargs):
    """Convert a pandas.Dataframe or pandas.Series to the required format"""
    if isinstance(df, pd.Series):
        df.name = df.name or "value"
        df = df.to_frame()

    # check for R-style year columns, converting where necessary
    def convert_r_columns(c):
        try:
            first = c[0]
            second = c[1:]
            if first == "X":
                try:
                    #  bingo! was X2015 R-style, return the integer
                    return int(second)
                except:
                    # nope, not an int, fall down to final return statement
                    pass
        except:
            # not a string/iterable/etc, fall down to final return statement
            pass
        return c

    df.columns = df.columns.map(convert_r_columns)

    # if `value` is given but not `variable`,
    # melt value columns and use column name as `variable`
    if "value" in kwargs and "variable" not in kwargs:
        value = kwargs.pop("value")
        value = value if islistable(value) else [value]
        _df = df.set_index(list(set(df.columns) - set(value)))
        dfs = []
        for v in value:
            if v not in df.columns:
                raise ValueError("column `{}` does not exist!".format(v))
            vdf = _df[v].to_frame().rename(columns={v: "value"})
            vdf["variable"] = v
            dfs.append(vdf.reset_index())
        df = pd.concat(dfs).reset_index(drop=True)

    # otherwise, rename columns or concat to IAMC-style or do a fill-by-value
    for col, value in kwargs.items():
        if col in df:
            raise ValueError(
                "conflict of kwarg with column `{}` in dataframe!".format(col)
            )

        if isstr(value) and value in df:
            df.rename(columns={value: col}, inplace=True)
        elif islistable(value) and all([c in df.columns for c in value]):
            df[col] = df.apply(lambda x: concat_with_pipe(x, value), axis=1)
            df.drop(value, axis=1, inplace=True)
        elif isstr(value):
            df[col] = value
        else:
            raise ValueError("invalid argument for casting `{}: {}`".format(col, value))

    # all lower case
    str_cols = [c for c in df.columns if isstr(c)]
    df.rename(columns={c: str(c).lower() for c in str_cols}, inplace=True)

    if "notes" in df.columns:  # this came from the database
        logger.info("Ignoring notes column in dataframe")
        df.drop(columns="notes", inplace=True)
        col = df.columns[0]  # first column has database copyright notice
        df = df[~df[col].str.contains("database", case=False)]
        if "scenario" in df.columns and "model" not in df.columns:
            # model and scenario are jammed together in RCP data
            scen = df["scenario"]
            df.loc[:, "model"] = scen.apply(lambda s: s.split("-")[0].strip())
            df.loc[:, "scenario"] = scen.apply(
                lambda s: "-".join(s.split("-")[1:]).strip()
            )

    # reset the index if meaningful entries are included there
    if not list(df.index.names) == [None]:
        df.reset_index(inplace=True)

    # check that there is no column in the timeseries data with reserved names
    conflict_cols = [i for i in df.columns if i in ILLEGAL_COLS]
    if conflict_cols:
        msg = f"Column name {conflict_cols} is illegal for timeseries data.\n"
        _args = ", ".join([f"{i}_1='{i}'" for i in conflict_cols])
        msg += f"Use `IamDataFrame(..., {_args})` to rename at initialization."
        raise ValueError(msg)

    # check that index and required columns exist
    missing_index = [c for c in index if c not in df.columns]
    if missing_index:
        raise ValueError(f"Missing index columns `{missing_index}`!")

    missing_required_col = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_required_col:
        raise ValueError(f"Missing required columns `{missing_required_col}`!")

    # check whether data in wide format (IAMC) or long format (`value` column)
    if "value" in df.columns:
        # check if time column is given as `year` (int) or `time` (datetime)
        if "year" in df.columns:
            time_col = "year"
        elif "time" in df.columns:
            time_col = "time"
        else:
            msg = "Invalid time format, must have either `year` or `time`!"
            raise ValueError(msg)
        extra_cols = [
            c
            for c in df.columns
            if c not in index + REQUIRED_COLS + [time_col, "value"]
        ]
    else:
        # if in wide format, check if columns are years (int) or datetime
        cols = [c for c in df.columns if c not in index + REQUIRED_COLS]
        year_cols, time_cols, extra_cols = [], [], []
        for i in cols:
            try:
                int(i)  # this is a year
                year_cols.append(i)
            except (ValueError, TypeError):
                try:
                    dateutil.parser.parse(str(i))  # this is datetime
                    time_cols.append(i)
                except ValueError:
                    extra_cols.append(i)  # some other string
        if year_cols and not time_cols:
            time_col = "year"
            melt_cols = year_cols
        elif not year_cols and time_cols:
            time_col = "time"
            melt_cols = time_cols
        else:
            msg = "invalid column format, must be either years or `datetime`!"
            raise ValueError(msg)
        cols = index + REQUIRED_COLS + extra_cols
        df = pd.melt(
            df,
            id_vars=cols,
            var_name=time_col,
            value_vars=sorted(melt_cols),
            value_name="value",
        )

    # cast value column to numeric and drop nan
    df["value"] = df["value"].astype("float64")
    df.dropna(inplace=True, subset=["value"])

    # replace missing units by an empty string for user-friendly filtering
    df.loc[df.unit.isnull(), "unit"] = ""

    # verify that there are no nan's left (in columns)
    null_rows = df.isnull().values
    if null_rows.any():
        _raise_data_error("empty cells in `data`", df.loc[null_rows])

    # check for duplicates and empty data
    idx_cols = index + REQUIRED_COLS + [time_col] + extra_cols
    rows = df[idx_cols].duplicated()
    if any(rows):
        _raise_data_error("duplicate rows in `data`", df.loc[rows, idx_cols])

    if df.empty:
        logger.warning("Formatted data is empty!")

    df = format_time_col(sort_data(df, idx_cols), time_col)
    return df.set_index(idx_cols).value, index, time_col, extra_cols


def format_time_col(data, time_col):
    """Format time_col to int (year) or datetime"""
    if time_col == "year":
        data["year"] = to_int(pd.to_numeric(data["year"]))
    elif time_col == "time":
        data["time"] = pd.to_datetime(data["time"])
    return data


def _raise_data_error(msg, data):
    """Utils function to format error message from data formatting"""
    data = data.drop_duplicates()
    msg = f"{msg}:\n{data.head()}" + ("\n..." if len(data) > 5 else "")
    logger.error(msg)
    raise ValueError(msg)


def sort_data(data, cols):
    """Sort data rows and order columns by cols"""
    return data.sort_values(cols)[cols + ["value"]].reset_index(drop=True)


def merge_meta(left, right, ignore_conflict=False):
    """Merge two `meta` tables; raise if values are in conflict (optional)

    If conflicts are ignored, values in `left` take precedence over `right`.
    """
    left = left.copy()  # make a copy to not change the original object
    diff = right.index.difference(left.index)
    sect = right.index.intersection(left.index)

    # merge `right` into `left` for overlapping scenarios ( `sect`)
    if not sect.empty:
        # if not ignored, check that overlapping `meta` columns are equal
        if not ignore_conflict:
            cols = [i for i in right.columns if i in left.columns]
            if not left.loc[sect, cols].equals(right.loc[sect, cols]):
                conflict_idx = (
                    pd.concat([right.loc[sect, cols], left.loc[sect, cols]])
                    .drop_duplicates()
                    .index.drop_duplicates()
                )
                msg = "conflict in `meta` for scenarios {}".format(
                    [i for i in pd.DataFrame(index=conflict_idx).index]
                )
                raise ValueError(msg)
        # merge new columns
        cols = [i for i in right.columns if i not in left.columns]
        left = left.merge(
            right.loc[sect, cols], how="outer", left_index=True, right_index=True
        )

    # join `other.meta` for new scenarios (`diff`)
    if not diff.empty:
        left = left.append(right.loc[diff, :], sort=False)

    # remove any columns that are all-nan
    return left.dropna(axis=1, how="all")


def find_depth(data, s="", level=None):
    """Return or assert the depth (number of ``|``) of variables

    Parameters
    ----------
    data : str or list of strings
        IAMC-style variables
    s : str, default ''
        remove leading `s` from any variable in `data`
    level : int or str, default None
        if None, return depth (number of ``|``); else, return list of booleans
        whether depth satisfies the condition (equality if level is int,
        >= if ``.+``,  <= if ``.-``)
    """
    if isstr(data):
        return _find_depth([data], s, level)[0]

    return _find_depth(data, s, level)


def _find_depth(data, s="", level=None):
    """Internal implementation of `find_depth()´"""
    # remove wildcard as last character from string, escape regex characters
    _s = re.compile("^" + _escape_regexp(s.rstrip("*")))
    _p = re.compile("\\|")

    # find depth
    def _count_pipes(val):
        return len(_p.findall(re.sub(_s, "", val))) if _s.match(val) else None

    n_pipes = map(_count_pipes, to_list(data))

    # if no level test is specified, return the depth as (list of) int
    if level is None:
        return list(n_pipes)

    # if `level` is given, set function for finding depth level =, >=, <= |s
    if not isstr(level):
        test = lambda x: level == x if x is not None else False
    elif level[-1] == "-":
        level = int(level[:-1])
        test = lambda x: level >= x if x is not None else False
    elif level[-1] == "+":
        level = int(level[:-1])
        test = lambda x: level <= x if x is not None else False
    else:
        raise ValueError("Unknown level type: `{}`".format(level))

    return list(map(test, n_pipes))


def pattern_match(
    data, values, level=None, regexp=False, has_nan=False, return_codes=False
):
    """Return list where data matches values

    The function matches model/scenario names, variables, regions
    and meta columns to pseudo-regex (if `regexp == False`)
    for filtering (str, int, bool)
    """
    codes = []
    matches = np.zeros(len(data), dtype=bool)
    values = values if islistable(values) else [values]

    # issue (#40) with string-to-nan comparison, replace nan by empty string
    _data = data.fillna("") if has_nan else data

    for s in values:
        if return_codes and isinstance(data, pd.Index):
            try:
                codes.append(data.get_loc(s))
                continue
            except KeyError:
                pass

        if isstr(s):
            pattern = re.compile(_escape_regexp(s) + "$" if not regexp else s)
            depth = True if level is None else find_depth(_data, s, level)
            matches |= data.str.match(pattern) & depth
        else:
            matches = np.logical_or(matches, data == s)

    if return_codes:
        codes.extend(np.where(matches)[0])
        return codes

    return matches


def _escape_regexp(s):
    """Escape characters with specific regexp use"""
    return (
        str(s)
        .replace("|", "\\|")
        .replace(".", "\.")  # `.` has to be replaced before `*`
        .replace("*", ".*")
        .replace("+", "\+")
        .replace("(", "\(")
        .replace(")", "\)")
        .replace("$", "\\$")
    )


def years_match(data, years):
    """Return rows where data matches year"""
    years = [years] if (isinstance(years, (int, np.int64))) else years
    dt = (datetime.datetime, np.datetime64)
    if isinstance(years, dt) or isinstance(years[0], dt):
        error_msg = "Filter by `year` requires integers!"
        raise TypeError(error_msg)
    return np.isin(data, years)


def month_match(data, months):
    """Return rows where data matches months"""
    return time_match(data, months, ["%b", "%B"], "tm_mon", "months")


def day_match(data, days):
    """Return rows where data matches days"""
    return time_match(data, days, ["%a", "%A"], "tm_wday", "days")


def hour_match(data, hours):
    """Return rows where data matches hours"""
    hours = [hours] if isinstance(hours, int) else hours
    return np.isin(data, hours)


def time_match(data, times, conv_codes, strptime_attr, name):
    """Return rows where data matches a timestamp"""

    def conv_strs(strs_to_convert, conv_codes, name):
        for conv_code in conv_codes:
            try:
                res = [
                    getattr(time.strptime(t, conv_code), strptime_attr)
                    for t in strs_to_convert
                ]
                break
            except ValueError:
                continue

        try:
            return res
        except NameError:
            raise ValueError("Could not convert {} to integer".format(name))

    times = [times] if isinstance(times, (int, str)) else times
    if isinstance(times[0], str):
        to_delete = []
        to_append = []
        for i, timeset in enumerate(times):
            if "-" in timeset:
                ints = conv_strs(timeset.split("-"), conv_codes, name)
                if ints[0] > ints[1]:
                    error_msg = (
                        "string ranges must lead to increasing integer ranges,"
                        " {} becomes {}".format(timeset, ints)
                    )
                    raise ValueError(error_msg)

                # + 1 to include last month
                to_append += [j for j in range(ints[0], ints[1] + 1)]
                to_delete.append(i)

        for i in to_delete:
            del times[i]

        times = conv_strs(times, conv_codes, name)
        times += to_append

    return np.isin(data, times)


def datetime_match(data, dts):
    """Matching of datetimes in time columns for data filtering"""
    dts = dts if islistable(dts) else [dts]
    if any([not (isinstance(i, (datetime.datetime, np.datetime64))) for i in dts]):
        error_msg = "`time` can only be filtered by datetimes and datetime64s"
        raise TypeError(error_msg)
    return data.isin(dts).values


def print_list(x, n):
    """Return a printable string of a list shortened to n characters"""
    # if list is empty, only write count
    if len(x) == 0:
        return "(0)"

    # write number of elements, subtract count added at end from line width
    x = [i if i != "" else "''" for i in map(str, x)]
    count = f" ({len(x)})"
    n -= len(count)

    # if not enough space to write first item, write shortest sensible line
    if len(x[0]) > n - 5:
        return "..." + count

    # if only one item in list
    if len(x) == 1:
        return f"{x[0]} (1)"

    # add first item
    lst = f"{x[0]}, "
    n -= len(lst)

    # if possible, add last item before number of elements
    if len(x[-1]) + 4 > n:
        return lst + "..." + count
    else:
        count = f"{x[-1]}{count}"
        n -= len({x[-1]}) + 3

    # iterate over remaining entries until line is full
    for i in x[1:-1]:
        if len(i) + 6 <= n:
            lst += f"{i}, "
            n -= len(i) + 2
        else:
            lst += "... "
            break

    return lst + count


def to_int(x, index=False):
    """Formatting series or timeseries columns to int and checking validity

    If `index=False`, the function works on the :class:`pandas.Series` x;
    else, the function casts the index of x to int and returns x with new index
    """
    _x = x.index if index else x
    cols = list(map(int, _x))
    error = _x[cols != _x]
    if not error.empty:
        raise ValueError("invalid values `{}`".format(list(error)))
    if index:
        x.index = cols
        return x
    else:
        return _x


def concat_with_pipe(x, cols=None):
    """Concatenate a pandas.Series x using ``|``, drop None or numpy.nan"""
    cols = cols or x.index
    return "|".join([x[i] for i in cols if x[i] not in [None, np.nan]])


def reduce_hierarchy(x, depth):
    """Reduce the hierarchy (indicated by ``|``) of x to the specified depth"""
    _x = x.split("|")
    depth = len(_x) + depth - 1 if depth < 0 else depth
    return "|".join(_x[0 : (depth + 1)])


def get_variable_components(x, level, join=False):
    """Return components for requested level in a list or join these in a str.

    Parameters
    ----------
    x : str
        Uses ``|`` to separate the components of the variable.
    level : int or list of int
        Position of the component.
    join : bool or str, optional
        If True, IAMC-style (``|``) is used as separator for joined components.
    """
    _x = x.split("|")
    if join is False:
        return [_x[i] for i in level] if islistable(level) else _x[level]
    else:
        level = [level] if type(level) == int else level
        join = "|" if join is True else join
        return join.join([_x[i] for i in level])


def s(n):
    """Return an s if n!=1 for nicer formatting of log messages"""
    return "s" if n != 1 else ""
