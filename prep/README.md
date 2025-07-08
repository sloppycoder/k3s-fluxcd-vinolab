# Prerequisites

*** the following steps must be done prior to bootstrap fluxcd in the cluster ***

## create secret to allow access GCP secret manager

this is required for external-secret-operator to sync secrets from GCP to local K8S cluster.

```shell

# create gcpsm-secret.yaml file using gcpsm-secret-example.yaml
# replace the content with your GCP json key
kubectl apply -f gcpsm-secret.yaml -n infra
```

## create GCP secret for credentials to dashboards and etc

```shell

# create a ```infra_secret.json``` based on template in ```infra-secret-sample.json```, then

gcloud secrets create infra-secret --project project_id --data-file=infra-secret.json

```
