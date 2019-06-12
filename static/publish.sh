#!/bin/bash

AWSPROFILE=bdl-backend-publish
BUCKET=static.bazardelux.com

unset AWS_DEFAULT_REGION
unset AWS_SECRET_ACCESS_KEY
unset AWS_ACCESS_KEY_ID

echo "=> Checking that awscli is installed"
which aws >/dev/null
RES=$?
if [ $RES != 0 ]; then
    echo ""
    echo "ERROR: The aws cli is not installed"
    echo "please run: pip install awscli"
    echo ""
    exit 1

fi

echo "=> Checking that $AWSPROFILE is configured"
aws configure list --profile $AWSPROFILE
RES=$?
if [ $RES != 0 ]; then
    echo ""
    echo "ERROR: AWS profile $AWSPROFILE is not configured"
    echo "please run: aws configure --profile $AWSPROFILE"
    echo ""
    exit 1
fi

# are we really in the project's root?
GIT_ROOT_DIR=$(git rev-parse --show-toplevel)
if [ -z "$GIT_ROOT_DIR" ]; then
    echo "ERROR: you are not in the website's root directory, or it is not a git clone"
    exit 1
fi

echo "Synching to aws S3..."
aws s3 sync $GIT_ROOT_DIR/static s3://$BUCKET/ \
    --profile $AWSPROFILE \
    --exclude ".git/*" \
    --exclude "publish.sh" \
    --exclude "tmp/*" \
    --exclude "README.md" \
    --exclude "psd/*" \
    --exclude "*.xml" \
    --cache-control max-age=86600,public \
    --expires 2034-01-01T00:00:00Z \
    --acl public-read \
    --delete
