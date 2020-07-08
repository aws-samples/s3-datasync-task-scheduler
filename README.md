# s3-datasync-task-scheduler

AWS SAM application which creates and executes DataSync tasks when a task definition CSV file is uploaded to S3.

## Requirements

**For deployment**

* AWS CLI installed and configured for your environment
* Git installed and configured

**For local development**

* [Pipenv installed](https://github.com/pypa/pipenv)
* Python 3.8. You can install this with [Pyenv](https://github.com/pyenv/pyenv).
    ```
    pyenv install 3.8.0
    cd src/get
    pipenv --python ~/.pyenv/versions/3.8.0/bin/python3.8
    ```

## Initial setup & deployment

**Prepare the infrastructure**

1. Create an S3 bucket to store the CloudFormation templates stored in the `infrastructure` directory.
```bash
aws s3 mb s3://s3-datasync-task-scheduler-infra-<YOUR_COMPANY>
```

2. Edit `infrastructure/deploy.sh` and set the `BucketName` variable to match the bucket you created in step 1.
 
3. Deploy the infrastructure
```bash
make infra
```

4. Take note of the CodeCommit repo URL, you will need this for deployment.

**Deploy the solution**

1. Update the CloudWatch Log Group ARN environment variables info in the `template.yaml` file to match your environment.
    - LOG_GROUP_ARN: this is where DataSync Tasks will send their logs

2. Add a new git remote and point it at the CodeCommit repo created during infrastructure deployment.
```bash
git remote add codecommit <codecommit-clone-url-http>
```

3. Push your changes and the pipeline should kick off a build.
```bash
git push -u codecommit master
```

4. Look in CloudFormation to see the Stack details, including important information such as the S3 bucket used to initiate the DataSync task creation process.

## Usage

1. Create a UTF-8 encoded CSV file, use the `sample-data/task-definitions.csv` file as a reference.
    - The `SourceLocationArn` and `DestinationLocationArn` fields are _REQUIRED_.
2. Upload the CSV file to the S3 bucket created during the "Deploy the solution" step.
3. Navigate to the DataSync console to oversee the task executions.
