# MPXRadar-frontend
MonkeyPoxRadar frontend codebase.

# Installation

´´´
´´´


----

# Contribution

Always check code version from dev branch before coding.
´´´
git checkout dev
git pull
´´´

## Install dependencies

´´´
conda create -n mpxsonar-dev python=3.9 poetry fortran-compiler nox pre-commit emboss=6.6.0
conda activate covsonar-dev
git config blame.ignoreRevsFile .git-blame-ignore-revs  # ignore black reformatting when doing git blame
pre-commit install  # install pre-commit hooks for formatting and linting
poetry install  # install current source of covsonar and its dependencies
´´´

## Before Commit/Push
1. Check current branch.
2. Run python format checking -> `pre-commit run --all-files`, Fix it if found, otherwise you will not be allowed to commit and push.

# Add/Update MPXsonar


## First time add MPXsonar
´´´
git subtree add --prefix libs/mpxsonar https://github.com/silenus092/mpxsonar dev --squash
´´´

## Update MPXsonar
´´´
git subtree pull --prefix libs/mpxsonar https://github.com/silenus092/mpxsonar dev --squash
´´´