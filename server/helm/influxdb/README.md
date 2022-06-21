Setup InfluxDB database

```
helm repo add influxdata https://helm.influxdata.com/
helm upgrade --install -n local  -f values.yaml influxdb influxdata/influxdb
```