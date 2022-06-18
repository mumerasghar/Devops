#!/usr/bin/env python3

import aws_cdk as cdk

from sprint1.sprint1_stack import Sprint1Stack


app = cdk.App()
Sprint1Stack(app, "sprint1")

app.synth()
