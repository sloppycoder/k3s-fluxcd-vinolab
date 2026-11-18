# GitOps setup with FluxCD for K3s Kubernetes clusters

This repo contains the [FluxCD](https://fluxcd.io) setup for my homelab K3S cluster with 6 Raspberry Pi CM4. See [this repo](https://github.com/sloppycoder/k3s-ansible) for hardware details.

## Design principles for GitOps

In a large organiztion it is common to have an infra team who is in charge is shared infrastructure components, e.g. Kubernetes clsuters, databases, Redis cache and other compoents; while application teams are respsonbile for deployment of the applcaiton components on top of shared infrastructure mangaed by the infrastructre team.

With this use case in mind, here are the design decisions for this FluxCD setup:

* This repo is intended to be used for multiple Kuberentes clusters that share a common underlying infrastructure, e.g. K3S, EKS, etc
* Shared components, e.g. storage, monitoring, external secret operator are manged in this repo.
* Each Kuberentes cluster can be shared by multiple application teams.
* Each application team mangages their own GitOps repo that is external to this repo.
* Each application environment, e.g. App1 DEV, App2 SIT, are deployed into its own namespace in a Kuberntes cluster. By default the communicatoin between application namespaces are blocked, to provide proper isolation between envrionments.

### Directory structure

#### [prep](prep)

steps to be peform manually prior to bootstrap FluxCD.

#### [infra/controllers](infra/controllers)

Kustomization directory strcture that creates CRDs

* ```base```  contains the common components
* ```optional``` contains the optional components
* Cluster overlays live in [`cluster-configs`](cluster-configs). Each cluster includes the base and selected optional components; see [super6 controllers](cluster-configs/super6/infra/controllers/kustomization.yaml).

#### [infra/configs](infra/configs)

Infra configurations that depends on CRD in the ```controllers``` direcrory. The directory structure is similiar to ```controllers``` directory.
The ```namespaces``` diretory cotnains individual namespaces that will be created and their associated configuration, including networkpolicy that blocks communication between namespaces except for ones that runs shared components, e.g. infra. see [an example network policy](infra/configs/namespaces/test/network-policy.yaml) here.

The [`cluster-configs`](cluster-configs) directory selects configurations for each cluster: the base, optional configurations, and namespaces; see [super6 configs](cluster-configs/super6/infra/configs/kustomization.yaml). [`clusters`](clusters) contains the Flux bootstrap manifests, infrastructure reconciliation definitions, and external application repository sources.

### Components

Versions below describe the checked-in manifests, not an inspection of a running cluster. Upstream versions were checked on **2026-11-18** using official release metadata, Helm indexes, and the Weave GitOps OCI registry. Helm chart versions and application versions are separate where they differ. Release candidates are excluded from upgrade targets.

| Component / purpose | Version in this repo | Selected by | Latest verified stable version / source |
| --- | --- | --- | --- |
| FluxCD — GitOps controllers | Bundle **2.10.0** | Both clusters | [2.10.0](https://github.com/fluxcd/flux2/releases/tag/v2.10.0) |
| External Secrets Operator — GCP Secret Manager sync | Chart/app **0.18.2** | Both, [base](infra/controllers/base/external-secrets.yaml) | Chart/app [2.15.0](https://charts.external-secrets.io/index.yaml) |
| Longhorn — persistent block storage | **1.9.0** | Both, [manifest](infra/controllers/optional/longhorn/kustomization.yaml) | [1.13.0](https://github.com/longhorn/longhorn/releases/tag/v1.13.0) |
| CloudNativePG — PostgreSQL operator | **1.26.0** | Both, [manifest](infra/controllers/optional/cnpg/kustomization.yaml) | [1.30.2](https://github.com/cloudnative-pg/cloudnative-pg/releases/tag/v1.30.2) |
| Knative Serving — serverless workloads | **1.18.1**, CRDs and core | Both, [CRDs](infra/controllers/optional/knative-serving/kustomization.yaml), [core](infra/configs/optional/knative-serving/kustomization.yaml) | [1.24.0](https://github.com/knative/serving/releases/tag/knative-v1.24.0) |
| Kourier — ingress for Knative Serving | **1.18.0** | Both, [manifest](infra/configs/optional/knative-serving/kustomization.yaml) | [1.24.0](https://github.com/knative-extensions/net-kourier/releases/tag/knative-v1.24.0) |
| Knative Eventing — events, in-memory channels, channel broker | **1.18.2**, CRDs and core/plugins | Both, [CRDs](infra/controllers/optional/knative-eventing/kustomization.yaml), [core/plugins](infra/configs/optional/knative-eventing/kustomization.yaml) | [1.24.0](https://github.com/knative/eventing/releases/tag/knative-v1.24.0) |
| Weave GitOps — Flux dashboard | Chart **4.0.36**, app **0.38.0** | Both, [manifest](infra/configs/base/weave-gitops.yaml) | Stable chart **4.0.36**, app **0.38.0**; [OCI registry](https://github.com/weaveworks/weave-gitops/pkgs/container/charts%2Fweave-gitops). The newer app tag `0.39.1-rc.1` is a release candidate. |
| NFS subdirectory provisioner — existing NFS server volumes | **Unpinned remote deploy directory**; currently upstream uses image **4.0.2** | super6 only, [manifest](infra/controllers/optional/nfs-subdir-external-provisioner/kustomization.yaml) | Latest [chart release 4.0.18](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/releases/tag/nfs-subdir-external-provisioner-4.0.18); [deploy image 4.0.2](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/blob/master/deploy/deployment.yaml). Chart and image numbers differ. |
| Redis Operator (OT-CONTAINER-KIT) | Chart/app **0.21.0** | mockpie only, [manifest](infra/controllers/optional/redis-operator.yaml) | Chart/app [0.27.0](https://ot-container-kit.github.io/helm-charts/index.yaml) |
| NATS — messaging with JetStream | Chart **1.3.9**, server **2.11.6** | Available, **neither cluster selects it**; [manifest](infra/controllers/optional/nats.yaml) | Chart/server [2.15.2](https://nats-io.github.io/k8s/helm/charts/index.yaml) |
| NACK — NATS JetStream controller | Chart **0.25.1**, app **0.14.1** | Available alongside NATS, **not selected** | Chart **0.35.0**, app **0.24.0**; [index](https://nats-io.github.io/k8s/helm/charts/index.yaml) |
| Traefik whoami — ingress test service | `traefik/whoami`, **no tag** (implicit `latest`) | Both, [manifest](infra/configs/base/whoami.yaml) | [1.12.0](https://github.com/traefik/whoami/releases/tag/v1.12.0) |
| Alpine Linux — debug deployment | `alpine:latest`, **not pinned** | Available, **not selected**; [manifest](infra/configs/optional/alpine-linux.yaml) | [3.24.4](https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/aarch64/latest-releases.yaml) |
| K3s / Kubernetes — underlying cluster | **Not pinned or installed here**; managed outside this repo | Both clusters | Latest published [K3s 1.37.2+k3s1](https://github.com/k3s-io/k3s/releases/tag/v1.37.2%2Bk3s1); choose a supported upgrade path for the actual installed version |
| Traefik — ingress and dashboards | **Not pinned or installed here**; routes assume it exists | Both clusters | Upstream [3.7.19](https://github.com/traefik/traefik/releases/tag/v3.7.19); use the version compatible with the selected K3s release |

Both clusters contain the same Flux bundle and controller image pins:

| Flux controller | Pinned image version |
| --- | --- |
| source-controller | 1.10.1 |
| kustomize-controller | 1.10.1 |
| helm-controller | 1.7.1 |
| notification-controller | 1.10.0 |
| image-reflector-controller | 1.3.0 |
| image-automation-controller | 1.3.0 |

These are a bundle: regenerate each cluster's `gotk-components.yaml` with the target Flux CLI rather than independently upgrading controller images. The [Flux 2.10.0 release notes](https://github.com/fluxcd/flux2/releases/tag/v2.10.0) list its matching controller versions.

GCP Secret Manager and Cloudflare Zero Trust are external service integrations with no package version pinned here. Application and database instance versions in the external `vinobank-gitops` repository are outside this inventory; the CloudNativePG and Redis entries above are operator versions.

### Certificate and ingress transition

cert-manager (previously 1.18.2), the Let's Encrypt issuer, its Cloudflare DNS credential sync, and the whoami certificate request have been removed. No external-dns deployment existed in this repository. External Secrets Operator remains enabled. Traefik-specific dashboard routes are not selected, and whoami and Weave are currently internal-only while Cloudflare ingress is introduced. Local tests can use direct Service access or port forwarding.

### New Relic removal

New Relic is no longer selected by either cluster. Its `nri-bundle` HelmRelease (previously chart **6.0.4**), HelmRepository, cluster-name patches, license ExternalSecrets in `infra` and `test`, and sample license field have been removed.

The `infra-configs` Flux Kustomizations have `prune: true`. Once this change reaches each cluster's tracked branch, Flux should prune the old resources and helm-controller should uninstall the New Relic release. **mockpie tracks `develop`; super6 tracks `main`**, so both branches must receive the removal. Verify reconciliation and Helm uninstall completion before treating monitoring as removed. A failed uninstall or an orphaned generated license Secret may need separate cleanup.

The remote `infra-secret` in GCP Secret Manager and ignored local credential files are not changed by GitOps removal. Remove their obsolete `newrelic_license_key` property separately, preserving the remaining credentials. No replacement monitoring stack is configured by this change.

## Boostrap FluxCD in a cluster

Follow the steps in [prep](prep). This creates a secret that contains the credential to access GCP Secret Manager, where we'll sync secrets to the cluster using [external-secret](https://external-secrets.io/). Using external secret in order to avoid the hassle of setup SOPS and managing keys locally.

Download Flux CLI by following the [officail documentation](https://fluxcd.io/flux/cmd/), then

```shell
export GITHUB_TOKEN=ghp_pat
flux bootstrap github   \
     --components-extra=image-reflector-controller,image-automation-controller \
     --owner=sloppycoder \
     --repository=k3s-fluxcd-vinolab \
     --branch=main \
     --read-write-key \
     --path=clusters/super6

```

## Upgrade FluxCD

```shell

# checkout this repo

flux install \
--components-extra image-reflector-controller,image-automation-controller \
--export > clusters/super6/flux-system/gotk-components.yaml

git commit -m "Upgrade to flux version 2.x.x"
git push

```

## Upgrade components

These clusters are being rebuilt from fresh installations. Current release pins can be selected directly after checking their Kubernetes and node prerequisites; the adjacent-minor migration procedures for existing deployments are not required for an empty cluster.

Work on `develop` and test the local mockpie configuration before discussing promotion to `main` for super6. The planned sequence is: remove New Relic; upgrade Flux and migrate APIs; remove cert-manager and obsolete ingress configuration; upgrade the remaining components; test locally; then introduce Cloudflare Tunnel ingress with Access policies configured before dashboards are published.

Flux manifests use stable HelmRelease `v2` and HelmRepository `v1` APIs. Weave GitOps uses an OCIRepository and HelmRelease `chartRef`. The bundle is generated by Flux CLI **2.10.0** for both clusters; this release supports Kubernetes **1.35.2+, 1.36.1+, or 1.37.0+**. The stable Weave GitOps app remains old: its compatibility with these controllers must be verified, rather than inferred from successful chart rendering.

For any later upgrades of a running cluster, follow each component's supported migration procedure and verify restorable backups. In particular, [Longhorn](https://longhorn.io/docs/1.13.0/deploy/upgrade/) and [Knative](https://knative.dev/docs/install/upgrade/upgrade-installation/) have version-step requirements. Keep CRD and core/plugin manifest pins synchronized.

Render affected overlays, commit, and push only the tested development configuration to its tracked branch. Check reconciliation and workload behavior after each deployment change. Local tests do not establish Raspberry Pi hardware or super6 NFS compatibility.

## Common Maintanence Commands

1. force external secret sync
```shell
kubectl annotate es <name> -n <ns> force-sync=$(date +%s) --overwrite
```
