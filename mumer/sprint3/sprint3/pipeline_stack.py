from aws_cdk import(
    Stack,
    pipelines as pipelines_,
    aws_codepipeline_actions as pipelineactions_
)

import aws_cdk as cdk
from constructs import Construct
from sprint3.pipeline_stage import MyStage


class MyPipeLineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source = pipelines_.CodePipelineSource.git_hub(
            "mumer23229/Pegasus_Python", "main",
            authentication=cdk.SecretValue.secrets_manager('MyAwsSecret'),
            trigger=pipelineactions_.GitHubTrigger("POLL")
        )

        synth = pipelines_.ShellStep(
            "CodeBuild",
            input=source,
            commands=[
                'cd  mumer/sprint3/',
                'npm install -g aws-cdk',
                "pip install -r requirements.txt",
                "cdk synth"
            ],
            primary_output_directory="Pegasus_Python/sprint3/cdk.out"
        )

        code_pipeline = pipelines_.CodePipeline(
            self,
            "mumer-pipeline",
            synth=synth
        )

        unit_test = pipelines_.ShellStep(
            "UnitTesting",
            input=source,
            commands=[
                "cd mumer/sprint3/",
                "pip install -r requirements.txt -r requirements-dev.txt",
                "pytest" 
            ]
        )

        code_pipeline.add_stage(
            MyStage(self, "mumer-alphatesting"),
            pre=[
                unit_test
            ]
        )
         
        code_pipeline.add_stage(
            MyStage(self, "mumer-prodstage"),
            pre=[
                pipelines_.ManualApprovalStep("Pre-Stack Check")
            ]
        )

    