*********
Changelog
*********

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[v0.5.3] - 2022-04-05
=====================

Added
--------
* Complete documentation now available on public GitHub Pages at https://hsbc.github.io/pyratings/.


[v0.5.2] - 2022-01-24
=====================

Changed
--------
* Moved sphinx configuration to ``docsrc`` folder.
* Documentation data for GitHub pages can be found under ``docs``.


[v0.5.1] - 2022-01-06
=====================

Security
--------
* Removed links to internal network drives in ``tox.ini``.
* Removed links to GitHub issues in this ``CHANGELOG.rst`` as they link to internal GitHub repo.


[v0.5.0] - 2022-01-03
=====================
| This release introduces a number of **BREAKING CHANGES!**
| Supported versions:

* Python 3.9
* Python 3.10

Added
-----
Some new functions have been introduced (`Issue #61`).

* ``pyratings.get_scores_from_ratings``
* ``pyratings.get_scores_from_warf``
* ``pyratings.get_ratings_from_scores``
* ``pyratings.get_ratings_from_warf``
* ``pyratings.get_warf_from_scores``
* ``pyratings.get_warf_from_ratings``

Changed
-------
* Internal resource handling now utilizes ``importlib.resources``, which makes Python >=3.9 **mandatory**.
* Some function signatures have been changed, which will probably **break existing code**!

    * ``pyratings.get_pure_ratings``
        | **Old**: ``get_pure_ratings(ratings: Union[pd.Series, List[pd.Series], pd.DataFrame]) -> Union[pd.Series, List[pd.Series], pd.DataFrame]``
        | **New**: ``get_pure_ratings(ratings: Union[str, pd.Series, pd.DataFrame]) -> Union[str, pd.Series, pd.DataFrame]``
    * ``pyratings.get_best_ratings``
        | **Old**: ``get_best_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``
        | **New**: ``get_best_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``
    * ``pyratings.get_second_best_ratings``
        | **Old**: ``get_second_best_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``
        | **New**: ``get_second_best_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``
    * ``pyratings.get_worst_ratings``
        | **Old**: ``get_worst_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``
        | **New**: ``get_worst_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``

Removed
-------
Some functions have been removed/replaced:

* ``get_rating()`` -> Use ``pyratings.get_ratings_from_scores`` or ``pyratings.get_ratings_from_warf`` instead.
* ``to_ratings_from_scores()`` -> Use ``pyratings.get_ratings_from_scores`` instead.
* ``to_scores_from_ratings()`` -> Use ``pyratings.get_scores_from_ratings`` instead.
* ``to_score_from_warf()`` -> Use ``pyratings.get_scores_from_warf`` instead.
* ``to_warf_from_ratings()`` -> Use ``pyratings.get_warf_from_ratings`` instead.


[v0.4.2] - 2021-11-19
=====================

Changed
-------
* Deleted unused code (`Issue #49`).
* Added unit test in order to arrive at 100% code coverage


[v0.4.1] - 2021-11-16
=====================

Changed
-------
* Function signature of ``pyratings.get_pure_ratings`` (`Issue #43`).
* Updated source code location in ``README.rst`` and ``tox.ini`` (`Issue #46`).


[v0.4.0] - 2021-03-26
=====================

Added
-----
* Computation of `best`, `worst`, and `second_best` ratings on a security basis (`Issue #14`).

  * ``pyratings.get_best_ratings``
  * ``pyratings.get_second_best_ratings``
  * ``pyratings.get_worst_ratings``
* Computation of WARF buffer, i.e. distance from current WARF to next maxWARF (`Issue #19`).

  * ``pyratings.get_warf_buffer``
* Improved docstrings.
* ``doctest`` integration into ``pytest``.
* Documentation (online and PDF)

  * Overview
  * Getting started
  * API Reference

Changed
-------
* | Some functions such as ``to_scores_from_ratings`` and ``get_pure_ratings`` got their signatures changed (`Issue #16`).
  | They now accept a ``Dict[str, pd.Series]``, where the dictionary keys represent the rating provider and the dictionary values represent the respective ratings. This will allow to transform multiple columns of a ``pd.DataFrame`` in one step.
* "S&P" and "Moody's" are no valid rating provider anymore. The new acronyms are "SP" and "Moody".
* ``pyratings.get_pure_ratings`` output column names now have the suffix "_clean".
* ``to_ratings_from_scores`` became an internal function
* | ``get_rating`` is now the go-to function when it comes to translating a single rating score or numerical WARF into a rating.
  | It replaces ``to_ratings_from_avg_warf`` and ``get_avg_rating``.
* ``get_avg_rating_score`` and ``get_avg_warf`` shared the exact same code. These functions have been merged into ``get_weighted_average`` (`Issue #40`).
* Internal code optimizations

Removed
-------
* ``get_avg_rating``
* ``get_avg_rating_score``
* ``get_avg_warf``
* ``to_ratings_from_avg_warf``
* ``to_ratings_from_warf``

Fixed
-----
* | ``get_weighted_average`` (previously ``get_avg_rating_score`` and ``get_avg_warf``) now handle missing rating scores/WARF differently. Previously, they have been ignored. However, this led to a too positive average rating/WARF.
  | Now, only securities with a rating score/WARF available will contribute to the average computation. To put it differently, the average score/WARF is solely based on rated securities (`Issue #38`).


[v.0.3.0] - 2021-02-22
======================

Added
-----
* Computation of average ratings (`Issue #8`).
* Computation of average WARF (`Issue #9`).
* Translation from traditional ratings to WARF and vice versa (`Issue #10`).
* ``tox`` unit tests

Changed
-------
* Adjusted WARF and MaxWARF values for ratings Ca and C to allow for differentiation of translated values between ratings Ca/C/D.
* Folder layout now adheres to ``src`` layout.
* Package resource management now using ``pkg_resources`` from Python's standard library.


[v.0.2.0] - 2020-12-18
======================

Added
-----
* Short-term ratings (`Issue #1`).
* More rating agencies to database: DBRS, Bloomberg composite, ICE (`Issue #5`).

Changed
-------
* Rating scales are now maintained within a SQLite database. Previously, rating scales had been hard coded in a traditional Python ``dict``.

Fixed
-----
* Cleansing of unsolicited ratings (`Issue #3`).


[v0.1.0] - 2020-12-09
=====================

Added
-----
* Function to clean ratings (delete watches).
* Function to translate S&P/Fitch/Moody's credit ratings into rating scores.
* Function to translate rating scores into S&P/Fitch/Moody's credit ratings.