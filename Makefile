DEST:=/usr/bin
THUMB_FOLDER:=/usr/share/thumbnailers
MIME:=/usr/share/mime

install:
	/usr/bin/python3 -c 'import numpy, PIL' || (echo 'Missing numpy/Pillow, see README.md'; exit 1)
	cp ${CURDIR}/src/mrc-em-thumbnailer.py ${DEST}/mrc-em-thumbnailer
	chmod a+rx ${DEST}/mrc-em-thumbnailer

	cp ${CURDIR}/src/mrc-em-thumbnailer.xml ${MIME}/packages/
	update-mime-database ${MIME}

	mkdir -p ${THUMB_FOLDER}
	cp ${CURDIR}/src/mrc-em.thumbnailer ${THUMB_FOLDER}/
	echo "Installation completed!"

uninstall:
	rm ${DEST}/mrc-em-thumbnailer
	rm ${THUMB_FOLDER}/mrc-em.thumbnailer
	rm ${MIME}/packages/mrc-em-thumbnailer.xml
	update-mime-database ${MIME}

update: uninstall install
