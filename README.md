<p align="center">
    <img src="logo.svg" style="width: 100pt; background: white; border-radius: 30pt; border: 5pt solid black" alt="StaticPIE" />
</p>
<p align="center">
    <em>Simple web-based scanner interface.</em>
</p>

# Simple Linux Network Scanner

<img src="screenshots/04-cropping.png" width="300">

This is simple web-based scanner interface. It allows share the scanner via IP address which makes it accessible by web browser. The frontend interface allows user to crop the image as well as browse previousely scanned images.

From technical perspective it is simply SANE scanimage wrapper. There are quite many things to do to make it production (see TODO section).

## Requirements

- Python >= 3.8
- SANE (Scanner Access Now Easy) properly configured
- `scanimage` tool
- [Optionally] NPM (for frontend app building)

## Build app

```
sh build.sh
```

## Run

```
mkdir -p slns && \
tar -C slns -xvzf slns.tar.gz && \
cd slns && \
vim .env && \
python slns.py
```

_You will have to replace IP address with appropirate one in `.env` file_

## Screenshots

<img src="screenshots/01-welcome-screen.png" width="300">
<img src="screenshots/02-scanning-params.png" width="300">
<img src="screenshots/03-scanning-progress.png" width="300">
<img src="screenshots/04-cropping.png" width="300">
<img src="screenshots/05-menu.png" width="300">
<img src="screenshots/06-list.png" width="300">

## TODO:

- [ ] error handling
- [ ] pip package
- [ ] automatically add service with `systemctl`
- [ ] better user interface (i.e. image remove button)
- [ ] move actions to vuex
