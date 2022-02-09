cd front
quasar build -m spa
mv dist/spa/* ../app/
cd ..
tar -czvf slns.tar.gz app core .env main.py LICENSE
