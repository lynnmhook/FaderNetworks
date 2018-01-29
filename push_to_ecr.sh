#!/bin/bash

algorithm_name=platform/fadernetwork

account=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

fullname_classifier="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name}-cls:latest"
fullname_train="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name}-trn:latest"

aws ecr describe-repositories --repository-names "${algorithm_name}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${algorithm_name}" > /dev/null
fi

# Get the login command from ECR and execute it directly
$(aws ecr get-login --region ${region} --no-include-email)

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build  -t ${algorithm_name}-cls -f Dockerfile_classifier .
docker tag ${algorithm_name}-cls ${fullname_classifier}

docker push ${fullname_classifier}
echo "Image:"
echo $fullname_classifier
