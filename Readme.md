[![PyPI version](https://badge.fury.io/py/fandogh_cli.svg)](https://badge.fury.io/py/fandogh_cli)

Fandogh-CLI
======

fandogh-cli is the official CLI of [Fandogh PaaS](http://fandogh.cloud). 
One with the current version of the CLI can create new images on Fandogh and publish the versions and deploy them as service.

### How to install the CLI

<b>Please note that</b>Fandogh-cli is a python based application which needs the python 3.5 or higher. 
Run the following command to install the CLI:

`pip install fandogh-cli`  

Once it's installed run the following command to see the installation has been done successfully.

`fandogh --version`

If the output of the above command is the version of the Fandogh CLI... then congratulations you can now enjoy the taste of the Fandogh.
<b>Otherwise</b> please create an issue here with the output of the command to help us fixing the issues ASAP.

### How to login

After you install the CLI, run the following command to log in with your Fandogh account credentials:

`fandogh login` 

TODO: explain what happens internally

### How to create a new Image

In order to create a new image in Fandogh you need to change your current directory to the directory of your application, 
then you can run the following command:

```bash
$ cd ~/your-app-directory
$ fandogh image init
$ image name: test-application
Image created successfully
```

Now it's time to publish the first version of your image. An image in fandogh consists of a Dockerfile and the files which are necessary (a.k.a context) to build the docker image. For the time being you Dockerfile should be in the root of your application directory.
Run the following command to publish your image version:

```bash
$ fandogh image publish 
$ image version: v1
Image Version created successfully
```

### How to deploy a service

Deploying a service on Fandogh is easy as pie. Let's say you have an image with name `hello-world` 
which has a version named `v1` in state `BUILT` (to see the state of builds todo read here).

Run the following command to deploy your service:
```bash
$ fandogh service deploy  --image hello-world --version v1 --name hello-world
Your service deployed successfully.
The service is accessible via following link:
http://hello-world.fandogh.cloud
```

The above command will deploy a <b>service</b> with name <b>hello-world</b> from docker image hello-world:v1.
 
<b>Note:</b> at the time being services can be only exposed to the outside via port 80. 
so ensure your web server is listening on this port.

### How to shutdown a service

Releasing the resources is your friend to manage your cost. In cloud you can easily free the resource and not to pay for it anymore.
To do so via fandogh-cli it's even simpler than deploying a service. Let's say we want to destroy the service we deployed in the previous section.
 
```bash
$ fandogh service destroy  --name hello
Service destroyed successfully.
```
