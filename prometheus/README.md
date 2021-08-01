```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/prometheus/kube-prometheus-stack.yaml \
    kube-prometheus-stack prometheus-community/kube-prometheus-stack
```
