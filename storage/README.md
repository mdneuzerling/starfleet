# Storage

## What is this and what is it used for?

Deployments that run _stateful_ services like databases have data that must persist beyond the life of any single pod. This kind of storage requires a _persistent volume_. Pods can make a _persistent volume claim_ for a given amount of storage, and Kubernetes will assign that amount from the available persistent volumes.

## How do I install it?

```bash
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
    --set nfs.server=192.168.2.50 \
    --set nfs.path=/media/cargobay
```

## Notes

* It took me a while to realise this: each persistent volume claim needs its own persistent volume (at least, with "ReadWriteOnce"). A claim will choose "the most appropriate" volume --- I _hope_ that this means the smallest volume meeting the storage class and capacity. requirements.
* To continue the Star Trek theme, I'll be calling my persistent volumes
* In general, persistent volumes are cloud storage. Here, I'm using an SSD as a _local persistent volume_.
    * Local persistent volumes [reached general availability in 2019](https://kubernetes.io/blog/2019/04/04/kubernetes-1.14-local-persistent-volumes-ga/).
    * I'm using a single SSD. To mitigate the damage done by drive failure, I should be using two in a RAID.
* Raspberry Pi 4s can output a total of 1.4A across all USB ports. Based on some superficial Googling, this should be enough to support one USB-powered SSD, but not two. The _starfleet_ Raspberry Pi with my control plane uses two SSDs: one for its file system, and another for the persistent volume. I use a dual-bay powered dock for the drives so that I don't need to worry about the 1.4A limit.
* Two elements are required:
    * A [storage class](https://kubernetes.io/docs/concepts/storage/storage-classes/) defines the kind of storage offered by the cluster.
    * A [persistent volume](https://kubernetes.io/docs/concepts/storage/storage-classes/) is a _cluster-level_ volume used for persistent storage.
* The `nodeAffinity` for the persistent volume links the volume to the _starfleet_ node, which is the machine to which the SSD is physically connected.
    * If the node with the SSD becomes unavailable, so will the volume. However, the _starfleet_ node is the sole location of the control plane, so this doesn't introduce any new risk.
* `WaitForFirstConsumer` means that the volume will not be _bound_ until a deployment makes a persistent volume claim.
* `ReadWriteOnce` means that only a single node can mount the volume with read-write privileges.

## Questions

* I'm still a little unsure about how the storage class and persistent volume interact here, or why I need to specify a storage class at all.
* Persistent volume claims also have access policies like `ReadWriteOnce`. Is this an entirely separate concept?
