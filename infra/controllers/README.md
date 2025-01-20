## ```infra/controllers```
This directory contains the CRD that must be installed before settings in ```infra/configs``` can be applied

|---|---|
| ```base``` | base components required for each cluster managed |
| ```optional``` | optional components |
| ```clusters``` | clusters managed. each cluster should have a directory under it |
