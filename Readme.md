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

When you run `fandogh login` it wil prompt for username and password which will be used to obtain a token. the token will be stored in $HOME/.fandogh/credentials and later will be used by all other fandogh commands.

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
which has a version named `v1` in state `BUILT`.

Run the following command to deploy your service:
```bash
$ fandogh service deploy  --image hello-world --version v1 --name hello-world
Your service deployed successfully.
The service is accessible via following link:
http://hello-world.fandogh.cloud
```
The above command will deploy a <b>service</b> with name <b>hello-world</b> from docker image hello-world:v1.
You can also use the following options when running deploy command:  

- --port or -p: to specify which port of of container should be exposed
- --internal: to indicate that this service is an internal service and the port should only be accessible within the private network
- --env or -e: to specify environment variables to set in the container.you can use this option as many as you need, for example `fandogh service deploy  --image hello-world --version v1 --name hello-world --env some_variable=some_value --env another_variable=another_value`



### How to shutdown a service

Releasing the resources is your friend to manage your cost. In cloud you can easily free the resource and not to pay for it anymore.
To do so via fandogh-cli it's even simpler than deploying a service. Let's say we want to destroy the service we deployed in the previous section.
 
```bash
$ fandogh service destroy  --name hello
Service destroyed successfully.
```

## Managed Services

Fandogh Platform provides a set of production ready managed services that you can deploy in seconds and use them via your services. 
The following list consist of the managed services we already support.

### MySQL Service

The MySQL Managed Service on Fandogh consist of Mysql RDBMS itself and Web UI (PHPMyAdmin) that let you to manage your DBMS.
In order to log into the Web UI you can use the master user credentials.
 
Username: master

password: master (can be changed through config options)

You can deploy a MySQL Server in your namespace by running the following command:

```bash
$ fandogh managed-service deploy mysql 9.4

Your Mysql service will be ready in a few seconds.
You can have access to the PHPMyAdmin via following link:
http://mysql.your_namespace.fandogh.cloud
```  

From your services you can access to the Mysql by using `mysql:3306` address. 

#### Configuration
There are couple of configuration that you can pass to Fandogh when you are deploying a Mysql service:

* `service_name default: mysql` 

    The value of this field will be the name of your DBMS. as the result this name will change the URL of your phpmyadmin panel. 
    e.g. If you set `service_name=test-dbms` then the admin URL will be something like `http://test-dbms.your_namespace.fandogh.cloud`
* `phpmyadmin_enabled default: true`  

    This is a boolean field that indicates if you want to have phpmyadmin running for this RDBMS or not.
    e.g. If you set `phpmyadmin_enabled=false` then the admin UI won't be deployed for the given DBMS.
* `mysql_root_password default: root`
 
    The value of this field will be the password of your mysql master password.
    
Example:
```bash
$ fandogh managed-service deploy mysql 9.4 -c service_name=test-dbms -c phpmyadmin_enabled=false -c mysql_root_password=test123
```
