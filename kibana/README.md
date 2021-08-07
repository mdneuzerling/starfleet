```bash
helm repo add elastic https://helm.elastic.co
helm repo update

helm install \
    -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/kibana/values.yaml \
    elasticsearch elastic/kibana 
```

```bash
kubectl apply -f https://raw.githubusercontent.com/mdneuzerling/starfleet/main/kibana/kibana-nodeport.yaml
```