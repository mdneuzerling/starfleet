
There are many ways to make the Raspberry Pi run a Python script automatically on startup. My method involved creating a file `~/.config/autostart/environment.desktop` with the following contents:

```bash
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=environment
Comment=
Exec=authbind --deep python3 /home/.pi/starfleet/environment/environment.py
```

Note the use of `authbind` here --- the server runs on port 80, which is usually protected, but `authbind` allows its use. The following command configures `authbind`:

```bash
sudo touch /etc/authbind/byport/80
```

I only want to be able to access the server from within my local network. The below command sets up a firewall rule that allows this. The `192.168.0.0/22` range works for me, but may need to be adjusted for individual networks to cover the range of IP addresses offered by the router.

```bash
sudo ufw allow from 192.168.0.0/22 to any port 80 proto tcp
```

Another rule might exist on port 22, to allow for SSH access. Otherwise, the intention is that this device is locked down and serves only a single purpose.

By default, UFW blocks all incoming connections and allows all outgoing connections. One option here, to lock the Pi down even further, would be to block all outgoing connections. This would disconnect the device from the internet (and also from updates). I'm not convinced that this is necessary, but the command is:

```bash
sudo ufw default deny outgoing
```
