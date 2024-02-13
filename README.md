
# WebRTC Client Server Demo

This is a simple WebRTC based application where a server sending frames of a bouncing ball to the client. The client then detects the balls in the frame and sends the location of the ball to the server using datachannel. The server then calculates the error between ball position and logs it out.

## Steps to run

- Install dependencies for this project. I like to use poetry for dependency but here I have just providded requirements.txt

    ` pip install -r requirements.txt `

- Run server. By default the server runs on `127.0.0.1` port `8080`

    `python server.py`

- Open another terminal/shell and run

    `python client.py`

- You should be able to see ball bouncing across the screen. The real-time position of the balll will be communicated between server and client and the error calculated by the server will be logged to the terminal.

## Deployment

- Start minikube 

    `minikube start`

- Build Docker images

    `docker build -t myserver Dockerfile.server .`

    `docker build -t myclient Dockerfile.client .`

- Apply the manifest files using

    `kubectl apply -f client_k8s.yaml`

    `kubectl apply -f server_k8s.yaml`

- Get deployments using 

    `kubectl get deployments`



## Reflections

- The code is structed in a way that it is not easy to be unit testable. Could improve the code structure. Improve tests.
- Making a shell scripts to take care of deployment. Ran out of time.






