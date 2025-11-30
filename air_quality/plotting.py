"""
Plotting utilities and style configurations for air quality visualizations.

This module provides consistent plotting styles, color schemes, and helper
functions for creating professional figures with consistent styling.
"""

import matplotlib.pyplot as plt
from typing import Dict, Tuple, Any


def get_plot_style() -> Dict[str, Any]:
    """
    Return matplotlib rcParams dictionary for consistent plot styling.

    Configures font size, line width, and bbox settings following
    matplotlib best practices.

    Returns
    -------
    dict
        Dictionary of matplotlib rcParams settings

    Examples
    --------
    >>> import matplotlib as mpl
    >>> mpl.rcParams.update(get_plot_style())
    """
    return {
        'font.size': 12,
        'lines.linewidth': 2,
        'savefig.bbox': 'tight'
    }


def get_city_colors() -> Dict[str, str]:
    """
    Return colorblind-friendly color scheme for six US cities.

    Uses a palette that maintains distinction for viewers with reduced
    color vision for improved accessibility.

    Returns
    -------
    dict
        Dictionary mapping city names to hex color codes

    Examples
    --------
    >>> colors = get_city_colors()
    >>> la_color = colors['Los Angeles']
    '#1f77b4'
    """
    return {
        'Los Angeles': '#1f77b4',      # Blue
        'Fresno': '#ff7f0e',           # Orange
        'Phoenix': '#2ca02c',          # Green
        'Denver': '#d62728',           # Red
        'Salt Lake City': '#9467bd',   # Purple
        'Pittsburgh': '#8c564b'        # Brown
    }


def get_common_kwargs() -> Dict[str, Any]:
    """
    Return common keyword arguments for plot styling.

    Provides default alpha, marker, and line style settings that can be
    used or overridden in plotting commands.

    Returns
    -------
    dict
        Dictionary of common matplotlib kwargs

    Examples
    --------
    >>> kwargs = get_common_kwargs()
    >>> plt.plot(x, y, **kwargs)
    """
    return {
        'alpha': 0.8,
        'linewidth': 2,
        'markersize': 6
    }


def setup_subplot_grid(
    nrows: int = 1,
    ncols: int = 1,
    figsize: Tuple[float, float] = None
) -> Tuple[plt.Figure, Any]:
    """
    Create a subplot grid with consistent styling.

    Helper function for creating subplots with appropriate figure size
    for professional figures. Default figure size scales with
    number of subplots.

    Parameters
    ----------
    nrows : int, default=1
        Number of subplot rows
    ncols : int, default=1
        Number of subplot columns
    figsize : tuple of float, optional
        Figure size as (width, height) in inches. If None, uses
        (6*ncols, 4*nrows) for appropriate scaling

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes or array of Axes
        Single axes object (if nrows=ncols=1) or array of axes

    Examples
    --------
    >>> fig, ax = setup_subplot_grid(nrows=2, ncols=3)
    >>> ax[0, 0].plot(x, y)

    >>> fig, ax = setup_subplot_grid(figsize=(10, 6))
    >>> ax.plot(x, y)
    """
    if figsize is None:
        figsize = (6 * ncols, 4 * nrows)

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

    return fig, ax


def configure_legend_outside(
    ax: plt.Axes,
    loc: str = 'upper left',
    bbox_to_anchor: Tuple[float, float] = (1.02, 1),
    **kwargs
):
    """
    Configure legend to appear outside plot area.

    Positions legend outside the plot to avoid obscuring data.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object to add legend to
    loc : str, default='upper left'
        Location anchor point for legend
    bbox_to_anchor : tuple of float, default=(1.02, 1)
        Box anchor position (x, y) in axes coordinates
    **kwargs
        Additional keyword arguments passed to ax.legend()

    Returns
    -------
    Legend
        Matplotlib legend object

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.plot(x, y, label='Data')
    >>> configure_legend_outside(ax)
    """
    default_kwargs = {
        'ncol': 1,
        'borderaxespad': 0,
        'frameon': True
    }
    default_kwargs.update(kwargs)

    return ax.legend(
        loc=loc,
        bbox_to_anchor=bbox_to_anchor,
        **default_kwargs
    )
