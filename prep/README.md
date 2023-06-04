# Prerequisites

## create secret to allow access GCP secret manager

this is required for external-secret-operator to sync secrets from GCP to local K8S cluster.

```shell

# create gcpsm-secret.yaml file using gcpsm-secret-example.yaml
# replace the content with your GCP json key
kubectl create namespace infra
kubectl apply -f gcpsm-secret.yaml -n infra
```

## create an secret in GCP secret manager

```shell

printf ' {"newrelic_license_key":"new_relic_api_key", \
    "gitops_username": "<your gitopts console user name>", \
    "gitops_password": "<your gitopts console password hash>"}' > infra_secret.json

gcloud secrets create infra-secret --project vino9-276317 --data-file=infra-secret.json

```
