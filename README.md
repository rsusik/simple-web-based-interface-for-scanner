# Simple Linux Network Scanner

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
mkdir slns
cd slns
tar -xvzf slns.tar.gz
vim .env # replace the IP address
python main.py
```

## TODO:

- [ ] error handling
- [ ] pip package
- [ ] automatically add service with `systemctl`
- [ ] better user interface (i.e. image remove button)
- [ ] move actions to vuex
