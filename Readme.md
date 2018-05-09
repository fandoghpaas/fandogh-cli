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

Now it's time to publish the first version of your application. An application in fandogh consists of a Dockerfile and the the files which are necessary (a.k.a context) to build the docker image. For the time being you Dockerfile should be in the root your application directory.
Run the following command to publish your application version:

```bash
$ fandogh app publish 
$ application version: v1
"Version created successfully"
```

### How to deploy a service

Deploying a service on Fandogh is easy as pie. Let's say you have an application with name `hello-world` 
which has version named `v1` with state `BUILT` (to see the state of builds todo read here).

You just need to run the following command:
```bash
$ fandogh service deploy  --app hello-world --version v1 --name hello-world`
Your service deployed successfully.
The service is accessible via following link:
http://hello-world.fandogh.cloud
```

The above command will deploy a <b>service</b> with name <b>hello-world</b> from docker image hello-world:v1.
 
<b>Note:</b> at the time being services can be only exposed to the outside via port 80. 
so ensure your web server is listening on this port.

### How to shutdown a service

Releasing the resources is your friend to manage your cost. In cloud you can easily free the resource and no to pay for it anymore.
To do so via fandogh-cli is even simpler than deploying a service. Let's say we want to destroy the service we deployed in the previous section.
 
```bash
$ fandogh service destroy  --name hello
Service destroyed successfully.
```

TODO:
- service log 