## Claude Code Instructions

This project contains FluxCD configurations for a Kuberntes Cluster.

Read [README.md](README.md) before making changes. It documents the component
versions, cluster selections, and upgrade prerequisites. Keep its component
inventory in sync when changing versions or adding/removing components.


## Current workflow

* Work on `develop` for local mockpie/OrbStack testing; `main` drives super6. Promotion was authorized on 2026-11-18; super6 hardware/runtime validation is deferred until machine access is available.
* Read README's **Pending work** before continuing. Image automation must be restored; its suspension and local image/readiness overrides are temporary, not the intended workflow. Do not suspend it merely for local testing.
* Cloudflare account ID/token come from GCP Secret Manager through External Secrets. Keep credentials out of Git.
* Longhorn is upgraded but excluded/untested locally: host iSCSI tools are missing. `iscsi_tcp.ko` exists but is unloaded; do not assume missing kernel support. Super6 storage still needs testing.

** Important **
When you upgrade the versions of the components, you'll need to

1. Find all kustomization.yaml files, and check if there are any version numbers.
   If so, search for the latest version of the related package and update the version number back into the kustomization.yaml. Do not touch other files

2. Look at all yaml files that contains "kind: HelmRepository".
   For every HelpRepository,  search the internet for the latest versions, and update
   the version number in the respetive yaml file. If the latest version cannot be determined, just report it and continue to the next one.
