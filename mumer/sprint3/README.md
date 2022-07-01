
# Devops Sprint3 

Sprint3 was mostly about introduction of aws CI/CD: creating pipelines, adding application metrics and deployment groups for deployment of application.

To go forward with the work of this sprint we have used amazon cdk, it is installed using the following command

```
npm install -g aws-cdk
```

Initialization of basic project will be done using the command 
```
cdk init app --language python
```

### synth init will autmatically create a .venv environment file which can be activated with the use
### of following command.

```
$ source .venv/bin/activate
```

### Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

### Since our work is build upon the application stack of sprint2 copy resoucrs folder from sprint2 to sprint3
```
$ cp resources ../sprint3/
```


### Since we are creating a pipeline, we need to deploy the pipeline, it in turn will deploy our application. To that end run 
```
$ cdk deploy mumer-Sprint3-PipelineStack
```
Make sure to push code to github before deploying pipleine.