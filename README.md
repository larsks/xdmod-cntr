# xdmod-cntr
A project to deploy XDMoD on kubernetes/OpenShift.


## deploying xdmod on minikube
1) Start minikube (not needed for kubernetes):
 
    minikube start --driver=hyperkit --extra-config=apiserver.service-node-port-range=1-65535
    kubectl config use-context minikube

2) Create the persistent volumes (may be different for Kubernetes and OpenShift - as this is likely a privileged operation):

    kubectl apply -f ./pv-mariadb.yaml
    kubectl apply -f ./pv-xdmod-conf.yaml
    kubectl apply -f ./pv-xdmod-src.yaml
    kubectl apply -f ./pv-xdmod-data.yaml
## deploying on kubernetes/openshift

3) build the docker files

    for minikube:
        minikube image build --logtostderr -f Dockerfile.moc-xdmod -t moc-xdmod .

    for openshift
        docker build -f Dockerfile.moc-xdmod -t moc-xdmod .

4) create the necessary configmaps/secrets
     
    kubectl create cm --from-file xdmod_conf/xdmod_init.json cm-xdmod-init-json 
    oc create cm --from-file xdmod_conf/xdmod_init.json cm-xdmod-init-json 

5) Create the namespace (project) - use kubectl for minikube, or oc for openshift 

   - not needed for the NERC

    kubectl apply -f ./k8s/kube-base/xdmod-namespace.yaml

6) Load the project into the namespace

    kubectl -n xdmod apply -k ./k8s/kube-base
    oc -n xdmod apply -k ./k8s/kube-base

