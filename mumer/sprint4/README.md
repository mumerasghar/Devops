# Devops Sprint4

Sprint3 was mostly about introduction of aws CI/CD: creating pipelines, adding application metrics and deployment groups for deployment of application.

To go forward with the work of this sprint we have used amazon cdk, it is installed using the following command

```
npm install -g aws-cdk
```

Initialization of basic project will be done using the command

```
cdk init app --language python
```

synth init will autmatically create a .venv environment file which can be activated with the use of following command.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

Since our work is build upon the application stack of sprint2 copy resoucrs folder from sprint3 to sprint4

```
$ cp resources ../sprint3/
```

Since we are creating a pipeline, we need to deploy the pipeline, it in turn will deploy our application. To that end run

```
$ cdk deploy mumer-Sprint4-PipelineStack
```

Make sure to push code to github before deploying pipleine.

## My progress in sprint4

1. Worked on CI/CD pipeline for web health lambda.
2. Created a pipeline stack and restructured the sprint2 into sprint3: by moving resources from sprint2 to sprint3.
3. Added different stages in pipeline, CodeSource, CodeBuild, AlphaTesting stage(unit tests), BetaTesting(functional tests), and Prod Stage.
4. Wrote unit tests to validate individual constructs usage in stack.
5. Created AWS Alarms in `sprint4/sprint3_stack.py` to monitor lambda real time performance.
6. Lambda alarms work as a policy, if alarms went off application will rollback to previous version.
