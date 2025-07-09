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
