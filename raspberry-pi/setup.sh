#!/usr/bin/env bash
#Warning this installs pulseaudio as root unfortunately this needs to be done for stability
# https://mendel-nykorowycz.pl/2021/05/01/raspberry-pi-debian-a2dp-sink-or-how-to-make-your-own-bluetooth-speaker/
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

apt install python3 python3-pip libopenjp2-7 libtiff5 zlib1g-dev libjpeg-dev pulseaudio-module-bluetooth bluez


#Create /etc/systemd/system/pulseaudio.service
if [ -f "/etc/systemd/system/pulseaudio.service" ]; then
   echo "/etc/systemd/system/pulseaudio.service found"
else
   cat <<- EOF > /etc/systemd/system/pulseaudio.service
[Unit]
Description=Pulseaudio sound server
After=avahi-daemon.service network.target

[Service]
ExecStart=/usr/bin/pulseaudio --system --disallow-exit --disable-shm --daemonize=no
ExecReload=/bin/kill -HUP $MAINPID
User=root
Group=pulse
UMask=007

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl enable pulseaudio

if grep -q -wi "module-bluetooth-policy" /etc/pulse/system.pa; then
   echo "module-bluetooth-policy already loaded"
else
   cat <<- EOF >> /etc/pulse/system.pa
.ifexists module-bluetooth-policy.so
load-module module-bluetooth-policy
.endif
EOF
fi

if grep -q -wi "module-bluetooth-discover" /etc/pulse/system.pa; then
   echo "module-bluetooth-discover already loaded"
else
   cat <<- EOF >> /etc/pulse/system.pa
.ifexists module-bluetooth-discover.so
load-module module-bluetooth-discover
.endif
EOF
fi

adduser pulse bluetooth
adduser root bluetooth
adduser root pulse
adduser root pulse-access
systemctl restart dbus
systemctl start pulseaudio
