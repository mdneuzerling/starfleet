```bash
helm repo add influxdata https://helm.influxdata.com/
helm repo update
helm install \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/influxdb/influxdb.yaml \
    influxdb influxdata/influxdb
```
