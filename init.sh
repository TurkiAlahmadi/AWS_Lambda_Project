# install specific python version
sudo apt update
sudo apt install python3.8 -y

# install awscli
sudo apt install awscli -y

# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# deactivate the virtual environment
deactivate

# make run.sh executable
chmod a+x run.sh

# create log directory if it doesn't exist
mkdir -p log

# create lambda-layer directory
mkdir lambda-layer
