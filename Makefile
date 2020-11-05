DEST:=/usr/bin
THUMB_FOLDER:=/usr/share/thumbnailers
MIME:=/usr/share/mime

install: clean_cache
	/usr/bin/pip3 install -r requirements.txt
	cp ${CURDIR}/src/mrc-thumbnailer.py ${DEST}/mrc-thumbnailer
	chmod a+rx ${DEST}/mrc-thumbnailer

	cp ${CURDIR}/src/mrc-thumbnailer.xml ${MIME}/packages/
	update-mime-database ${MIME}

	cp ${CURDIR}/src/mrc.thumbnailer ${THUMB_FOLDER}/
	echo "Installation completed"

uninstall:
	rm ${DEST}/mrc-thumbnailer
	rm ${THUMB_FOLDER}/mrc.thumbnailer
	rm ${MIME}/packages/mrc-thumbnailer.xml

update: uninstall install

clean_cache:
	rm -rf /home/ilja/.cache/thumbnails/fail
