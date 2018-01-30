#!/bin/bash

algorithm_name_train=platform/fadernetwork-trn
algorithm_name_classifier=platform/fadernetwork-cls

account=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

fullname_classifier="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name_classifier}:latest"
fullname_train="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name_train}:latest"

aws ecr describe-repositories --repository-names "${algorithm_name_classifier}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${algorithm_name_classifier}" > /dev/null
fi

aws ecr describe-repositories --repository-names "${algorithm_name_train}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${algorithm_name_train}" > /dev/null
fi


# Get the login command from ECR and execute it directly
$(aws ecr get-login --region ${region} --no-include-email)

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build  -t ${algorithm_name_classifier} -f Dockerfile_classifier .
docker tag ${algorithm_name_classifier} ${fullname_classifier}
docker push ${fullname_classifier}

echo "Classifier image:"
echo $fullname_classifier

docker build  -t ${algorithm_name_train} -f Dockerfile_train .
docker tag ${algorithm_name_train} ${fullname_train}
docker push ${fullname_train}

echo "Training image:"
echo $fullname_train
