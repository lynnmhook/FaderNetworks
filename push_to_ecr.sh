#!/bin/bash -x

function create_repo_if_missing() {
    echo "Checking ECR repo $1"
    aws ecr describe-repositories --repository-names $1 > /dev/null 2>&1

    if [ $? -ne 0 ]
    then
        echo "Creating ECR repo $1"
        aws ecr create-repository --repository-name $1 > /dev/null
    fi
}

algorithm_name=platform/fadernetwork

account=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

reponame="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name}"

# Get the login command from ECR and execute it directly
$(aws ecr get-login --region ${region} --no-include-email)

for suffix in base cls trn int; do
    # Prepare repo 
    create_repo_if_missing ${algorithm_name}-${suffix}
    # Build the docker image locally with the image name
    docker build  -t ${algorithm_name}-${suffix} -f Dockerfile-${suffix} . --build-arg BASEIMAGE=${algorithm_name}-base
    # tag it with full name including ECR repo prefix 
    docker tag ${algorithm_name}-${suffix} ${reponame}-${suffix}
    # and push to ECR
    docker push ${reponame}-${suffix}
done   


