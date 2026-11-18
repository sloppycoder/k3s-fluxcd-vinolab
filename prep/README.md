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
the password in the ```infra-secret``` should the hash of the actual password, to create it
```shell
# on debain, apt install apache2-utils -y
# make sure to use bcrypt, the -B flag

htpasswd -nbB admin admin
admin:$2y$05$70FHgaU08MCO6zkjurXFF.hD28w4g0nOUDfV3xrfuQk63LjUn5STy
```

Then create a ```infra_secret.json``` based on template in ```infra-secret-sample.json```
```shell
# create new secret
gcloud secrets create infra-secret --project project_id --data-file=infra-secret.json

# add a new revision
gcloud secrets versions add infra-secret --project project_id --data-file=infra-secret.json
```


## Cloudflare Tunnel ingress credentials

The `infra-secret` JSON in GCP Secret Manager must contain:

* `cloudflare_account_id`: the Cloudflare account identifier.
* `cloudflare_api_token`: a token scoped to the intended account and zone with **Account: Cloudflare Tunnel: Edit**, **Zone: DNS: Edit**, and **Zone: Zone: Read**.

External Secrets maps these fields into `infra/cloudflare-tunnel-credentials`.
The controller reads that Kubernetes Secret; credentials and the account ID are
not embedded in manifests. Preserve unrelated fields when adding a new secret
version. The obsolete `newrelic_license_key` field is no longer needed.

Cloudflare Access applications/policies are configured separately before
publishing dashboard Ingresses. Local and super6 tunnel names are distinct. Tunnel creation and connector startup
were verified locally after granting the token tunnel Edit permission.
