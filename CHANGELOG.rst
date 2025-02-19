Change Log
===========

0.0.21
------
- Fixed chart EOY chart's `xticks` when charting data with 10+ years

0.0.20
------
- Misc bugfixes

0.0.19
------
- Cleaning up data before calculations (replaces inf/-inf/-0 with 0)
- Removed usage of `pandas.compound()` for future `pandas` version compatibility
- Auto conversion of price-to-returns and returns-to-data as needed

0.0.18
------
- Fixed issue when last date in data is in the past (issue #4)
- Fixed issue when data has less than 5 drawdown periods (issue #4)

0.0.17
------
- Fixed CAGR calculation for more accuracy
- Handles drawdowns better in live trading mode when currently in drawdown

0.0.16
------
- Handles no drawdowns better

0.0.15
------
- Better report formatting
- Code cleanup

0.0.14
------
- Fixed calculation for rolling sharpe and rolling sortino charts
- Nicer CSS when printing html reports

0.0.13
------
- Fixed non-compounded plots in reports when using ``compounded=False``

0.0.12
------
- Option to add ``compounded=True/False`` to reports (default is ``True``)

0.0.11
------
- Minor bug fixes

0.0.10
------
- Updated to install and use ``yfinance`` instead of ``fix_yahoo_finance``

0.0.09
------
- Added support for 3 modes (cumulative, compounded, fixed amount) in ``plots.earnings()`` and ``utils.make_portfolio()``
- Added two DataFrame utilities: ``df.curr_month()`` and ``df.date(date)``
- Misc bug fixes and code refactoring


0.0.08
------
- Better calculations for cagr, var, cvar, avg win/loss and payoff_ratio
- Removed unused param from ``to_plotly()``
- Added risk free param to ``log_returns()`` + renamed it to ``to_log_returns()``
- Misc bug fixes and code improvements

0.0.07
------
- Plots returns figure if ``show`` is set to False

0.0.06
------
- Minor bug fix

0.0.05
------
- Added ``plots.to_plotly()`` method
- Added Ulcer Index to metrics report
- Better returns/price detection
- Bug fixes and code refactoring

0.0.04
------
- Added ``pct_rank()`` method to stats
- Added ``multi_shift()`` method to utils

0.0.03
------
- Better VaR/cVaR calculation
- Fixed calculation of ``to_drawdown_series()``
- Changed VaR/cVaR default confidence to 95%
- Improved Sortino formula
- Fixed conversion of returns to prices (``to_prices()``)

0.0.02
------
- Initial release

0.0.01
------
- Pre-release placeholder
