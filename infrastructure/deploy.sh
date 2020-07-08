#!/usr/bin/env bash

set -e
set -u

cd $(dirname $0)

# Configuration
CodeCommitRepoName=s3-datasync-task-scheduler
StackName=s3-datasync-task-scheduler-infrastructure
BucketName=s3-datasync-task-scheduler-infrastructure
Region=us-west-2

# Package and deploy
aws cloudformation package \
--template-file project.yaml \
--s3-bucket ${BucketName} \
--output-template-file packaged-${StackName}-template.yaml \
--region ${Region}

aws cloudformation deploy \
--stack-name ${StackName} \
--template-file packaged-${StackName}-template.yaml \
--parameter-overrides \
"CodeCommitRepoName=${CodeCommitRepoName}" \
--s3-bucket ${BucketName} \
--capabilities CAPABILITY_IAM \
--region ${Region}

# Display CodeCommit repository URL
aws codecommit get-repository --repository-name ${CodeCommitRepoName} \
--region ${Region} \
--output text | awk '{print $4}'
