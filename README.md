# Code for "Conducting Qualitative Interviews with AI"  

This codebase allows you to conduct qualitative interviews with human subjects by delegating the task of interviewing to an AI-interviewer. We support three options of running the application: 
1. Running the application locally on your own machine for testing and development. 
2. Deploying the application as a Flask app on your own server. 
3. Deploying the application as a serverless Lambda function on Amazon AWS. 

Option 2 and 3 are for eventual large-scale data collection. We explain the setup steps below.  

The application requires access to a large language model (LLM). The code currently operates with OpenAI's API. You can obtain API keys [here](https://platform.openai.com/) and supply the key to the application in the `app/parameters.py` file by editing the `OPENAI_API_KEY` variable. 

The file `app/parameters.py` provides a detailed description of how the parameters and prompts of the application work. 

Our recommended setup is to host the AI interviewer application as an AWS Lambda function (Option 3 below) and to embed the AI interview into a Qualtrics survey, for which we provide files in `/Qualtrics`. 


## Paper and citation 

The paper is available here: [https://dx.doi.org/10.2139/ssrn.4583756](https://dx.doi.org/10.2139/ssrn.4583756). 

This code is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Commercial use, including applications in business or for-profit ventures, is strictly prohibited without prior written permission. Uses and distribution should cite: 

```
Chopra, Felix and Haaland, Ingar, Conducting Qualitative Interviews with AI (2023). CESifo Working Paper No. 10666, Available at SSRN: https://ssrn.com/abstract=4583756 or http://dx.doi.org/10.2139/ssrn.4583756 
``` 
or use the suggested Bibtex entry: 
```
@article{ChopraHaaland2023, 
  title={Conducting Qualitative Interviews with AI}, 
  author={Chopra, Felix and Haaland, Ingar}, 
  journal={CESifo Working Paper No. 10666}, 
  url={https://ssrn.com/abstract=4583756}, 
  year={2023} 
} 
``` 

For inquiries about commercial licenses, please contact [Felix Chopra](f.chopra@fs.de).  


## Table of Contents 
* [Option 1: Running the app locally for testing and development](#option-1-local-testing) 
    * [Docker](#docker) 
    * [Manually](#manual) 
* [Option 2: Deploy as Flask app](#option-2-deploy-as-flask-app) 
* [Option 3: Deploy as AWS Lambda function (preferred)](#option-3-deploy-on-aws) 
* [Qualtrics integration](#integrating-with-qualtrics) 
* [How to interact with the app](#how-to-interact-with-the-app) 
* [Retrieving stored interviews](#retrieving) 


## Option 1: Running the app locally for testing and development 

This option is ideal for testing the app before data collection and making changes to the code or prompts to better fit your research setting. We explain how this is done using Docker as well as manually. 

### Docker 

The cleanest way to then run the application -- locally or remotely -- is through a [Docker](https://docs.docker.com/engine/install/) container. You can easily build a Docker image containing only the necessary packages in a contained environment from whatever operating system. You will also need to have Git [installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 


**Step 1**: Clone the project from GitHub and navigate into the repo: 

```bash 
git clone https://github.com/fchop/interviews.git 
cd interviews 
``` 

**Step 2**: Build a Docker image (e.g. named `interviews`) and run it in a container: 

To build and then run a container in the background you can add the `--detach` flag. We are publishing the `8000` port to forward requests and mounting (i.e. sharing) the filesystem within the `/app` subdirectory such to see outputs directly. This can be done by running: 

```bash 
docker build --tag interviews . 
docker run --detach --publish 8000:80 --volume $(pwd)/app:/app --env DATA_DIR=/app/data --name app interviews 
``` 

Or, alternatively, build and run using the template `docker-compose` YAML by simply running: 

```bash 
docker compose up --build --detach 
``` 

**Comments**:  
- You can now make requests to your local host listening on port `8000` (e.g. `localhost:8000`, `0.0.0.0:8000`, or `127.0.0.1:8000`). Running in the command line `curl http://127.0.0.1:8000/` should return text `Running!` to confirm the application is successfully up and running. 
- You can stop (e.g. `docker stop`) and remove (i.e. `docker rm`) containers, or do the same using the compose file (e.g. `docker compose down`). If you make local changes to your code, you can restart the container to reflect these changes using `docker restart` or `docker compose restart`. 


### Manual setup 

If you decide against Docker, you will need install Python. We recommend the stable version 3.12. You can install Python from [here](https://www.python.org/downloads). You will also need to have Git [installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 

**Step 0:** Create a virtual environment, e.g. named `interviews-env`, and activate it, so as to install necessary packages in a clean environment, guaranteeing no clashing dependencies. In your command-line terminal run: 

```bash 
python -m venv interviews-env 
cd interviews-env 
source bin/activate 
``` 

**Step 1:** Clone this project from Github and install the necessary packages defined in the repository's `local_requirements.txt` file using `pip`: 

```bash 
git clone https://github.com/fchop/interviews.git 
cd interviews 

pip install -r local_requirements.txt 
``` 

**Step 2:** Now start a *development* server to host your application by running: 

```bash 
python app/app.py 
``` 

**Comments**:  
- As you can see in `app/app.py`, we are listening on port `8000` so you can now make requests to your local host (e.g. `localhost`, `0.0.0.0`, or `127.0.0.1`). Running in the command line `curl http://127.0.0.1:8000/` should return text `Running!` to confirm the application is successfully up and running. 
- Changes to your local code will automatically restart the server, reflecting your changes. You can stop the server by entering `control-C` on your command line. 


## Option 2: Deploy as Flask app  

This option is for when you are ready to collect data and want to deploy your application on a production server. The benefit of this option is that you can manage the server and all aspects of your code, logs, and application service directly. However, it is less convenient thatn AWS Lambda because you have to manage the server yourself. We recommend that you use Docker when deploying as a Flask app, so again on your remote server make sure Docker is [installed](https://docs.docker.com/engine/install/). 

**Step 1:** Copy your current codebase, including changes you have made, to your remote server. In Linux, you can securely transfer files between servers using Secure Shell (SSH) protocol with `scp`, e.g. 
```bash 
scp -r <LOCAL_DIRECTORY> <REMOTE_DIRECTORY> 
``` 

**Step 2:** Once you have your codebase on your remote server, you can use Docker and follow the steps from Option 1 above, e.g. run 
```bash 
docker compose up --build --detach 
``` 

Your remote machine will now forward requests to port `8000` onto port `80` on which the Docker container is listening, thereby processing requests to `<REMOTE_HOST>:8000/`.  


##
