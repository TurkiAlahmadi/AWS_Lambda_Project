mkdir -p lambda-layer/aws-layer/python/lib/python3.8/site-packages && cd lambda-layer
pip3 install -r requirements.txt --target aws-layer/python/lib/python3.8/site-packages
cd aws-layer && zip -r9 lambda-layer.zip .
aws lambda publish-layer-version \
    --layer-name LambdaProject \
    --description "Lambda mini-project layer" \
    --zip-file fileb://lambda-layer.zip \
    --compatible-runtimes python3.8