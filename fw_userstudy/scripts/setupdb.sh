python clear_all.py
cd ../
python manage.py syncdb
cd scripts
python prepare_data.py
python setup_experiment.py
