# Next Release

- [#527](https://github.com/IAMconsortium/pyam/pull/527) Add an in-dataframe subtraction operation
- [#519](https://github.com/IAMconsortium/pyam/pull/519) Enable explicit `label` and fix for non-string items in plot legend 

# Release v0.11.0

## Highlights

- Easily order data in the line plot feature.
- Add a module for reading data from the [UNFCCC Data Inventory](https://di.unfccc.int/).
- Improved integration with any [IIASA Scenario Explorer instance](https://data.ece.iiasa.ac.at):
  read non-default versions from the connected database
  and obtain the "audit" info (scenario upload/edit timestamp and user).
- Performance improvements when aggregating or concatenating data.
- Refactor the entire code base to the [Black code style](https://black.readthedocs.io/).

## API changes

PR [#507](https://github.com/IAMconsortium/pyam/pull/507) harmonizes the behavior of
the `aggregate()` and `aggregate_region()` methods when performing "empty" aggregation,
i.e., no components exist to perform the requested aggregation.
In the new implementation, an empty IamDataFrame is returned if `append=False`
(instead of None).

PR [#488](https://github.com/IAMconsortium/pyam/pull/488) changes the default
behavior when initializing an IamDataFrame from xlsx: now, all sheets names
starting with `data` will be parsed for timeseries data.

## Individual updates

- [#510](https://github.com/IAMconsortium/pyam/pull/510) Improve performance of `pyam.concat()`
- [#508](https://github.com/IAMconsortium/pyam/pull/508) Bugfix for non-empty but invisible header and no rows in 'meta' sheet
- [#507](https://github.com/IAMconsortium/pyam/pull/507) Refactor aggregation-functions to increase performance
- [#502](https://github.com/IAMconsortium/pyam/pull/502) Switch to Black code style
- [#499](https://github.com/IAMconsortium/pyam/pull/499) Implement `order` feature in line plot 
- [#497](https://github.com/IAMconsortium/pyam/pull/497) Add a module for reading data from the UNFCCC Data Inventory 
- [#496](https://github.com/IAMconsortium/pyam/pull/496) Enable loading meta from csv file
- [#494](https://github.com/IAMconsortium/pyam/pull/494) Small performance improvements
- [#491](https://github.com/IAMconsortium/pyam/pull/491) Allow loading meta from file without exclude columns or with empty rows
- [#488](https://github.com/IAMconsortium/pyam/pull/488) Read all sheets starting with `data` when reading from xlsx
- [#486](https://github.com/IAMconsortium/pyam/pull/486) Enable reading non-default scenario versions from IIASA API
- [#483](https://github.com/IAMconsortium/pyam/pull/483) Add a tutorial for integration with R
- [#481](https://github.com/IAMconsortium/pyam/pull/481) Enable custom index columns
- [#477](https://github.com/IAMconsortium/pyam/pull/477) Add a nightly test suite
- [#476](https://github.com/IAMconsortium/pyam/pull/476) Add docstrings to plotting functions `df.plot.<kind>()`
- [#471](https://github.com/IAMconsortium/pyam/pull/471) Add a `iiasa.Connection.properties()` function to retrieve scenario audit data

# Release v0.10.0

## Highlights

 - Refactor the plotting library for better UX and consistency
   with **pandas**, **matplotlib** and **seaborn**.
 - Add a `sankey()` feature to the plotting library.
 - Rework the documentation and tutorials.

## API changes

Several PRs in this release changed the implementation of the plotting library 
for better UX and consistency with **pandas**, **matplotlib** and **seaborn**. 

Replace the calls to plotting features by the following:
 - `plot(...)` (or `plot(kind='line', ...)`) for `line_plot()`
 - `plot.stack(...)` for `stack_plot()`
 - `plot.bar()` for `bar_plot()`
 - ...

These PRs also add an `order` arg to the plotting functions, and the levels
are ordered based on the `run_control()['order']` dictionary by default.

## Individual updates

- [#464](https://github.com/IAMconsortium/pyam/pull/463) Add `order` arg to `stackplot()`
- [#466](https://github.com/IAMconsortium/pyam/pull/466) Add a `sankey()`function to create sankey diagrams
- [#475](https://github.com/IAMconsortium/pyam/pull/475) Add a scatter plot example to the gallery
- [#473](https://github.com/IAMconsortium/pyam/pull/473) Refactor to plotting API following pandas/matplotlib implementation
- [#472](https://github.com/IAMconsortium/pyam/pull/472) Add a `sankey()` example to the plotting gallery
- [#470](https://github.com/IAMconsortium/pyam/pull/470) Add two types of `order` arg to `barplot()`
- [#467](https://github.com/IAMconsortium/pyam/pull/467) Refactor the GAMS-pyam tutorial to use the gamstransfer module
- [#466](https://github.com/IAMconsortium/pyam/pull/466) Add a `sankey()` function to create sankey diagrams
- [#464](https://github.com/IAMconsortium/pyam/pull/464) Add `order` arg to `stackplot()`
- [#463](https://github.com/IAMconsortium/pyam/pull/463) Clarification of initialization-error message if file does not exist

# Release v0.9.0

## Highlights

 - Extend the data format to work with dimensionless variables
   (i.e., accept "empty" units).
 - Refactor the `interpolate()` feature to accept a list of years
   or `datetime` instances.
 - Add the list of authors/contributors to the docs.

## API changes

PR [#456](https://github.com/IAMconsortium/pyam/pull/456) changed the interface
of the `interpolate()` feature to do the operation inplace (previous behaviour)
or return a new instance (future default).
A deprecation warning is written if a user does not provide the arg `inplace`
to warn of the future change.

## Individual updates

- [#461](https://github.com/IAMconsortium/pyam/pull/461) Add list of authors to repo and docs pages
- [#459](https://github.com/IAMconsortium/pyam/pull/459) Add a `get_variable_components()` function to retrieve or join variable components
- [#458](https://github.com/IAMconsortium/pyam/pull/458) Enable `Path` for IamDataFrame initialization 
- [#456](https://github.com/IAMconsortium/pyam/pull/456) Speed up interpolation and support interpolation for multiple time-points
- [#454](https://github.com/IAMconsortium/pyam/pull/454) Enable dimensionless units and fix `info()` if IamDataFrame is empty
- [#451](https://github.com/IAMconsortium/pyam/pull/451) Fix unit conversions from C to CO2eq
- [#450](https://github.com/IAMconsortium/pyam/pull/450) Defer logging set-up to when the first logging message is generated
- [#445](https://github.com/IAMconsortium/pyam/pull/445) Prevent conflicts between attributes and data/meta columns
- [#444](https://github.com/IAMconsortium/pyam/pull/444) Use warnings module for deprecation warnings

# Release v0.8.0

## Highlights

- Add a `boxplot()` visualization feature to the plotting toolbox.
- Implement an API to read data from World Bank Open Data Catalogue.
- Write a tutorial illustrating how to read model results from a GAMS gdx file.
- Define `index`, `model`, `scenario`, ... attributes
  and show a summary of the index dimensions on `print()`.
- Refactor the timeseries data backend for improved performance.

## API changes

PR [#432](https://github.com/IAMconsortium/pyam/pull/432) added attributes to
access the list of (unique) items of each index dimension
(`model`, `scenario`, ...).
The PR also marked as deprecated the equivalent functions
(`models()`, `scenarios()`, ...). The new behaviour is closer
(though still different) to what a pandas user would expect. 

## Notes

PR [#420](https://github.com/IAMconsortium/pyam/pull/420) added
an object `IamDataFrame._data` to handle timeseries data internally. 
This is implemented as a `pandas.Series` (instead of the previous long-format
`pandas.DataFrame`) to improve performance.
The previous behaviour with `IamDataFrame.data` is maintained
via getter and setter functions.

## Individual updates

- [#440](https://github.com/IAMconsortium/pyam/pull/440) Add `boxplot()` visualization feature
- [#438](https://github.com/IAMconsortium/pyam/pull/438) Add an `index` attribute of model-scenario combinations
- [#437](https://github.com/IAMconsortium/pyam/pull/437) Improved test for appending mismatched timeseries
- [#436](https://github.com/IAMconsortium/pyam/pull/436) Raise an error with appending mismatching timeseries index dimensions
- [#432](https://github.com/IAMconsortium/pyam/pull/432) Add attributes to access index dimensions
- [#429](https://github.com/IAMconsortium/pyam/pull/429) Fix return type of `validate()` after data refactoring
- [#427](https://github.com/IAMconsortium/pyam/pull/427) Add an `info()` function and use in `print(IamDataFrame)`
- [#424](https://github.com/IAMconsortium/pyam/pull/424) Add a tutorial reading results from a GAMS model (via a gdx file).
- [#420](https://github.com/IAMconsortium/pyam/pull/420) Add a `_data` object (implemented as a pandas.Series) to handle timeseries data internally.
- [#418](https://github.com/IAMconsortium/pyam/pull/418) Read data from World Bank Open Data Catalogue as IamDataFrame.
- [#416](https://github.com/IAMconsortium/pyam/pull/416) Include `meta` in new IamDataFrames returned by aggregation functions.

# Release v0.7.0

## Highlights

- Add new features for aggregating and downscaling timeseries data.
- Update the plotting library for compatibility with the latest matplotlib release.
- Refactor the feature to read data directly from an IIASA scenario database API.
- Migrate the continuous-integration (CI) infrastructure
  from Travis & Appveyor to GitHub Actions
  and use CodeCov.io instead of coveralls.io for test coverage metrics.

## API changes

PR [#413](https://github.com/IAMconsortium/pyam/pull/413) changed the
return type of `pyam.read_iiasa()` and `pyam.iiasa.Connection.query()`
to an `IamDataFrame` (instead of a `pandas.DataFrame`)
and loads meta-indicators by default.

Also, the following functions were deprecated for package consistency: 
- `index()` replaces `scenario_list()` for an overview of all scenarios 
- `meta_columns` (attribute) replaces `available_metadata()`
- `meta()` replaces `metadata()`

PR [#402](https://github.com/IAMconsortium/pyam/pull/402) changed the default
behaviour of `as_pandas()` to include all columns of `meta` in the returned
dataframe, or only merge columns given by the renamed argument `meta_cols`. 
The feature to discover meta-columns from a dictionary was split out into
a utility function `pyam.plotting.mpl_args_to_meta_cols()`.

## Individual Updates

- [#413](https://github.com/IAMconsortium/pyam/pull/413) Refactor IIASA-connection-API and rework all related tests.
- [#412](https://github.com/IAMconsortium/pyam/pull/412) Add building the docs to GitHub Actions CI.
- [#411](https://github.com/IAMconsortium/pyam/pull/411) Add feature to pass an explicit weight dataframe to `downscale_region()`.
- [#410](https://github.com/IAMconsortium/pyam/pull/410) Activate tutorial tests on GitHub Actions CI (py3.8).
- [#409](https://github.com/IAMconsortium/pyam/pull/409) Remove travis and appveyor CI config.
- [#408](https://github.com/IAMconsortium/pyam/pull/408) Update badges on the docs page and readme.
- [#407](https://github.com/IAMconsortium/pyam/pull/407) Add Codecov to Github Actions CI.
- [#405](https://github.com/IAMconsortium/pyam/pull/405) Add ability for recursivley aggregating variables.
- [#402](https://github.com/IAMconsortium/pyam/pull/402) Refactor `as_pandas()` and docs for more consistent description of `meta`.
- [#401](https://github.com/IAMconsortium/pyam/pull/401) Read credentials for IIASA-API-Connection by default from known location.
- [#396](https://github.com/IAMconsortium/pyam/pull/396) Enable casting to `IamDataFrame` multiple times.
- [#394](https://github.com/IAMconsortium/pyam/pull/394) Switch CI to Github Actions.
- [#393](https://github.com/IAMconsortium/pyam/pull/393) Import ABC from collections.abc for Python 3.10 compatibility.
- [#380](https://github.com/IAMconsortium/pyam/pull/380) Add compatibility with latest matplotlib and py3.8

# Release v0.6.0

## Highlights

- Add feature to aggregate timeseries at sub-annual time resolution
- Refactored the iam-units utility from a submodule to a dependency
- Clean up documentation and dependencies

## Individual Updates

- [#386](https://github.com/IAMconsortium/pyam/pull/386) Enables unit conversion to apply to strings with "-equiv" in them. 
- [#384](https://github.com/IAMconsortium/pyam/pull/384) Add documentation for the pyam.iiasa.Connection class.
- [#382](https://github.com/IAMconsortium/pyam/pull/382) Streamline dependencies and implementation of xlsx-io
- [#373](https://github.com/IAMconsortium/pyam/pull/373) Extends the error message when initializing with duplicate rows.
- [#370](https://github.com/IAMconsortium/pyam/pull/370) Allowed filter to work with np.int64 years and np.datetime64 dates.  
- [#369](https://github.com/IAMconsortium/pyam/pull/369) `convert_unit()` supports GWP conversion of same GHG species without context, lower-case aliases for species symbols.
- [#361](https://github.com/IAMconsortium/pyam/pull/361) iam-units refactored from a Git submodule to a Python dependency of pyam.
- [#322](https://github.com/IAMconsortium/pyam/pull/322) Add feature to aggregate timeseries at sub-annual time resolution

# Release v0.5.0

## Highlights

- Improved feature for unit conversion
  using the [pint package](https://pint.readthedocs.io) and
  the [IAMconsortium/units](https://github.com/IAMconsortium/units) repository,
  providing out-of-the-box conversion of unit definitions commonly used
  in integrated assessment research and energy systems modelling;
  see [this tutorial](https://pyam-iamc.readthedocs.io/en/stable/tutorials/unit_conversion.html)
  for more information
- Increased support for operations on timeseries data with continuous-time
  resolution
- New tutorial for working with various input data formats;
  [take a look](https://pyam-iamc.readthedocs.io/en/stable/tutorials/data_table_formats.html)
- Rewrite and extension of the documentation pages for the API;
  [read the new docs](https://pyam-iamc.readthedocs.io/en/stable/api.html)!

## API changes

PR [#341](https://github.com/IAMconsortium/pyam/pull/341) changed
the API of `IamDataFrame.convert_unit()` from a dictionary to explicit kwargs
`current`, `to` and `factor` (now optional, using `pint` if not specified).

PR [#334](https://github.com/IAMconsortium/pyam/pull/334) changed the arguments
of `IamDataFrame.interpolate()` and `pyam.fill_series()` to `time`. It can still
be an integer (i.e., a year).

With PR [#337](https://github.com/IAMconsortium/pyam/pull/337), initializing
an IamDataFrame with `n/a` entries in columns other than `value` raises an error.

## Individual Updates

- [#354](https://github.com/IAMconsortium/pyam/pull/354) Fixes formatting of API parameter docstrings
- [#352](https://github.com/IAMconsortium/pyam/pull/352) Bugfix when using `interpolate()` on data with extra columns
- [#349](https://github.com/IAMconsortium/pyam/pull/349) Fixes an issue with checking that time columns are equal when appending IamDataFrames
- [#348](https://github.com/IAMconsortium/pyam/pull/348) Extend pages for API docs, clean up docstrings, and harmonize formatting
- [#347](https://github.com/IAMconsortium/pyam/pull/347) Enable contexts and custom UnitRegistry with unit conversion
- [#341](https://github.com/IAMconsortium/pyam/pull/341) Use `pint` and IIASA-ene-units repo for unit conversion
- [#339](https://github.com/IAMconsortium/pyam/pull/339) Add tutorial for dataframe format io
- [#337](https://github.com/IAMconsortium/pyam/pull/337) IamDataFrame to throw an error when initialized with n/a entries in columns other than `value`
- [#334](https://github.com/IAMconsortium/pyam/pull/334) Enable interpolate to work on datetimes

# Release v0.4.1

This is a patch release to enable compatibility with `pandas v1.0`.
It also adds experimental support of the frictionless `datapackage` format.

## Individual Updates

- [#324](https://github.com/IAMconsortium/pyam/pull/324) Enable compatibility with pandas v1.0
- [#323](https://github.com/IAMconsortium/pyam/pull/323) Support import/export of frictionless `datapackage` format

# Release v0.4.0

## Highlights

- New feature: downscale regional timeseries data to subregions using a proxy variable
- Improved features to support aggregation by sectors and regions: support weighted-average, min/max, etc.
  (including a reworked tutorial)
- Streamlined I/O: include `meta` table when reading from/writing to xlsx files
- Standardized logger behaviour

## API changes

PR [#305](https://github.com/IAMconsortium/pyam/pull/305) changed the default
behaviour of `aggregate_region()` regarding the treatment of components at the
region-level. To keep the previous behaviour, add `components=True`.

PR [#315](https://github.com/IAMconsortium/pyam/pull/314) changed the return
type of `aggregate[_region]()` to an `IamDataFrame` instance.
To keep the previous behaviour, add `timeseries()`.
The object returned by `[check_]aggregate[_region]()` now includes both the
actual and the expected value as a `pd.DataFrame` instance.
The function `check_internal_consistency()` now returns a concatenated dataframe
rather than a dictionary and also includes optional treatment of components
(see paragraph above). To keep the previous behaviour, add `components=True`.

## Individual Updates

- [#315](https://github.com/IAMconsortium/pyam/pull/315) Add `equals()` feature, change return types of `[check_]aggregate[_region]()`, rework aggregation tutorial
- [#314](https://github.com/IAMconsortium/pyam/pull/314) Update IPCC color scheme colors and add SSP-only colors
- [#313](https://github.com/IAMconsortium/pyam/pull/313) Add feature to `downscale` timeseries data to subregions using another variable as proxy
- [#312](https://github.com/IAMconsortium/pyam/pull/312) Allow passing list of variables to `aggregate` functions
- [#305](https://github.com/IAMconsortium/pyam/pull/305) Add `method` and `weight` options to the (region) aggregation functions
- [#302](https://github.com/IAMconsortium/pyam/pull/302) Rework the tutorials
- [#301](https://github.com/IAMconsortium/pyam/pull/301) Bugfix when using `to_excel()` with a `pd.ExcelWriter`
- [#297](https://github.com/IAMconsortium/pyam/pull/297) Add `empty` attribute, better error for `timeseries()` on empty dataframe
- [#295](https://github.com/IAMconsortium/pyam/pull/295) Include `meta` table when writing to or reading from `xlsx` files
- [#292](https://github.com/IAMconsortium/pyam/pull/292) Add warning message if `data` is empty at initialization (after formatting)
- [#288](https://github.com/IAMconsortium/pyam/pull/288) Put `pyam` logger in its own namespace (see [here](https://docs.python-guide.org/writing/logging/#logging-in-a-library>))
- [#285](https://github.com/IAMconsortium/pyam/pull/285) Add ability to fetch regions with synonyms from IXMP API

# Release v0.3.0

## Highlights

- Streamlined generation of quantitative metadata indicators from timeseries data using `set_meta_from_data()`
- Better support for accessing public and private IIASA scenario explorer databases via the REST API
- More extensive documentation of the `pyam` data model and the IAMC format
- Compatible with recent `pandas` v0.25

## Individual Updates

- [#277](https://github.com/IAMconsortium/pyam/pull/277) Restructure and extend the docs pages, switch to RTD-supported theme
- [#275](https://github.com/IAMconsortium/pyam/pull/275) Completely removes all features related to region plotting, notably `region_plot()` and `read_shapefile()`
- [#270](https://github.com/IAMconsortium/pyam/pull/270) Include variables with zeros in `stack_plot`  (see [#266](https://github.com/IAMconsortium/pyam/issues/266))
- [#269](https://github.com/IAMconsortium/pyam/pull/269) Ensure append doesn't accidentally swap indexes
- [#268](https://github.com/IAMconsortium/pyam/pull/268) Update `aggregate_region` so it can find variables below sub-cateogories too
- [#267](https://github.com/IAMconsortium/pyam/pull/267) Make clear error message if variable-region pair is missing when `check_aggregate_region` is called
- [#261](https://github.com/IAMconsortium/pyam/pull/261) Add a check that `keep` in `filter()` is a boolean
- [#254](https://github.com/IAMconsortium/pyam/pull/254) Hotfix for aggregating missing regions and filtering empty dataframes
- [#243](https://github.com/IAMconsortium/pyam/pull/243) Update `pyam.iiasa.Connection` to support all public and private database connections. DEPRECATED: the argument 'iamc15' has been deprecated in favor of names as queryable directly from the REST API.
- [#241](https://github.com/IAMconsortium/pyam/pull/241) Add `set_meta_from_data` feature
- [#236](https://github.com/IAMconsortium/pyam/pull/236) Add `swap_time_for_year` method and confirm datetime column is compatible with pyam features
- [#273](https://github.com/IAMconsortium/pyam/pull/273) Fix several issues accessing IXMP API (passing correct credentials, improve reliability for optional fields in result payload)

# Release v0.2.0

## Highlights

- the `filters` argument in `IamDataFrame.filter()` has been deprecated
- `pd.date_time` now has **experimental** supported for time-related columns
- plots now support the official IPCC scenario color palatte
- native support for putting legends outside of plot axes
- dataframes can now be initialized with default values, making reading raw
  datasets easier

## Individual Updates

- [#228](https://github.com/IAMconsortium/pyam/pull/228) Update development environment creation instructions and make pandas requirement more specific
- [#219](https://github.com/IAMconsortium/pyam/pull/219) Add ability to query metadata from iiasa data sources
- [#214](https://github.com/IAMconsortium/pyam/pull/214) Tidy up requirements specifications a little
- [#213](https://github.com/IAMconsortium/pyam/pull/213) Add support for IPCC colors, see the new tutorial "Using IPCC Color Palattes"
- [#212](https://github.com/IAMconsortium/pyam/pull/212) Now natively support reading R-style data frames with year columns like "X2015"
- [#207](https://github.com/IAMconsortium/pyam/pull/207) Add a `aggregate_region()` function to sum a variable from subregions and add components that are only defined at the region level
- [#202](https://github.com/IAMconsortium/pyam/pull/202) Extend the `df.rename()` function with a `check_duplicates (default True)` validation option
- [#201](https://github.com/IAMconsortium/pyam/pull/201) Added native support for legends outside of plots with `pyam.plotting.OUTSIDE_LEGEND` with a tutorial
- [#200](https://github.com/IAMconsortium/pyam/pull/200) Bugfix when providing `cmap`  and `color`  arguments to plotting functions
- [#199](https://github.com/IAMconsortium/pyam/pull/199) Initializing an `IamDataFrame` accepts kwargs to fill or create from the data any missing required columns
- [#198](https://github.com/IAMconsortium/pyam/pull/198) Update stack plot functionality and add aggregation tutorial. Also adds a `copy` method to `IamDataFrame`.
- [#197](https://github.com/IAMconsortium/pyam/pull/197) Added a `normalize` function that normalizes all data in a data frame to a specific time period.
- [#195](https://github.com/IAMconsortium/pyam/pull/195) Fix filtering for `time`, `day` and `hour` to use generic `pattern_match()` (if such a column exists) in 'year'-formmatted IamDataFrames
- [#192](https://github.com/IAMconsortium/pyam/pull/192) Extend `utils.find_depth()` to optionally return depth (as list of ints) rather than assert level tests
- [#190](https://github.com/IAMconsortium/pyam/pull/190) Add `concat()` function
- [#189](https://github.com/IAMconsortium/pyam/pull/189) Fix over-zealous `dropna()` in `scatter()`
- [#186](https://github.com/IAMconsortium/pyam/pull/186) Fix over-zealous `dropna()` in `line_plot()`, rework `as_pandas()` to (optionally) discover meta columns to be joined
- [#178](https://github.com/IAMconsortium/pyam/pull/178) Add a kwarg `append` to the function `rename()`, change behaviour of mapping to only apply to data where all given columns are matched
- [#177](https://github.com/IAMconsortium/pyam/pull/177) Modified formatting of time column on init to allow subclasses to avoid pandas limitation (https://stackoverflow.com/a/37226672)
- [#176](https://github.com/IAMconsortium/pyam/pull/176) Corrected title setting operation in line_plot function
- [#175](https://github.com/IAMconsortium/pyam/pull/175) Update link to tutorial in readme.md
- [#174](https://github.com/IAMconsortium/pyam/pull/174) Add a function `difference()` to compare two IamDataFrames
- [#171](https://github.com/IAMconsortium/pyam/pull/171) Fix a bug when reading from an `ixmp.TimeSeries` object, refactor to mitigate circular dependency
- [#162](https://github.com/IAMconsortium/pyam/pull/162) Add a function to sum and append timeseries components to an aggregate variable
- [#152](https://github.com/IAMconsortium/pyam/pull/152) Fix bug where scatter plots did not work with property metadata when using two variables (#136, #152)
- [#151](https://github.com/IAMconsortium/pyam/pull/151) Fix bug where excel files were not being written on Windows and MacOSX (#149)
- [#145](https://github.com/IAMconsortium/pyam/pull/145) Support full semantic and VCS-style versioning with `versioneer`
- [#132](https://github.com/IAMconsortium/pyam/pull/132) support time columns using the `datetime` format and additional `str` columns in `data`

# Release v0.1.2

- [#128](https://github.com/IAMconsortium/pyam/pull/128) add ability to directly read data from iiasa data sources
- [#120](https://github.com/IAMconsortium/pyam/pull/120) update install setup

# Release v0.1.0

- [#114](https://github.com/IAMconsortium/pyam/pull/114) extends `append()` such that data can be added to existing scenarios
- [#111](https://github.com/IAMconsortium/pyam/pull/111) extends `set_meta()` such that it requires a name (not None)
- [#109](https://github.com/IAMconsortium/pyam/pull/109) add ability to fill between and add data ranges in `line_plot()`
- [#104](https://github.com/IAMconsortium/pyam/pull/104) fixes a bug with timeseries utils functions, ensures that years are cast as integers
- [#101](https://github.com/IAMconsortium/pyam/pull/101) add function `cross_threshold()` to determine years where a timeseries crosses a given threshold
- [#98](https://github.com/IAMconsortium/pyam/pull/98) add a module to compute and format summary statistics for timeseries data (wrapper for `pd.describe()`
- [#95](https://github.com/IAMconsortium/pyam/pull/95) add a `scatter()` chart in the plotting library using metadata
- [#94](https://github.com/IAMconsortium/pyam/pull/94) `set_meta()` can take pd.DataFrame (with columns `['model', 'scenario']`) as `index` arg
- [#93](https://github.com/IAMconsortium/pyam/pull/93) IamDataFrame can be initilialzed from pd.DataFrame with index
- [#92](https://github.com/IAMconsortium/pyam/pull/92) Adding `$` to the pseudo-regexp syntax in `pattern_match()`, adds override option
- [#90](https://github.com/IAMconsortium/pyam/pull/90) Adding a function to `set_panel_label()` as part of the plotting library
- [#88](https://github.com/IAMconsortium/pyam/pull/88) Adding `check_aggregate_regions` and `check_internal_consistency` to help with database validation, especially for emissions users
- [#87](https://github.com/IAMconsortium/pyam/pull/87) Extending `rename()` to work with model and scenario names
- [#85](https://github.com/IAMconsortium/pyam/pull/85) Improved functionality for importing metadata and bugfix for filtering for strings if `nan` values exist in metadata
- [#83](https://github.com/IAMconsortium/pyam/pull/83) Extending `filter_by_meta()` to work with non-matching indices between `df` and `data
- [#81](https://github.com/IAMconsortium/pyam/pull/81) Bug-fix when using `set_meta()` with unnamed pd.Series and no `name` kwarg
- [#80](https://github.com/IAMconsortium/pyam/pull/80) Extend the pseudo-regexp syntax for filtering in `pattern_match()`
- [#73](https://github.com/IAMconsortium/pyam/pull/73) Adds ability to remove labels for markers, colors, or linestyles
- [#72](https://github.com/IAMconsortium/pyam/pull/72) line_plot now drops NaNs so that lines are fully plotted
- [#71](https://github.com/IAMconsortium/pyam/pull/71) Line plots `legend` keyword can now be a dictionary of legend arguments
- [#70](https://github.com/IAMconsortium/pyam/pull/70) Support reading of both SSP and RCP data files downloaded from the IIASA database.
- [#66](https://github.com/IAMconsortium/pyam/pull/66) Fixes a bug in the `interpolate()` function (duplication of data points if already defined)
- [#65](https://github.com/IAMconsortium/pyam/pull/65) Add a `filter_by_meta()` function to filter/join a pd.DataFrame with an IamDataFrame.meta table
