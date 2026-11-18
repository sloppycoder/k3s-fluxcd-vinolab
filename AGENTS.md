## Claude Code Instructions

This project contains FluxCD configurations for a Kuberntes Cluster.


** Important **
When you upgrade the versions of the components, you'll need to

1. Find all kustomization.yaml files, and check if there are any version numbers.
   If so, search for the latest version of the related package and update the version number back into the kustomization.yaml. Do not touch other files

2. Look at all yaml files that contains "kind: HelmRepository".
   For every HelpRepository,  search the internet for the latest versions, and update
   the version number in the respetive yaml file. If the latest version cannot be determined, just report it and continue to the next one.