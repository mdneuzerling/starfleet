
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/fluentd/values.yaml \
    fluentd bitnami/fluentd

helm apply \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/fluentd/elasticsearch-output.yaml.yaml
```