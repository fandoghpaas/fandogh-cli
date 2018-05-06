Fandogh-CLI
======

fandogh-cli is the official CLI of [Fandogh PaaS](http://fandogh.com). 
One with the current version of the CLI can create new apps on fandogh and publish the versions and deploy them as service.

### How to install the CLI

fandogh-cli is a python based application which needs the python 3.5 or higher. 
Run the following command to install the CLI:

`pip install fandogh-cli`  

Once it's installed run the following command to see the install has been done successfully.

`fandogh --version`

If the output of the above command is the version of the fandogh... then congratulation you can now enjoy the taste of fandogh.
<b>Otherwise</b> please create an issue here with the output of the command to help us fixing the issues ASAP.

### How to login

After you install the CLI, run the following command to log in with your Fandogh account credentials:

`fandogh login` 

TODO: explain what happens internally

### How to create a new Application

In order to create a new app in Fandogh you need to change your current directory to the directory of your application, 
then you can run the following command:

```bash
 $ cd ~/your-app-directory
 $ fandogh app init
 $ application name: test-application
 "App created successfully"
```

Now it's time to publish the first version of your application. An application in fandogh consists of a Dockerfile and the the files which are necessary to build the docker image. For the time being you Dockerfile should be in the root your application directory.
Run the following command to publish your application version:

```bash
$ fandogh app publish 
$ application version: v1
"Version created successfully"
```

TODO:
- clean up workspace
- service log
- app list
- service destroy 