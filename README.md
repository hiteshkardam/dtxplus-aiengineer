# dtxplus-aiengineer
Take Home Assignment for DTX+ AI Engineer Role

# Setup (using arch linux and conda env)
conda env create -f environment.yml<br/>
pip install -r requirements.txt<br/>

Created using:<br/>
conda env export --from-history > environment.yml<br/>
pip freeze > requirements.txt<br/>

# Local instance
docker-compose up -d<br/>
python dtxplus_patient_chat/manage.py runserver<br/>
