# GitOps setup with FluxCD for K3S Kuberentes clusgter

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
* ```clusters``` contains the overlay for each cluster under management. each cluster will incldue all components in ```base``` and select components in ```optional```. see [super6 cluster](infra/controllers/clusters/super6/kustomization.yaml) as an example

#### [infra/configs](infra/configs)

Infra configurations that depends on CRD in the ```controllers``` direcrory. The directory structure is similiar to ```controllers``` directory.
The ```namespaces``` diretory cotnains individual namespaces that will be created and their associated configuration, including networkpolicy that blocks communication between namespaces except for ones that runs shared components, e.g. infra. see [an example network policy](infra/configs/namespaces/vinobank/network-policy.yaml) here.

The ```clusters``` contains configs for each cluster, each cluster will include configs in ```base``` directory, selected components from ```optional``` directory and selected namespaces that the cluster should host, see [an example cluster config](infra/configs/clusters/super6/kustomization.yaml) here.

### Components

The following components are managed by FluxCD:

* [external-secrets](https://external-secrets.io/) for syncing secrets from external source (e.g. GCP) to the cluster
* [Longhorn](https://longhorn.io) for persistent storage
* [nfs-subdir-external-provisioner](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner) for using NFS based persistent volumes.
* [cert-manager](https://cert-manager.io/) setup to works with [Let's Encrpt](https://letsencrypt.org/)
* [nats streaming](https://nats.io/) light-weigh high performance streaming
* [CloudNativePG PostgreSQL operator](https://cloudnative-pg.io/) for setting up HA PostgreSQL database instances
* [New Relic](https://newrelic.com) for infra monitoring, mainly for simpler pricing model on data upload, unlike Datadog's convulated licensing model.

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

Checkout this repo, update various varion numbers, commit and push. FluxCD will upgrade components according. Follow [this step](https://longhorn.io/docs/1.9.0/deploy/upgrade/upgrade-engine/) after a version upgrade for Longhorn.
