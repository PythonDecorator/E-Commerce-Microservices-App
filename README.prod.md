# DEPLOY USING DOCKER-COMPOSE, KUBERNETES AND GOOGLE CLOUD

---
<br />

## SETUP DATABASE
1. Go to google cloud and add SQL select the preferred engine ie MYSQL or ProgresSQL and configure it.
2. Add the host or IP as DB_HOST in your docker-compose.prod.yaml file or 🔐secrets.
3. Create a users-db in the Database and add your IP address to the networks to be able to connect to it from 
your local machine.
---

<br />

## DOCKER
### 👉 Build the Image
- Create a docker-compose.prod.yaml file and build it.
- Make sure to add the image name and tag.

```shell
$ docker-compose -f docker-compose.prod.yaml build
```
This will build the image.
👏👏👏This is the image that will be pushed to Google Cloud.
---

<br />

## KOMPOSE
- The first step is to make sure you can run kompose commands on your `CLI`.
You can download and add the kompose `kompose.exe` file to your machine environment `PATH`
- The file yaml files created is what you will upload to gcloud. The two files can be combined in one yaml file
---

### 👉 Convert docker compose file to a kubernetes compatible
After building the image you need to convert the docker-compose.prod.yaml file to kubernetes version.
> Generate yaml file via `kompose`
```shell
$ kompose convert -f docker-compose.prod.yaml
```
Remove any unwanted part and upload it to gcloud.

---

<br />

## KUBERNETES 

### ✔️ create pod
```shell
$ kubectl apply -f users.yaml
````


### ✔️ Check the running pods
```shell
$ kubectl get pods
```

### ✔️ See details and messages of the pod
```shell
$ kubectl describe pod <name>  
```
> The name can be something like this  `users-backend-6ff69fd6f-wsnbc` 

### Delete pod
```shell
$ kubectl delete pod users-backend-6ff69fd6f-wsnb
```
😃 Oops, this won't work, because kubernetes will create it back automatically. Try it.

### ✅ 🔐Create secrets and hide your environment variables
```shell
$ kubectl create secret generic kafka-secrets --from-literal=BOOTSTRAP_SERVERS=VALUE  
--from-literal=EMAIL_PASSWORD=VALUE
--from-literal=KEY=VALUE
```
---

<br />

## GOOGLE CLOUD
> 🌦️Google cloud 
1. Create a new project Ecommerce-Microservices-Apps.
2. Add Apache confluent-kafka.
3. Click on `Manage` and set it up on their website.
4. Add kubernetes and enable it.
5. Click `CREATE` and add a new cluster called `Project Name`.
---

### 👉 Open Google Cloud CLI
- Click activate cloud shell and on the shell run the following commands:

> Switch to the gcloud project <Project Name>
```shell
$ gcloud config set project <projectId>
```

### 👉 Activate the kubernetes cluster
```shell
$ gcloud container clusters get-credentials projectId --zone=us-west2
```

###  Upload the yaml file generated with kompose into it.
> or use: nano users.yaml
...

### 💻On Your Local Machine✅
-  Login to google cloud.
>  gcloud auth login
-  Make sure you are logged-in to google-cloud-cli, and you are able to run gcloud commands
- You can download the gcloud SDK for your operating system and add it to you system environment PATH

### Tag Image to Google Cloud
> docker tag any-name/users:0.0.1 gcr.io/projectname-56572/users
- if you get unauthorized: You don't have the needed permissions to perform this operation error.

`RUN`
> gcloud auth configure-docker

### Push Image to Google cloud
> docker push gcr.io/projectname-56572/users

- Once you have pushed the image.
- Click on the image in Google Cloud container registry and copy the image name.
- Go to the yaml file on Google cloud and replace the image name with the one you copied.

### Add your secretes
On google CLI run
```shell
$ kubectl create secret generic kafka-secrets --from-literal=BOOTSTRAP_SERVERS=VALUE  
--from-literal=EMAIL_PASSWORD=VALUE
--from-literal=KEY=VALUE
```

### Apply the changes
On google CLI run
> kubectl apply -f users.yaml
---

## Finally, Create an ingress.yaml file in google cloud.
- The ingress.yaml file is responsible for redirecting request to the users-backend or other services in the cluster
as defined in the path.
- If we go to the path api/users then it redirects to the users-backend
- For the ingress to work, you need to add FORCE_SCRIPT to your app.settings.py file.
This will make the app live in the directory you provided instead of the root url or domain name.

### Apply the changes
On google CLI run
> kubectl apply -f ingress.yaml
---
<br />

The app should be up and running.

---
Python Decorator