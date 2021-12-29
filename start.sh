cp -r ../dixit-web/build/ react_build
pipenv run gunicorn server:app -w=1 -b 0.0.0.0:5000 --threads 8