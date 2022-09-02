How to setup MongoDB database

Using the bitnami Helm Chart

Add the bitnami repo to Helm
```
helm repo add bitnami https://charts.bitnami.com/bitnami
```

Install the chart
```
helm upgrade --install -n local -f mongodb/values.yaml mongodb-local bitnami/mongodb
```
