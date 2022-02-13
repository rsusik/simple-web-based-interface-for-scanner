cd front && \
quasar build -m spa && \
rm -rf ../swis/app/* && \
mv dist/spa/* ../swis/app/ && \
cd .. && \
tar -czvf swis.tar.gz swis LICENSE README.md requirements.txt
