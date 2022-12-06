# Changelog
All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Option to choose between three different strategies to translate short-term
  ratings into scores and vice versa ([#24](https://github.com/hsbc/pyratings/pull/24)).
- Functionality to remove prefix '(P)' when cleaning ratings
  ([#27](https://github.com/hsbc/pyratings/issues/27))

### Changed
- BREAKING CHANGE: Automatic column naming
  ([#9](https://github.com/hsbc/pyratings/issues/9)). 
    - ``get_scores_from_ratings()``  
      When input a ``pd.Series``, the name of the output series will now become
      ``ratings.name`` prefixed with "rtg_score_".  
      When input a ``pd.DataFrame``, the column names of the output frame will now 
      become ``ratings.columns`` prefixed with "rtg_score_". 
    - ``get_warf_from_ratings()``   
      When input a pd.Series, the name of the output series will now become
      ``ratings.name`` prefixed with "warf_".  
      When input a pd.DataFrame, the column names of the output frame will now become 
      ``ratings.columns`` prefixed with "warf_".
- BREAKING CHANGE: Translations of short-term ratings are now different
  ([#16](https://github.com/hsbc/pyratings/issues/16)).

### Fixed
- Short-term DBRS rating entries in Ratings.db
  ([#29](https://github.com/hsbc/pyratings/issues/29)).

### Improved
- Splitting the code base into multiple files in order to increase maintainability
  ([#8](https://github.com/hsbc/pyratings/issues/8)).
- Internal checks have been improved 
  ([#20](https://github.com/hsbc/pyratings/issues/20)).
- Documentation has been updated and will now be created via
  [mkdocs](https://www.mkdocs.org/) and 
  [mkdocstrings](https://mkdocstrings.github.io/python/).
- Using [nox](https://nox.thea.codes/) to test the code base against multiple Python 
  versions.
- Make code base [flake8](https://flake8.pycqa.org/) compliant.
- Use [pre-commit](https://pre-commit.com/) to ensure good quality before 
  commiting/sending PRs.
- Use [python-kacl](https://pypi.org/project/python-kacl/) in order to maintain CHAGELOG.

## [0.5.4] - 2022-07-07
### Refactored
- Moved from ``setup.py`` to ``pyproject.toml`` configuration file.

## [0.5.3] - 2022-04-05
### Added
- Complete documentation now available on public GitHub Pages at 
  https://hsbc.github.io/pyratings/.

## 0.5.2 - 2022-01-24
### Refactored
- Moved sphinx configuration to ``docsrc`` folder.
- Documentation data for GitHub pages can be found under ``docs``.

## 0.5.1 - 2022-01-06
### Security
- Removed links to internal network drives in ``tox.ini``.
- Removed links to GitHub issues in this ``CHANGELOG.md`` as they link to internal 
  GitHub repo.

## 0.5.0 - 2022-01-03
### Added
- ``pyratings.get_scores_from_ratings``
- ``pyratings.get_scores_from_warf``
- ``pyratings.get_ratings_from_scores``
- ``pyratings.get_ratings_from_warf``
- ``pyratings.get_warf_from_scores``
- ``pyratings.get_warf_from_ratings``

### Changed
- BREAKING CHANGE: Internal resource handling now utilizes ``importlib.resources``, 
  which makes Python >=3.9 **mandatory**.
- BREAKING CHANGE: Some function signatures have been changed:
    - ``pyratings.get_pure_ratings``  
      --Old--: ``get_pure_ratings(ratings: Union[pd.Series, List[pd.Series], pd.DataFrame]) -> Union[pd.Series, List[pd.Series], pd.DataFrame]``  
      --New--: ``get_pure_ratings(ratings: Union[str, pd.Series, pd.DataFrame]) -> Union[str, pd.Series, pd.DataFrame]``
    - ``pyratings.get_best_ratings``  
      --Old--: ``get_best_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``  
      --New--: ``get_best_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``
    - ``pyratings.get_second_best_ratings``  
      --Old--: ``get_second_best_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``  
      --New--: ``get_second_best_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``
    - ``pyratings.get_worst_ratings``  
      --Old--: ``get_worst_ratings(ratings: Dict[str, pd.Series], tenor: Optional[str] = "long-term") -> pd.Series``  
      --New--: ``get_worst_ratings(ratings: pd.DataFrame, rating_provider_input: List[str] = None, rating_provider_output: str = "S&P", tenor: str = "long-term") -> pd.Series``

### Removed
- ``get_rating()`` -> Use ``pyratings.get_ratings_from_scores`` or 
  ``pyratings.get_ratings_from_warf`` instead.
- ``to_ratings_from_scores()`` -> Use ``pyratings.get_ratings_from_scores`` instead.
- ``to_scores_from_ratings()`` -> Use ``pyratings.get_scores_from_ratings`` instead.
- ``to_score_from_warf()`` -> Use ``pyratings.get_scores_from_warf`` instead.
- ``to_warf_from_ratings()`` -> Use ``pyratings.get_warf_from_ratings`` instead.

## 0.4.2 - 2021-11-19
### Refactored
- Added unit tests in order to arrive at 100% code coverage

## 0.4.1 - 2021-11-16
### Changed
- Function signature of ``pyratings.get_pure_ratings``.

## 0.4.0 - 2021-03-26
### Added
- Computation of `best`, `worst`, and `second_best` ratings on a security basis. 
    - ``pyratings.get_best_ratings``
    - ``pyratings.get_second_best_ratings``
    - ``pyratings.get_worst_ratings``
- Computation of WARF buffer, i.e. distance from current WARF to next maxWARF. 
    - ``pyratings.get_warf_buffer``
- Documentation
    - Overview
    - Getting started
    - API Reference

### Improved
- Updated docstrings.
- ``doctest`` integration into ``pytest``.

### Changed
- Some functions such as ``to_scores_from_ratings`` and ``get_pure_ratings`` got 
  their signatures changed.  
  They now accept a ``Dict[str, pd.Series]``, where the dictionary keys represent 
  the rating provider and the dictionary values represent the respective ratings. 
  This will allow to transform multiple columns of a ``pd.DataFrame`` in one step.
- "S&P" and "Moody's" are no valid rating provider anymore. The new acronyms are 
  "SP" and "Moody".
- ``pyratings.get_pure_ratings`` output column names now have the suffix "_clean".
- ``to_ratings_from_scores`` became an internal function.
- ``get_rating`` is now the go-to function when it comes to translating a single 
  rating score or numerical WARF into a rating. It replaces 
  ``to_ratings_from_avg_warf`` and ``get_avg_rating``.
- ``get_avg_rating_score`` and ``get_avg_warf`` shared the exact same code. These 
  functions have been merged into ``get_weighted_average``.
- Internal code optimizations.

### Removed
- ``get_avg_rating``
- ``get_avg_rating_score``
- ``get_avg_warf``
- ``to_ratings_from_avg_warf``
- ``to_ratings_from_warf``

### Fixed
- ``get_weighted_average`` (previously ``get_avg_rating_score`` and ``get_avg_warf``)
  now handle missing rating scores/WARF differently. Previously, they have been 
  ignored. However, this led to a too positive average rating/WARF.
  Now, only securities with a rating score/WARF available will contribute to the 
  average computation. To put it differently, the average score/WARF is solely based 
  on rated securities.

## 0.3.0 - 2021-02-22
### Added
- Computation of average rating.
- Computation of average WARF.
- Translation from traditional ratings to WARF and vice versa.

### Changed
- Adjusted WARF and MaxWARF values for ratings Ca and C to allow for differentiation 
  of translated values between ratings Ca/C/D.
- Folder layout now adheres to ``src`` layout.
- Package resource management now using ``pkg_resources`` from Python's standard 
  library.

### Improved
- Use ``tox`` for unit tests.

## 0.2.0 - 2020-12-18
### Added
- More rating agencies: DBRS, Bloomberg composite, ICE.
- Short-term ratings.

### Improved
- Rating scales are now maintained within a SQLite database. Previously, rating 
  scales had been hard coded in a traditional Python ``dict``.

### Fixed
- Cleansing of unsolicited ratings.

## 0.1.0 - 2020-12-09
### Added
- Function to clean ratings (delete watches).
- Function to translate S&P/Fitch/Moody's credit ratings into rating scores.
- Function to translate rating scores into S&P/Fitch/Moody's credit ratings.

[Unreleased]: https://github.com/hsbc/pyratings/tree/v0.5.4...HEAD
[0.5.4]: https://github.com/hsbc/pyratings/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/hsbc/pyratings/compare/v0.5.2..v0.5.3
