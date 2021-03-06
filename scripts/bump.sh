#!/bin/bash
set -e

OPERATION=$(tr [a-z] [A-Z] <<< ${1:-patch})

VERSION=$(grep "version=" setup.py | sed "s/.*'\(\([[:digit:]].\?\)*\)'.*/\1/g")

PATCH='echo "\1.\2.$((\3+1))"'
MINOR='echo "\1.$((\2+1)).0"'
MAJOR='echo "$((\1+1)).0.0"'
eval BUMPER='$'$OPERATION
VERSION_REGEX='^\([[:digit:]]\+\)\.\([[:digit:]]\+\)\.\([[:digit:]]\+\)$'
NEW_VERSION=$(sed "s/${VERSION_REGEX}/${BUMPER}/ge" <<< ${VERSION})

TIMESTAMP=$(date +%Y-%m-%d)
CHANGELOG_ENTRY="## [${NEW_VERSION}] - ${TIMESTAMP}"
sed -i "s/^\(## \[Unreleased\]\)$/\1\n\n${CHANGELOG_ENTRY}/g" CHANGELOG.md

CHANGELOG_HEAD_LINK="^\[Unreleased\]\(.*\)v${VERSION}...HEAD$"
CHANGELOG_NEW_HEAD_LINK="[Unreleased]\1v${NEW_VERSION}...HEAD"
CHANGELOG_NEW_COMPARISON="[${NEW_VERSION}]\1v${VERSION}...v${NEW_VERSION}"
CHANGELOG_LINK="${CHANGELOG_NEW_HEAD_LINK}\n${CHANGELOG_NEW_COMPARISON}"
sed -i "s/${CHANGELOG_HEAD_LINK}/${CHANGELOG_LINK}/g" CHANGELOG.md

sed -i "s/version='${VERSION}'/version='${NEW_VERSION}'/g" setup.py

git add CHANGELOG.md setup.py
git commit -m "Version ${NEW_VERSION}"
git tag "v${NEW_VERSION}"
git push
git push --tags

exit 0
