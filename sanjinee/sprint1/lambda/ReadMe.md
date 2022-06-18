# Complete set-up of lambda function using python!

`Python Lambda Function` development with CDK in Using local machine.
As we know CDK allow us to use other prgramming language to write our code and then we can deploy it on cloud.
In this project First I installed Linux in windows and then combine it with VS Code by downloading extension .

The initialization process of this project start with version checking and upgrade of python version.
first check version.
```
 python --version       

```
Then do these steps to upgrade. 

```
 python vim ~/.bashrc               
 alias python='/usr/bin/python3'    
 soucre ~/.bashrc                 

```
Now check aws version and also update your cli.

```
 aws --version                    
 curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"  -o "awscliv2.zip
 sudo ./aws/install             

```
Next step is to create venv (Virtual Environment)

```
python3 -m venv .venv

```

Then use cdk init command and after that activate virtual environment.

```

 cdk init app --language python
 source .venv/bin/activate

```
virtual environment is activated,Now you can install the required dependencies.

```
 pip install -r requirements.txt

```

After this this you can write your code in stack.py file and then synth your cdk.
For synth use command

```
cdk synth

```
For pushing your code to git you can use these commands.

```
git add .
git commit -m "yourcommit"
git push

```
For deploy your code into cloud formation template use command.

```
cdk deploy                    

```
Happy Coding!!!

Enjoy !!!
