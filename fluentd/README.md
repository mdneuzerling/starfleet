
```bash
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update

helm install \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/fluentd/values.yaml \
    fluentd fluent/fluentd
```
