The files in this directory serve as both example code for displaying image streams and scripts for our canary releases.

A **canary release** (or canary launch or canary deployment) allows developers to have features incrementally tested by a small set of users[^1]. To set up these canaries on Debian-based Linux distribution follow the steps below.

#### Install Python3 dependencies 
```bash
$ pip3 install -r requirements.txt
```
#### Create a systemd user instance 
Create an instance in the exact location listed below, filling in the bracketed parameters.
```bash
$ cat ~/.config/systemd/user/canary.service
[Unit]
Description=Canary Launch
After=network-online.target graphical.target
Wants=network-online.target graphical.target

[Service]
RuntimeMaxSec=1hour
Restart=always
TimeoutStartSec=15m
Environment=DISPLAY=:0.0
Environment=PASSWORD=<root_password> 
ExecStartPre=<path to vision-service-examples>/canaries/update
ExecStart=<needs absolute path to Python3, use $(which python3)> <path to vision-service-examples>/canaries/controller.py

[Install]
WantedBy=multi-user.target
```
#### Create a secrets file
This file contains the address the payload arguments for both canary scripts. It MUST be in the location below
```bash
$ cat ~/.canary_secrets.json                         
{
        "canary": {
                "payload": "<payload>",
                "address": "<address>"
        }
}

```

#### Start instance

```bash
$ systemctl --user daemon-reload
$ systemctl --user enable canary.service
$ systemctl --user restart canary.service
```

#### Query instance status 
```bash
$ systemctl --user status canary.service 
```


[^1]: https://en.wikipedia.org/wiki/Feature_toggle#Canary_release