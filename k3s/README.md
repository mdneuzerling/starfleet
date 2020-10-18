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
