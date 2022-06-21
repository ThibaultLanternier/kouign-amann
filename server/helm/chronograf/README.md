How to setup Chronograf (InfluxDB UI)

```
helm repo add influxdata https://helm.influxdata.com/
helm upgrade --install -n local -f values.yaml chronograf influxdata/chronograf
```