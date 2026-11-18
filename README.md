# GitOps setup with FluxCD for K3s Kubernetes clusters

This repo contains the [FluxCD](https://fluxcd.io) setup for my homelab K3S cluster with 6 Raspberry Pi CM4. See [this repo](https://github.com/sloppycoder/k3s-ansible) for hardware details.

## Pending work

Infrastructure and Helm releases reconcile on local OrbStack; the original `testfunc` passes PostgreSQL, Redis, and CloudEvent tests. All four local Flux Kustomizations, including `app-infra-test`, are now Ready.

* Restore normal image automation: refresh the rejected GitHub write credential in GCP `vinobank-gitops-token`, restore authenticated Git access, and remove the temporary suspension, image override, and readiness workaround. Verify build → image detection → Git commit → deployment.
* Publish and test additional development Ingress routes after confirming hostnames and Cloudflare Access policies. mockpie selects the public `kube-whoami-dev.vino9.net` test route; dashboards remain internal.
* Resurrect super6 and validate its Longhorn/NFS storage and hardware before discussing the merge into `main`. Longhorn was upgraded but not tested locally.

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
| Cloudflare Tunnel Ingress Controller (STRRL) | Chart/app **0.1.0**, bundled cloudflared **2026.7.3-host-metrics.1** | Both, [manifest](infra/configs/optional/cloudflare-tunnel.yaml); mockpie selects the public whoami test route | [0.1.0](https://github.com/STRRL/cloudflare-tunnel-ingress-controller/releases/tag/v0.1.0) |
| metrics-server — CPU metrics for autoscaling | **0.9.1** | mockpie only, [manifest](infra/controllers/optional/metrics-server/kustomization.yaml) | [0.9.1](https://github.com/kubernetes-sigs/metrics-server/releases/tag/v0.9.1) |
| FluxCD — GitOps controllers | Bundle **2.10.0** | Both clusters | [2.10.0](https://github.com/fluxcd/flux2/releases/tag/v2.10.0) |
| External Secrets Operator — GCP Secret Manager sync | Chart/app **2.15.0** | Both, [base](infra/controllers/base/external-secrets.yaml) | Chart/app [2.15.0](https://charts.external-secrets.io/index.yaml) |
| Longhorn — persistent block storage | **1.13.0** | super6; skipped on OrbStack, [manifest](infra/controllers/optional/longhorn/kustomization.yaml) | [1.13.0](https://github.com/longhorn/longhorn/releases/tag/v1.13.0) |
| CloudNativePG — PostgreSQL operator | **1.30.2** | Both, [manifest](infra/controllers/optional/cnpg/kustomization.yaml) | [1.30.2](https://github.com/cloudnative-pg/cloudnative-pg/releases/tag/v1.30.2) |
| Knative Serving — serverless workloads | **1.24.0**, CRDs and core | Both, [CRDs](infra/controllers/optional/knative-serving/kustomization.yaml), [core](infra/configs/optional/knative-serving/kustomization.yaml) | [1.24.0](https://github.com/knative/serving/releases/tag/knative-v1.24.0) |
| Kourier — ingress for Knative Serving | **1.24.0** | Both, [manifest](infra/configs/optional/knative-serving/kustomization.yaml) | [1.24.0](https://github.com/knative-extensions/net-kourier/releases/tag/knative-v1.24.0) |
| Knative Eventing — events, in-memory channels, channel broker | **1.24.0**, CRDs and core/plugins | Both, [CRDs](infra/controllers/optional/knative-eventing/kustomization.yaml), [core/plugins](infra/configs/optional/knative-eventing/kustomization.yaml) | [1.24.0](https://github.com/knative/eventing/releases/tag/knative-v1.24.0) |
| Weave GitOps — Flux dashboard | Chart **4.0.36**, app **0.38.0** | Both, [manifest](infra/configs/base/weave-gitops.yaml) | Stable chart **4.0.36**, app **0.38.0**; [OCI registry](https://github.com/weaveworks/weave-gitops/pkgs/container/charts%2Fweave-gitops). The newer app tag `0.39.1-rc.1` is a release candidate. |
| NFS subdirectory provisioner — existing NFS server volumes | Deploy revision **`05abcf2e07f5`**, image **4.0.2** | super6 only, [manifest](infra/controllers/optional/nfs-subdir-external-provisioner/kustomization.yaml) | Latest [chart release 4.0.18](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/releases/tag/nfs-subdir-external-provisioner-4.0.18); [deploy image 4.0.2](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/blob/master/deploy/deployment.yaml). Chart and image numbers differ. |
| Redis Operator (OT-CONTAINER-KIT) | Chart/app **0.27.0** | mockpie only, [manifest](infra/controllers/optional/redis-operator.yaml) | Chart/app [0.27.0](https://ot-container-kit.github.io/helm-charts/index.yaml) |
| NATS — messaging with JetStream | Chart **2.15.2**, server **2.15.2** | Available, **neither cluster selects it**; [manifest](infra/controllers/optional/nats.yaml) | Chart/server [2.15.2](https://nats-io.github.io/k8s/helm/charts/index.yaml) |
| NACK — NATS JetStream controller | Chart **0.35.0**, app **0.24.0** | Available alongside NATS, **not selected** | Chart **0.35.0**, app **0.24.0**; [index](https://nats-io.github.io/k8s/helm/charts/index.yaml) |
| Traefik whoami — ingress test service | `traefik/whoami:v1.12.0` | Both, [manifest](infra/configs/base/whoami.yaml) | [1.12.0](https://github.com/traefik/whoami/releases/tag/v1.12.0) |
| Alpine Linux — debug deployment | `alpine:3.24.4` | Available, **not selected**; [manifest](infra/configs/optional/alpine-linux.yaml) | [3.24.4](https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/aarch64/latest-releases.yaml) |
| K3s / Kubernetes — underlying cluster | **Not pinned or installed here**; managed outside this repo | Both clusters | Latest published [K3s 1.37.2+k3s1](https://github.com/k3s-io/k3s/releases/tag/v1.37.2%2Bk3s1); choose a supported upgrade path for the actual installed version |

The optional NATS release uses current `config.jetstream` chart values and remains memory-only until persistent storage is explicitly configured. It and NACK are not enabled by either overlay.

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

### Local test environment

OrbStack **2.2.5** runs Kubernetes **1.36.5+orb1** on ARM64 here. Its managed host has neither `iscsiadm` nor `iscsid`, and no normal `apt`/`apk` package manager. A deeper inspection confirmed that `iscsi_tcp.ko` and its dependencies **are available**, but not loaded; missing kernel support was not established. [OrbStack added iSCSI kernel support in 1.11.0](https://github.com/orbstack/orbstack/issues/1841). A privileged Docker/`nsenter` shell reaches the managed host; documented `orb`/SSH machine access reaches separate Linux userspaces, so installing packages there does not equip the managed Kubernetes node. Host userspace/daemon setup remains untested. The mockpie overlay therefore still does not select Longhorn; its shared manifest is upgraded for super6, but Longhorn storage operations are **not tested locally**. Local PVC smoke tests use OrbStack's available storage provisioner. The mockpie NetworkPolicy overrides match this node's pod/service range (`192.168.194.0/24`) and API endpoint (`192.168.139.2:26443`); verify those addresses again if the local cluster is recreated.

The local Flux source uses its bootstrap SSH deploy key; the external application source reads its public repository over HTTPS without a deploy key. The old GCP application-repository credential was rejected and is not used by the local source. metrics-server is included locally for Knative HPAs; its development-only patch accepts OrbStack's kubelet certificate without verification. The external infrastructure-test overlay is patched to stable Flux image APIs, and its image-write automation is temporarily suspended; restoring the normal workflow remains pending. Its source files remain in the external repository.

Apply the ignored local `prep/gcpsm-secret.yaml` to the local context before reconciling External Secrets; never commit this credential file.

### Validation results (2026-11-18)

| Check | Result |
| --- | --- |
| Flux 2.10.0 and both local infra Kustomizations | Ready, reconciling `develop` |
| External Secrets and GCP SecretStore | Ready; dashboard, repository, registry, and tunnel credential mappings sync |
| CloudNativePG / Redis | Operators ready; local-path PVCs bound; PostgreSQL and Redis queries succeed |
| metrics-server | Node metrics available; Knative HPA metrics API enabled |
| Knative Serving / Kourier | Independent HTTP receiver responds through Kourier and scales to zero |
| Knative Eventing | Synthetic event traverses the default broker and a Trigger; receiver logs confirm delivery |
| Weave GitOps | Deployment ready and web page returns HTTP 200; authenticated API compatibility is not fully verified |
| Longhorn / NFS provisioner | Not runtime-tested on OrbStack; super6 manifests render |
| Original `testfunc` application | Rebuilt public ARM64/AMD64 image; PostgreSQL and Redis checks pass; direct CloudEvent requests return pong and broker/Trigger delivery is verified. Image repository and policy scans are ready. |
| Cloudflare Tunnel controller | Credential mapping syncs; tunnel created; controller and connector ready after granting tunnel Edit permission. mockpie selects `kube-whoami-dev.vino9.net`; public HTTPS verification is pending. |

The independent Knative receiver/Trigger were temporary test resources used before the original application image was rebuilt. Namespace policies match the standard `kubernetes.io/metadata.name` labels; test clients must carry `local.dev/pod-type: app` to use the application egress rules. Additional Cloudflare routes and authentication require testing once hostnames and Access policies are confirmed.

### Infrastructure test workload

The external `vinobank-gitops/infra-test` overlay deploys PostgreSQL, Redis, a helper pod, and the original [`testfunc`](https://github.com/sloppycoder/testfunc/blob/main/main.py) Knative workload. Its endpoints are:

* `GET /`: a simple running response.
* `GET /check`: connect to PostgreSQL and count public-schema tables, then write/read/delete a temporary Redis key. `?source=db` or `?source=redis` selects one check.
* `POST /`: receive and log a CloudEvent, then return a `dev.vino9.infra.test.infra.pong` reply event.

The old deployment tag was unavailable. The existing [manual build workflow](https://github.com/sloppycoder/testfunc/actions/runs/44266223434) was triggered without changing the source repository, publishing the public multi-architecture tag `main-20261118-162131-705da03`. The local Flux Kustomization overrides the stale external pin with that tag and immutable digest `sha256:6e325606121e4aa40c210160a7a76fbe805ba66f31848f7e2c840127902d9e8b`. No replacement workload was needed. Explicit health checks cover the running test workloads and image scans; intentionally suspended Git-write automation is excluded because it has no Ready condition.

### Certificate and ingress transition

cert-manager (previously 1.18.2), the Let's Encrypt issuer, its Cloudflare DNS credential sync, and the whoami certificate request have been removed. No external-dns deployment existed in this repository. External Secrets Operator remains enabled. Traefik-specific dashboard routes and middleware are removed; no Traefik controller is required. Kourier remains the Knative ingress. mockpie publishes whoami at `kube-whoami-dev.vino9.net` through Cloudflare Tunnel as a public test endpoint. Weave remains internal until its hostname and Access protection are confirmed. Local tests can use direct Service access or port forwarding.

The STRRL controller uses the explicit `cloudflare-tunnel` IngressClass and manages separate tunnels: `k3s-mockpie-dev` locally and `k3s-super6` for super6. It is selected with infra configurations, after External Secrets, to avoid a controller/credential dependency cycle. Credentials come from `infra-secret.cloudflare_api_token` and `infra-secret.cloudflare_account_id` in GCP Secret Manager; External Secrets creates `infra/cloudflare-tunnel-credentials`. Neither value is embedded in the repository. An Ingress publishes a service but does not create Cloudflare Access applications/policies: configure those before selecting any dashboard Ingress.

### New Relic removal

New Relic is no longer selected by either cluster. Its `nri-bundle` HelmRelease (previously chart **6.0.4**), HelmRepository, cluster-name patches, license ExternalSecrets in `infra` and `test`, and sample license field have been removed.

The `infra-configs` Flux Kustomizations have `prune: true`. Once this change reaches each cluster's tracked branch, Flux should prune the old resources and helm-controller should uninstall the New Relic release. **mockpie tracks `develop`; super6 tracks `main`**, so both branches must receive the removal. Verify reconciliation and Helm uninstall completion before treating monitoring as removed. A failed uninstall or an orphaned generated license Secret may need separate cleanup.

The latest GCP `infra-secret` version has also been updated to remove `newrelic_license_key` and add `cloudflare_account_id`, preserving all other fields. Historical Secret Manager versions and ignored local credential files remain unchanged. No replacement monitoring stack is configured by this change.

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

Work on `develop` and test the local mockpie configuration before discussing promotion to `main` for super6. The component upgrades, New Relic/cert-manager removal, local workload tests, and Cloudflare controller installation are complete. Finish the pending work above before promotion; configure Access policies before publishing dashboards.

Flux manifests use stable HelmRelease `v2` and HelmRepository `v1` APIs. Weave GitOps uses an OCIRepository and HelmRelease `chartRef`. The bundle is generated by Flux CLI **2.10.0** for both clusters; this release supports Kubernetes **1.35.2+, 1.36.1+, or 1.37.0+**. The stable Weave GitOps app remains old: its compatibility with these controllers must be verified, rather than inferred from successful chart rendering.

For any later upgrades of a running cluster, follow each component's supported migration procedure and verify restorable backups. In particular, [Longhorn](https://longhorn.io/docs/1.13.0/deploy/upgrade/) and [Knative](https://knative.dev/docs/install/upgrade/upgrade-installation/) have version-step requirements. Keep CRD and core/plugin manifest pins synchronized.

Render affected overlays, commit, and push only the tested development configuration to its tracked branch. Check reconciliation and workload behavior after each deployment change. Local tests do not establish Raspberry Pi hardware or super6 NFS compatibility.

## Common Maintanence Commands

1. force external secret sync
```shell
kubectl annotate es <name> -n <ns> force-sync=$(date +%s) --overwrite
```
