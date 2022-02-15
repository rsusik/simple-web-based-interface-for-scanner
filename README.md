<p align="center">
    <img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/logo.svg" style="background: white; border-radius: 30pt; border: 5pt solid black" alt="StaticPIE"  width="150" />
</p>
<p align="center">
    <em>Simple Web-based Interface for Scanner</em>
</p>

<p align="center">
<a href="https://pypi.org/project/swis" target="_blank">
    <img src="https://img.shields.io/pypi/v/swis?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://github.com/rsusik/simple-web-based-interface-for-scanner/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/rsusik/simple-web-based-interface-for-scanner" alt="License">
</a>
</p>

<p align="center" style="margin-top: 20pt;">
    <img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/04-cropping.png" width="300">
</p>

This is a simple web-based interface for scanners. It allows sharing the scanner via IP address, making it accessible by the web browser. The frontend interface allows users to crop the image and browse previously scanned images.

From a technical perspective, it is simply a SANE scanimage wrapper. There are quite many things to do to make it production (see TODO section).

## Requirements

- Linux
- SANE (Scanner Access Now Easy) properly configured (`scanimage` tool)
- Python >= 3.8
- [Optionally] NPM (for frontend app building)

## Install and run (local user)
```
pip install swis
swis --ip localhost --port 5520
```

If successfully executed visit the http://localhost:5520 (Note: `http` (without `s`))

**❗IMPORTANT❗** Change the IP (`localhost` above) to a proper host IP address if you want to access the scanner from other computers (or other devices).

## Install and run (system service)

### Prerequisites
This process requires root privileges, and you need to have Python>=3.8 installed. If the root user does't have the the `pip` installed, you will have to install it by running the below:

- Fedora (and similar): `sudo dnf install python3-pip`
- Ubuntu (and similar): `sudo apt-get install python3-pip`

### Install and start service

```
sudo pip3 install swis
sudo swis --ip [HOST IP ADDRESS] --port 5520 -u [USER] -g [GROUP] service install 
sudo swis service start
```

You can check the status by running: `sudo swis service status`

**❗IMPORTANT❗** Change the IP (`[HOST IP ADDRESS]` above) to a proper host IP address, and `[USER]` and `[GROUP]` to a proper system user (owner of scanned documents).


## Screenshots

### Welcome screen
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/01-welcome-screen.png" width="300">

### Scanning parameters
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/02-scanning-params.png" width="300">

### Scanning in progress
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/03-scanning-progress.png" width="300">

### Cropping scanned image
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/04-cropping.png" width="300">

### Side menu
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/05-menu.png" width="300">

### List of scanned images
<img src="https://github.com/rsusik/simple-web-based-interface-for-scanner/raw/main/screenshots/06-list.png" width="300">


## TODO:

- [ ] error handling
- [x] pip package
- [x] automatically add service with `systemctl`
- [ ] better user interface (i.e. image remove button, save as pdf, etc.)
- [ ] move actions to vuex (frontend)

