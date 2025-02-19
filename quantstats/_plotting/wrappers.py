#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Quantreturns: Portfolio analytics for quants
# https://github.com/ranaroussi/quantreturns
#
# Copyright 2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings
import matplotlib.pyplot as _plt
from matplotlib.ticker import (
    StrMethodFormatter as _StrMethodFormatter,
    FuncFormatter as _FuncFormatter
)

import numpy as _np
from pandas import DataFrame as _df
import seaborn as _sns

from .. import (
    stats as _stats, utils as _utils,
)

from . import core as _core


_FLATUI_COLORS = ["#fedd78", "#348dc1", "#af4b64",
                  "#4fa487", "#9b59b6", "#808080"]
_GRAYSCALE_COLORS = (len(_FLATUI_COLORS) * ['black']) + ['white']

_HAS_PLOTLY = False
try:
    import plotly
    _HAS_PLOTLY = True
except ImportError:
    pass


def to_plotly(fig, title=""):
    if not _HAS_PLOTLY:
        return fig
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig = plotly.tools.mpl_to_plotly(fig)
        return plotly.plotly.iplot(fig, filename='quantstats-plot',
                                   overwrite=True)


def snapshot(returns, grayscale=False, figsize=(10, 8),
             title='Portfolio Summary', fontname='Arial', lw=1.5,
             mode="comp", subtitle=True, savefig=None, show=True):

    colors = _GRAYSCALE_COLORS if grayscale else _FLATUI_COLORS

    returns = _utils.make_portfolio(returns, 1, mode).pct_change().fillna(0)

    if figsize is None:
        size = list(_plt.gcf().get_size_inches())
        figsize = (size[0], size[0]*.75)

    fig, axes = _plt.subplots(3, 1, sharex=True,
                              figsize=figsize,
                              gridspec_kw={'height_ratios': [3, 1, 1]})

    fig.suptitle(title, fontsize=14, y=.995,
                 fontname=fontname, fontweight='bold', color='black')

    fig.set_facecolor('white')

    if subtitle:
        axes[0].set_title("\n%s - %s ;  Sharpe: %.2f                      " % (
            returns.index.date[:1][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y'),
            _stats.sharpe(returns)
        ), fontsize=12, color='gray')

    axes[0].set_ylabel('Cumulative Return', fontname=fontname,
                       fontweight='bold', fontsize=12)
    axes[0].plot(returns.cumsum() * 100, color=colors[1],
                 lw=1 if grayscale else lw, zorder=1)
    axes[0].axhline(0, color='silver', lw=1, zorder=0)

    dd = _stats.to_drawdown_series(returns) * 100
    ddmin = _utils._round_to_closest(abs(dd.min()), 5)
    ddmin_ticks = 5
    if ddmin > 50:
        ddmin_ticks = ddmin / 4
    elif ddmin > 20:
        ddmin_ticks = ddmin / 3
    ddmin_ticks = int(_utils._round_to_closest(ddmin_ticks, 5))

    # ddmin_ticks = int(_utils._round_to_closest(ddmin, 5))
    axes[1].set_ylabel('Drawdown', fontname=fontname,
                       fontweight='bold', fontsize=12)
    axes[1].set_yticks(_np.arange(-ddmin, 0, step=ddmin_ticks))
    axes[1].plot(dd, color=colors[2], lw=1 if grayscale else 1, zorder=1)
    axes[1].axhline(0, color='silver', lw=1, zorder=0)
    if not grayscale:
        axes[1].fill_between(dd.index, 0, dd, color=colors[2], alpha=.1)

    axes[2].set_ylabel('Daily Return', fontname=fontname,
                       fontweight='bold', fontsize=12)
    axes[2].plot(returns * 100, color=colors[0], lw=0.5, zorder=1)
    axes[2].axhline(0, color='silver', lw=1, zorder=0)
    axes[2].axhline(0, color=colors[-1], linestyle='--', lw=1, zorder=2)

    retmax = _utils._round_to_closest(returns.max() * 100, 5)
    retmin = _utils._round_to_closest(returns.min() * 100, 5)
    retdiff = (retmax - retmin)
    steps = 5
    if retdiff > 50:
        steps = retdiff / 5
    elif retdiff > 30:
        steps = retdiff / 4
    steps = int(_utils._round_to_closest(steps, 5))
    axes[2].set_yticks(_np.arange(retmin, retmax, step=steps))

    for ax in axes:
        ax.set_facecolor('white')
        ax.yaxis.set_label_coords(-.1, .5)
        ax.yaxis.set_major_formatter(_StrMethodFormatter('{x:,.0f}%'))

    _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    fig.autofmt_xdate()

    try:
        _plt.subplots_adjust(hspace=0)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)

    if show:
        _plt.show(fig)

    _plt.close()

    if not show:
        return fig


def earnings(returns, start_balance=1e5, mode="comp",
             grayscale=False, figsize=(10, 6),
             title='Portfolio Earnings',
             fontname='Arial', lw=1.5,
             subtitle=True, savefig=None, show=True):

    colors = _GRAYSCALE_COLORS if grayscale else _FLATUI_COLORS
    alpha = .5 if grayscale else .8

    returns = _utils.make_portfolio(returns, start_balance, mode)

    if figsize is None:
        size = list(_plt.gcf().get_size_inches())
        figsize = (size[0], size[0]*.55)

    fig, ax = _plt.subplots(figsize=figsize)
    fig.suptitle(title, fontsize=14, y=.995,
                 fontname=fontname, fontweight='bold', color='black')

    if subtitle:
        ax.set_title("\n%s - %s ;  P&L: %s (%s)                " % (
            returns.index.date[1:2][0].strftime('%e %b \'%y'),
            returns.index.date[-1:][0].strftime('%e %b \'%y'),
            _utils._score_str("${:,}".format(
                round(returns.values[-1]-returns.values[0], 2))),
            _utils._score_str("{:,}%".format(
                round((returns.values[-1]/returns.values[0]-1)*100, 2)))
        ), fontsize=12, color='gray')

    mx = returns.max()
    returns_max = returns[returns == mx]
    ix = returns_max[~_np.isnan(returns_max)].index[0]
    returns_max = _np.where(returns.index == ix, mx, _np.nan)

    ax.plot(returns.index, returns_max, marker='o', lw=0,
            alpha=alpha, markersize=12, color=colors[0])
    ax.plot(returns.index, returns, color=colors[1],
            lw=1 if grayscale else lw)

    ax.set_ylabel('Value of  ${:,.0f}'.format(start_balance),
                  fontname=fontname, fontweight='bold', fontsize=12)

    ax.yaxis.set_major_formatter(_FuncFormatter(_core.format_cur_axis))
    ax.yaxis.set_label_coords(-.1, .5)

    fig.set_facecolor('white')
    ax.set_facecolor('white')
    fig.autofmt_xdate()

    try:
        _plt.subplots_adjust(hspace=0)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)

    if show:
        _plt.show(fig)

    _plt.close()

    if not show:
        return fig


def returns(returns, benchmark=None,
            grayscale=False, figsize=(10, 6),
            fontname='Arial', lw=1.5,
            match_volatility=False, compound=True, cumulative=True,
            resample=None, ylabel="Cumulative Returns",
            subtitle=True, savefig=None, show=True):

    title = 'Cumulative Returns' if compound else 'Returns'
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += ' vs %s' % benchmark.upper()
        else:
            title += ' vs Benchmark'
        if match_volatility:
            title += ' (Volatility Matched)'

    returns = _utils._prepare_returns(returns)
    benchmark = _utils._prepare_benchmark(benchmark, returns.index)

    _core.plot_timeseries(returns, benchmark, title,
                          ylabel=ylabel,
                          match_volatility=match_volatility,
                          log_scale=False,
                          resample=resample,
                          compound=compound,
                          cumulative=cumulative,
                          lw=lw,
                          figsize=figsize,
                          fontname=fontname,
                          grayscale=grayscale,
                          subtitle=subtitle, savefig=savefig, show=show)


def log_returns(returns, benchmark=None,
                grayscale=False, figsize=(10, 5),
                fontname='Arial', lw=1.5,
                match_volatility=False, compound=True, cumulative=True,
                resample=None, ylabel="Cumulative Returns",
                subtitle=True, savefig=None, show=True):

    title = 'Cumulative Returns' if compound else 'Returns'
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += ' vs %s (Log Scaled' % benchmark.upper()
        else:
            title += ' vs Benchmark (Log Scaled'
        if match_volatility:
            title += ', Volatility Matched'
    else:
        title += ' (Log Scaled'
    title += ')'

    returns = _utils._prepare_returns(returns)
    benchmark = _utils._prepare_benchmark(benchmark, returns.index)

    _core.plot_timeseries(returns, benchmark, title,
                          ylabel=ylabel,
                          match_volatility=match_volatility,
                          log_scale=True,
                          resample=resample,
                          compound=compound,
                          cumulative=cumulative,
                          lw=lw,
                          figsize=figsize,
                          fontname=fontname,
                          grayscale=grayscale,
                          subtitle=subtitle, savefig=savefig, show=show)


def daily_returns(returns,
                  grayscale=False, figsize=(10, 4),
                  fontname='Arial', lw=0.5,
                  log_scale=False, ylabel="Returns",
                  subtitle=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns)
    _core.plot_timeseries(returns, None, 'Daily Returns',
                          ylabel=ylabel,
                          match_volatility=False,
                          log_scale=log_scale,
                          resample='D',
                          compound=False,
                          lw=lw,
                          figsize=figsize,
                          fontname=fontname,
                          grayscale=grayscale,
                          subtitle=subtitle, savefig=savefig, show=show)


def yearly_returns(returns, benchmark=None,
                   fontname='Arial', grayscale=False,
                   hline=None, hlw=None,
                   hlcolor="red", hllabel="",
                   match_volatility=False,
                   log_scale=False, figsize=(10, 5), ylabel=True,
                   subtitle=True, compounded=True,
                   savefig=None, show=True):

    title = 'EOY Returns'
    if benchmark is not None:
        title += '  vs Benchmark'
        benchmark = _utils._prepare_benchmark(
            benchmark, returns.index).resample('A').apply(
                _stats.compsum).resample('A').last()

    returns = _utils._prepare_returns(returns).resample('A')
    if compounded:
        returns = returns.apply(_stats.compsum)
    else:
        returns = returns.apply(_df.cumsum)
    returns = returns.resample('A').last()

    _core.plot_returns_bars(returns, benchmark,
                            hline=returns.mean(),
                            hlw=1.5,
                            hllabel="",
                            match_volatility=False,
                            log_scale=False,
                            resample=None,
                            title=title,
                            figsize=figsize,
                            grayscale=grayscale,
                            ylabel=ylabel,
                            subtitle=subtitle, savefig=savefig, show=show)


def distribution(returns, fontname='Arial', grayscale=False, ylabel=True,
                 figsize=(10, 6), subtitle=True, compounded=True,
                 savefig=None, show=True):
    returns = _utils._prepare_returns(returns)
    _core.plot_distribution(returns,
                            fontname=fontname,
                            grayscale=grayscale,
                            figsize=figsize,
                            ylabel=ylabel,
                            subtitle=subtitle,
                            compounded=compounded,
                            savefig=savefig, show=show)


def histogram(returns, resample='M', fontname='Arial',
              grayscale=False, figsize=(10, 5), ylabel=True,
              subtitle=True, compounded=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns)
    if resample == 'W':
        title = "Weekly "
    elif resample == 'M':
        title = "Monthly "
    elif resample == 'Q':
        title = "Quarterly "
    elif resample == 'A':
        title = "Annual "
    else:
        title = ""

    return _core.plot_histogram(returns,
                                resample=resample,
                                grayscale=grayscale,
                                fontname=fontname,
                                title="Distribution of %sReturns" % title,
                                figsize=figsize,
                                ylabel=ylabel,
                                subtitle=subtitle,
                                compounded=compounded,
                                savefig=savefig, show=show)


def drawdown(returns, grayscale=False, figsize=(10, 5),
             fontname='Arial', lw=1, log_scale=False,
             match_volatility=False, compound=True, ylabel="Drawdown",
             resample=None, subtitle=True, savefig=None, show=True):

    dd = _stats.to_drawdown_series(returns)

    _core.plot_timeseries(dd, title='Underwater Plot',
                          hline=dd.mean(), hlw=2, hllabel="Average",
                          returns_label="Drawdown",
                          compound=False, match_volatility=False,
                          log_scale=log_scale, resample=None,
                          fill=True, lw=lw, figsize=figsize,
                          ylabel=ylabel,
                          fontname=fontname, grayscale=grayscale,
                          subtitle=subtitle,
                          savefig=savefig, show=show)


def drawdowns_periods(returns, periods=5, lw=1.5, log_scale=False,
                      fontname='Arial', grayscale=False, figsize=(10, 5),
                      ylabel=True, subtitle=True, compounded=True,
                      savefig=None, show=True):
    returns = _utils._prepare_returns(returns)
    _core.plot_longest_drawdowns(returns,
                                 periods=periods,
                                 lw=lw,
                                 fontname=fontname,
                                 grayscale=grayscale,
                                 figsize=figsize,
                                 ylabel=ylabel,
                                 subtitle=subtitle,
                                 compounded=compounded,
                                 savefig=savefig, show=show)


def rolling_beta(returns, benchmark,
                 window1=126, window1_label="6-Months",
                 window2=252, window2_label="12-Months",
                 lw=1.5, fontname='Arial', grayscale=False,
                 figsize=(10, 3), ylabel=True,
                 subtitle=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns)
    benchmark = _utils._prepare_benchmark(benchmark, returns.index)

    _core.plot_rolling_beta(returns, benchmark,
                            window1=window1, window1_label=window1_label,
                            window2=window2, window2_label=window2_label,
                            title="Rolling Beta to Benchmark",
                            fontname=fontname,
                            grayscale=grayscale,
                            lw=lw,
                            figsize=figsize,
                            ylabel=ylabel,
                            subtitle=subtitle, savefig=savefig, show=show)


def rolling_volatility(returns, benchmark=None,
                       period=126, period_label="6-Months",
                       lw=1.5, fontname='Arial', grayscale=False,
                       figsize=(10, 3), ylabel="Volatility",
                       subtitle=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns)
    returns = returns.rolling(period).std() * _np.sqrt(252)

    if benchmark is not None:
        benchmark = _utils._prepare_benchmark(benchmark, returns.index)
        benchmark = benchmark.rolling(period).std() * _np.sqrt(252)

    _core.plot_rolling_stats(returns, benchmark,
                             hline=returns.mean(),
                             hlw=1.5,
                             ylabel=ylabel,
                             title='Rolling Volatility (%s)' % period_label,
                             fontname=fontname,
                             grayscale=grayscale,
                             lw=lw,
                             figsize=figsize,
                             subtitle=subtitle, savefig=savefig, show=show)


def rolling_sharpe(returns, benchmark=None, rf=0.,
                   period=126, period_label="6-Months",
                   lw=1.25, fontname='Arial', grayscale=False,
                   figsize=(10, 3), ylabel="Sharpe",
                   subtitle=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns, rf)
    returns = returns.rolling(period).mean() / returns.rolling(period).std()
    returns = returns * _np.sqrt(1 if period is None else period)

    if benchmark is not None:
        benchmark = _utils._prepare_benchmark(benchmark, returns.index, rf)
        benchmark = benchmark.rolling(
            period).mean() / benchmark.rolling(period).std()
        benchmark = benchmark * _np.sqrt(1 if period is None else period)

    _core.plot_rolling_stats(returns, benchmark,
                             hline=returns.mean(),
                             hlw=1.5,
                             ylabel=ylabel,
                             title='Rolling Sharpe (%s)' % period_label,
                             fontname=fontname,
                             grayscale=grayscale,
                             lw=lw,
                             figsize=figsize,
                             subtitle=subtitle, savefig=savefig, show=show)


def rolling_sortino(returns, benchmark=None, rf=0.,
                    period=126, period_label="6-Months",
                    lw=1.25, fontname='Arial', grayscale=False,
                    figsize=(10, 3), ylabel="Sortino",
                    subtitle=True, savefig=None, show=True):

    returns = _utils._prepare_returns(returns, rf)
    returns = returns.rolling(period).mean() / \
        returns[returns < 0].rolling(period).std()
    returns = returns * _np.sqrt(1 if period is None else period)

    if benchmark is not None:
        benchmark = _utils._prepare_benchmark(benchmark, returns.index, rf)
        benchmark = benchmark.rolling(period).mean() / benchmark[
            benchmark < 0].rolling(period).std()
        benchmark = benchmark * _np.sqrt(1 if period is None else period)

    _core.plot_rolling_stats(returns, benchmark,
                             hline=returns.mean(),
                             hlw=1.5,
                             ylabel=ylabel,
                             title='Rolling Sortino (%s)' % period_label,
                             fontname=fontname,
                             grayscale=grayscale,
                             lw=lw,
                             figsize=figsize,
                             subtitle=subtitle, savefig=savefig, show=show)


def monthly_heatmap(returns, annot_size=10, figsize=(10, 5),
                    cbar=True, square=False,
                    compounded=True, eoy=False,
                    grayscale=False, fontname='Arial',
                    ylabel=True, savefig=None, show=True):

    colors, ls, alpha = _core._get_colors(grayscale)
    cmap = 'gray' if grayscale else 'RdYlGn'

    returns = _stats.monthly_returns(returns, eoy=eoy,
                                     compounded=compounded) * 100

    fig_height = len(returns) / 3

    if figsize is None:
        size = list(_plt.gcf().get_size_inches())
        figsize = (size[0], size[1])

    figsize = (figsize[0], max([fig_height, figsize[1]]))

    if cbar:
        figsize = (figsize[0]*1.04, max([fig_height, figsize[1]]))

    fig, ax = _plt.subplots(figsize=figsize)
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    ax.set_title('      Monthly Returns (%)\n', fontsize=14, y=.995,
                 fontname=fontname, fontweight='bold', color='black')

    # _sns.set(font_scale=.9)
    ax = _sns.heatmap(returns, ax=ax, annot=True, center=0,
                      annot_kws={"size": annot_size},
                      fmt="0.2f", linewidths=0.5,
                      square=square, cbar=cbar, cmap=cmap,
                      cbar_kws={'format': '%.0f%%'})
    # _sns.set(font_scale=1)

    # align plot to match other
    if ylabel:
        ax.set_ylabel('Years', fontname=fontname,
                      fontweight='bold', fontsize=12)
        ax.yaxis.set_label_coords(-.1, .5)

    ax.tick_params(colors="#808080")
    _plt.xticks(rotation=0, fontsize=annot_size*1.2)
    _plt.yticks(rotation=0, fontsize=annot_size*1.2)
    _plt.subplots_adjust(hspace=0, bottom=0, top=1)

    try:
        _plt.subplots_adjust(hspace=0)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)

    if show:
        _plt.show(fig)

    _plt.close()

    if not show:
        return fig


def monthly_returns(returns, annot_size=10, figsize=(10, 5),
                    cbar=True, square=False,
                    compounded=True, eoy=False,
                    grayscale=False, fontname='Arial',
                    ylabel=True, savefig=None, show=True):
    return monthly_heatmap(returns, annot_size, figsize,
                           cbar, square,
                           compounded, eoy,
                           grayscale, fontname,
                           ylabel, savefig, show)
