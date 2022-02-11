cd front && \
quasar build -m spa && \
rm -rf ../app/* && \
mv dist/spa/* ../app/ && \
cd .. && \
tar -czvf swis.tar.gz app core .env swis.py LICENSE
