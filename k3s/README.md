# k3s

## What is this and what is it used for?



## How do I install it?

There's a good supply of available guides for installing Kubernetes on a Raspberry Pi cluster. My two main sources were from [opensource.com](https://opensource.com/article/20/3/kubernetes-raspberry-pi-k3s) and [Learn Linux](https://wiki.learnlinux.tv/index.php/Setting_up_a_Raspberry_Pi_Kubernetes_Cluster_with_Ubuntu_20.04#Configure_boot_options). The latter goes through the process of installing a full Kubernetes distribution, rather than k3s, but I found [the accompanying video](https://www.youtube.com/watch?v=qv3_gLvjITk) pretty helpful.

This installation was the first software component of the cluster, starting with a freshly installed operating system. I used _Ubuntu_, rather than the standard _Raspberry Pi OS_ (formely known as _Raspbian_), because I wanted a 64-bit operating system. A 32-bit operating system can address only 4GB of memory (actually a little less), whereas my nodes have 8GB. The 64-bit version of Raspberry Pi OS is still under development and I was already familiar with Ubuntu servers, so it was an easy choice.

## Imaging the MicroSD cards and setting hostnames

Raspberry Pis boot from MicroSD cards by default. I picked up a few 128GB MicroSD cards, although in retrospect I think I could have gotten away with less storage. I needed to _image_ these cards, that is, I needed to put operating systems for the Pi on them.

On my laptop I downloaded the excellent [Raspberry Pi Imager](https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/) which made the process very simple. This supports imaging a variety of operating systems, including 64 bit Ubuntu Server. It can be a little slow to image the cards sometimes, so I suggest doing it while you're watching a movie.

While I had the MicroSD cards in my computer, I also set the _hostnames_ for the devices. These are names for the computer that are made available over the network. This way I could SSH into the machines by typing `ssh mdneuzerling@intrepid` rather than `ssh mdneuzerling@192.168.1.21`. The hostnames should be unique to each machine, and configuring them involves two steps:

1. Altering the top section of `/etc/hosts` to look like this:
```
127.0.0.1 localhost
127.0.1.1 intrepid
```
1. Changing the value set in `/etc/hostname` to the desired hostname (the default is ubuntu).

Both of these steps could be done while the MicroSD was still plugged into my (Ubuntu) laptop.

I also plugged the Raspberry Pis in one at a time and assigned them each a static IP address through my router configuration tool. This isn't strictly necessary since the hostnames should be sufficient to identify the devices, but it seemed like a fair precaution.

## (Optional) Booting from USB

MicroSD is not a great choice of media for a bootable drive. They're slow and flimsy --- occasionally failing within months. For the worker nodes this high failure rate is only an annoyance: I would be able to get a new card, copy the contents from another worker node, and off I go. But for the primary node with the control plane, I wanted a bit more stability.

A better option is to boot from an external SSD connected via USB. A 120GB SSD and an external caddy together cost about AUD 70. Despite the label on the button, the Raspberry Pi Imager can flash an SSD just as easily as it can a MicroSD.

A Raspberry Pi 4 can output a total of 1.4A through its USB ports, which is _probably_ enough for one SSD, but _probably not_ two. I wanted to use a second SSD for persistent storage for the cluster, so I `ended up buying a dual-bay dock with its own power supply to overcome this restriction.

[Support for booting from USB is fairly new](https://github.com/raspberrypi/rpi-eeprom/issues/28) and I had some trouble in getting it working. If you're reading this in 2021 or beyond, consider searching for more recent information before following what I did.

I initially followed [this guide](https://www.tomshardware.com/how-to/boot-raspberry-pi-4-usb) up to and including step 13. This required a copy of Raspberry Pi OS flashed to a microSD card. I have a few spare cards lying around, so I flashed a 32GB card with this operating system to keep as a backup.

Afterwards, I removed the microSD card and plugged in my Ubuntu hard drive. Unfortunately, it still wouldn't boot! My suspicion is that this would have been sufficient to boot the official Raspberry Pi OS via USB, but my Ubuntu operating system needed a little more tinkering. Fortunately, [the steps in this guide](https://www.raspberrypi.org/forums/viewtopic.php?t=281152) were enough to encourage the Pi to boot from my Ubuntu SSD. I may need to repeat them in the future if I ever upgrade the operating system, but that's a problem for future David.

## Firewalls

I had a lot of firewall trouble when I was setting up various services on the cluster --- [trouble that could have been saved had I just read the manual](https://rancher.com/docs/rancher/v2.x/en/installation/requirements/ports/). If I could go back in time, I would tell myself the following:

* Open up the SSH port (22/TCP) on all nodes
* Open up the Flannel VXLAN port (8472/UDP) on all nodes
* Open up the metrics server port (10250/TCP) on all nodes
* Open up the Kubernetes port (6443/TCP) on the server node only
* Open up the NFS (Network File System) port (2049) on the server node only

The tool I used for this is Uncomplicated Firewall (UFW), which I believe is installed but not enabled by default on Ubuntu server. It's very import to open up the SSH port **before** enabling the firewall, otherwise the machine will no longer accept SSH connections.

When I connect a machine to my network, the router's DHCP server assigns an IP address of the form 192.168.2.x. The CIDR notation for this is 192.168.2.0/24. This range is reserved for local IP addresses only, so by opening up firewall access to IP addresses in this range only I can restrict access from the outside world. My router also has a firewall which should be blocking access to these ports from the outside world as well.

The NFS ports will allow me to serve a network file system from the Raspberry Pi that hosts the server node. I'll use this as persistent storage for the pods in the cluster. I don't want this storage to visible to the local network in general, so I'll restrict its access only to the four static IP addresses I assigned to the nodes. I'm treating these four IP addresses as a "sub-range" of 192.168.2.0/24 that's reserved for the Kubernetes cluster.

I SSH'd into the Raspberry Pi hosting the server node and implemented the rules like so:

```
sudo ufw allow from 192.168.2.50 to any port nfs
sudo ufw allow from 192.168.2.51 to any port nfs
sudo ufw allow from 192.168.2.52 to any port nfs
sudo ufw allow from 192.168.2.53 to any port nfs
sudo ufw allow from 192.168.2.0/24 to any port ssh
sudo ufw allow proto tcp from 192.168.2.0/24 to any port 6443
sudo ufw allow proto udp from 192.168.2.0/24 to any port 8472
sudo ufw allow proto tcp from 192.168.2.0/24 to any port 10250
```

Afterwards I enabled the firewall with `sudo ufw enable`. I can check that the firewall is running with `sudo ufw status`:

```
To                         Action      From
--                         ------      ----
2049                       ALLOW       192.168.2.50
2049                       ALLOW       192.168.2.51
2049                       ALLOW       192.168.2.52
2049                       ALLOW       192.168.2.53
22/tcp                     ALLOW       192.168.2.0/24
6443/tcp                   ALLOW       192.168.2.0/24
8472/udp                   ALLOW       192.168.2.0/24
10250/tcp                  ALLOW       192.168.2.0/24
```

I repeated the process on each of the Raspberry Pis hosting the worker nodes, implementing only the necessary rules:

```
sudo ufw allow from 192.168.2.0/24 to any port ssh
sudo ufw allow proto udp from 192.168.2.0/24 to any port 8472
sudo ufw allow proto tcp from 192.168.2.0/24 to any port 10250
```

And after `sudo ufw enable` and `sudo ufw status`:

```
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       192.168.2.0/24
8472/udp                   ALLOW       192.168.2.0/24
10250/tcp                  ALLOW       192.168.2.0/24
```