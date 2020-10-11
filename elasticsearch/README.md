# Setting up Elasticsearch

As always, [the simplest way to install Elasticsearch is through Helm](https://artifacthub.io/packages/helm/elastic/elasticsearch). The default values assume a scale of cluster that isn't well-suited to a few Raspberry Pis. The `values.yaml` configuration here reduces the memory claim for each pod from 2GB to 512MB. It also reduces the number of replicas from 3 to 2.

With Helm 3:

```bash
Helm install elasticsearch \
    --version 7.9.2 elastic/elasticsearch \
    --values https://raw.githubusercontent.com/mdneuzerling/starfleet/main/elasticsearch/values.yaml
```

Alternatively, [this blog post](https://spot.io/blog/kubernetes-tutorial-successful-deployment-of-elasticsearch/) offers a more in-depth approach. Be aware that the `all-in-one.yaml` file is over 3000 lines long!

## Notes
* Elasticsearch uses terminology like "cluster" and "node" that conflict with Kubernetes terminology.
* Elasticsearch pods (AKA "nodes") take on up to three roles: _master_, _data_, and _ingress_.
  * For small-scale deployments, [it's advisable to assign all three roles to every pod](https://discuss.elastic.co/t/what-is-difference-between-master-node-and-data-node-etc/109896/4), which is the default setting of the Helm chart.
  * I doubt that a Raspberry Pi cluster will ever grow large enough to justify role separation.
* By default Elasticsearch will use 2GB of memory and 30GB of persistent storage **per pod**. This is a rather large memory commitment for 8GB nodes, and perhaps anticipates a scale that I'm unlikely to reach. The `values.yaml` I've configured here reduces the memory limits to 512MB, and similarly reduces the JVM stack size.
  * Storage is cheaper than memory, so I'll leave the 3*30GB volume claim as is.
  * I've borrowed some of this configuration from [the recommended values for installing Elasticsearch on microk8s](https://github.com/elastic/helm-charts/blob/7.9/elasticsearch/examples/microk8s/values.yaml).
  * I've also reduced the number of replicas to 2. I'm sceptical that 3 replicas are needed for such a small-scale deployment (3 worker nodes, 8GB of memory each). If I turn out to be wrong, then it's easy to scale up.
* I've noticed a tendency for applications that depend on Elasticsearch to set up an instance of Elasticsearch when installed through Helm. I have to watch out for this, as there is no justification for more than one Elasticsearch cluster on this Kubernetes cluster.

## Questions
* Why does each pod have its own persistent volume claim? It's perfectly reasonable to ask then where the data for Elasticsearch is being held. Is it duplicated across two PV claims? Are the two PV claims treated as one combined volume when querying Elasticsearch?
  * Supposedly, [replica sets in a deployment share a PV claim, whereas each replica pod in a stateful set has its own PV claim](https://stackoverflow.com/a/53999395/8456369).
  * Suppose we want to scale down by reducing the number of replicas. How do we consolidate the terminating pods' persistent volume claims into those of the remaining pods?
