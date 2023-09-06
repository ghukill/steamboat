# Steamboat

Steamboat is a library for orchestrating data pipeline tasks, oriented around a directed acyclic graph (DAG).

## Why "Steamboat"?

Navigating branching and merging rivers (see `DAG`), comprised of stacked decks chalk full of fun and adventure (see `parallelization`), locomotion derived from steam "feeding" propellers or paddlewheels (see `feeders`), all motivated by the calling (see `callers`) intrigue of the next river's bend.

And, sometimes, slow and steady wins the race.

## Installation

Base installation:
```shell
pip install steamboat
```

Installation with XML extras:
```shell
pip install "steamboat[xml]"
```

Installation with DataFrame extras:
```shell
pip install "steamboat[dataframe]"
```

## Development

Installation (creates Python 3.11 virtual environment and installs dev dependencies):
```shell
pipenv install --dev
```

Lint:
```shell
make lint
```

Tests:
```shell
make test
make test-verbose # chatty
```

## TODO  
  * Testing coverage now that architecture has settled down a bit
  * Create helpers to have instances of Steamboat `Runner` as both a return and step type
    * could pre-package DAGs and use _them_ as steps in another DAG
  * Add explicit types and behavior for combining steps
    * e.g. `context` will not have `.result` but only `.result_list` (or generator?)
    * then, a "normal" step (need a name) will have only `.result`
    * exceptions will be appropriately returned, if those properties are accessed, as we'll know the type of the active Step
  * Remove the ASCII graph
    * clunky with lots of nodes

## Wishlist

  * Docker containers as Steps
  * Parallel _process_ processing
    * Would need to ensure
      * steps and results are pickle-able
      * results are stored in a fashion that all processes can access
  * Webapp for running / finished pipeline
    * maybe something like `Runner(monitor=True)`
    * provides graphical outline of DAG
    * potentially show outputs along the way...
    * metrics on run
  * Apply pipeline of Steps to a list/generator return from a previous step
    * example:
      * Step1: parses JSONL file, returns list/generator of rows
      * Step2-5: perform sequential work on EACH line
      * Step6:
    * allows work to be parallel
    * MORE important: allows sequential steps to be oriented around a single item, vs lists of items
