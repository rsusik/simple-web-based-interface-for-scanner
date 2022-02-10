cd front && \
quasar build -m spa && \
rm -rf ../app/* && \
mv dist/spa/* ../app/ && \
cd .. && \
tar -czvf slns.tar.gz app core .env slns.py LICENSE
