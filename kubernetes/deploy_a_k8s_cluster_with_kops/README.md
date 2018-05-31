# Deploy a Kubernetes cluster with KOPS

[KOPS](https://github.com/kubernetes/kops) allow to create  a cluster or instancegroup using a YAML configuration specification files ([ClusterSpec](https://godoc.org/k8s.io/kops/pkg/apis/kops#ClusterSpec)).

Here, we will demonstrate how to leverage this feature to deploy a customized Kubernetes cluster.

# Architecture

![architecture.png](https://raw.githubusercontent.com/julienlevasseur/playground/master/kubernetes/deploy_a_k8s_cluster_with_kops/assets/images/architecture.png)

# The cluster deployement

First create a S3 bucket to store the Kubernetes cluster state files :

```hcl
provider "aws" {}

resource "aws_s3_bucket" "k8s_state_storage" {
  bucket = "example-kubernetes-states`"
  acl    = "private"

  versioning {
    enabled = true
  }

  tags {
    Name        = "example-kubernetes-states`"
    Environment = "Dev"
  }
}
```

You have to add the following variable to your environment:

`KOPS_STATE_STORE=s3://example-kubernetes-states`

Then, you're ready to prepare the cluster creation:

```bash
kops create -f cluster.spec 

Created cluster/k8s-hardened.example.com
Created instancegroup/master-us-east-1b
Created instancegroup/nodes

To deploy these resources, run: kops update cluster k8s-hardened.example.com --yes
```

Before applying the configuration, you have to create a secret to store your SSH public key:

```bash
kops create secret --name k8s-hardened.example.com sshpublickey admin -i ~/.ssh/id_rsa.pub
```

Let's create the cluster !

```bash
kops update cluster k8s-hardened.example.com --yes
I0525 16:20:28.124300   12961 executor.go:91] Tasks: 0 done / 77 total; 31 can run
I0525 16:20:29.120612   12961 vfs_castore.go:731] Issuing new certificate: "ca"
I0525 16:20:29.388046   12961 vfs_castore.go:731] Issuing new certificate: "apiserver-aggregator-ca"
I0525 16:20:30.799781   12961 executor.go:91] Tasks: 31 done / 77 total; 26 can run
I0525 16:20:32.050767   12961 vfs_castore.go:731] Issuing new certificate: "apiserver-proxy-client"
I0525 16:20:32.305776   12961 vfs_castore.go:731] Issuing new certificate: "kube-controller-manager"
I0525 16:20:32.497167   12961 vfs_castore.go:731] Issuing new certificate: "kube-proxy"
I0525 16:20:32.605388   12961 vfs_castore.go:731] Issuing new certificate: "kops"
I0525 16:20:32.610554   12961 vfs_castore.go:731] Issuing new certificate: "kube-scheduler"
I0525 16:20:32.749412   12961 vfs_castore.go:731] Issuing new certificate: "apiserver-aggregator"
I0525 16:20:32.766780   12961 vfs_castore.go:731] Issuing new certificate: "kubelet"
I0525 16:20:32.824766   12961 vfs_castore.go:731] Issuing new certificate: "kubelet-api"
I0525 16:20:32.864096   12961 vfs_castore.go:731] Issuing new certificate: "master"
I0525 16:20:33.275793   12961 vfs_castore.go:731] Issuing new certificate: "kubecfg"
I0525 16:20:34.052159   12961 executor.go:91] Tasks: 57 done / 77 total; 18 can run
I0525 16:20:34.590016   12961 launchconfiguration.go:341] waiting for IAM instance profile "nodes.k8s-hardened.example.com" to be ready
I0525 16:20:34.936018   12961 launchconfiguration.go:341] waiting for IAM instance profile "masters.k8s-hardened.example.com" to be ready
I0525 16:20:45.326815   12961 executor.go:91] Tasks: 75 done / 77 total; 2 can run
I0525 16:20:46.143212   12961 executor.go:91] Tasks: 77 done / 77 total; 0 can run
I0525 16:20:46.143247   12961 dns.go:153] Pre-creating DNS records
I0525 16:20:47.107511   12961 update_cluster.go:291] Exporting kubecfg for cluster
kops has set your kubectl context to k8s-hardened.example.com

Cluster is starting.  It should be ready in a few minutes.

Suggestions:
 * validate cluster: kops validate cluster
 * list nodes: kubectl get nodes --show-labels
 * ssh to the master: ssh -i ~/.ssh/id_rsa admin@api.k8s-hardened.example.com
 * the admin user is specific to Debian. If not using Debian please use the appropriate user based on your OS.
 * read about installing addons at: https://github.com/kubernetes/kops/blob/master/docs/addons.md.
```

Validate your cluster:

```bash
kops validate cluster
Using cluster from kubectl context: k8s-hardened.example.com

Validating cluster k8s-hardened.example.com

INSTANCE GROUPS
NAME			ROLE	MACHINETYPE	MIN	MAX	SUBNETS
master-us-east-1b	Master	m3.medium	1	1	us-east-1b
nodes			Node	t2.medium	2	2	us-east-1b,us-east-1c,us-east-1d

NODE STATUS
NAME				ROLE	READY
ip-172-20-117-187.ec2.internal	node	True
ip-172-20-33-56.ec2.internal	master	True
ip-172-20-60-96.ec2.internal	node	True

Your cluster k8s-hardened.example.com is ready
```

Good, everything is fine.

Now, let's install the [Dashboard Service](https://github.com/kubernetes/dashboard) to our new cluster.

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
```

To connect to the dashboard, you will need the credentials (api token and api administrative creds):

API bearer token:
```bash
kops get secrets --type secret admin -oplaintext
```

Admin access:
```bash
kops get secrets kube -oplaintext
```

![k8s_dashboard.png](https://raw.githubusercontent.com/julienlevasseur/playground/master/kubernetes/deploy_a_k8s_cluster_with_kops/assets/images/k8s_dashboard.png)

# The Terraform approach

![architecture_with_terraform.png](https://raw.githubusercontent.com/julienlevasseur/playground/master/kubernetes/deploy_a_k8s_cluster_with_kops/assets/images/architecture_with_terraform.png)

This is a variation of K8s cluster creation, still with Kops but, we generate [Terraform](https://www.terraform.io/) code to manage the cluster creation rather than creating it directly with Kops command.

```bash
kops create cluster --name=k8s-hardened.example.com --state=s3://k8s-hardened-tfstate --dns-zone=example.com --zones us-east-1b --zones us-east-1c --zones us-east-1d --image=ami-9462dbeb --out=. --target=terraform
I0523 13:53:12.577820   16311 create_cluster.go:1318] Using SSH public key: ~/.ssh/id_rsa.pub
I0523 13:53:13.332480   16311 create_cluster.go:472] Inferred --cloud=aws from zone "us-east-1b"
I0523 13:53:13.636571   16311 subnets.go:184] Assigned CIDR 172.20.32.0/19 to subnet us-east-1b
I0523 13:53:13.636595   16311 subnets.go:184] Assigned CIDR 172.20.64.0/19 to subnet us-east-1c
I0523 13:53:13.636608   16311 subnets.go:184] Assigned CIDR 172.20.96.0/19 to subnet us-east-1d
I0523 13:53:16.908772   16311 executor.go:91] Tasks: 0 done / 77 total; 31 can run
I0523 13:53:16.909985   16311 dnszone.go:242] Check for existing route53 zone to re-use with name "example.com"
I0523 13:53:17.015071   16311 dnszone.go:249] Existing zone "example.com." found; will configure TF to reuse
I0523 13:53:17.851508   16311 vfs_castore.go:731] Issuing new certificate: "ca"
I0523 13:53:18.908899   16311 vfs_castore.go:731] Issuing new certificate: "apiserver-aggregator-ca"
I0523 13:53:19.976941   16311 executor.go:91] Tasks: 31 done / 77 total; 26 can run
I0523 13:53:21.051639   16311 vfs_castore.go:731] Issuing new certificate: "kubelet"
I0523 13:53:21.362105   16311 vfs_castore.go:731] Issuing new certificate: "kube-proxy"
I0523 13:53:21.461494   16311 vfs_castore.go:731] Issuing new certificate: "kops"
I0523 13:53:21.821614   16311 vfs_castore.go:731] Issuing new certificate: "kubecfg"
I0523 13:53:21.952314   16311 vfs_castore.go:731] Issuing new certificate: "kubelet-api"
I0523 13:53:22.348586   16311 vfs_castore.go:731] Issuing new certificate: "apiserver-proxy-client"
I0523 13:53:22.361188   16311 vfs_castore.go:731] Issuing new certificate: "apiserver-aggregator"
I0523 13:53:22.371679   16311 vfs_castore.go:731] Issuing new certificate: "kube-scheduler"
I0523 13:53:22.516060   16311 vfs_castore.go:731] Issuing new certificate: "kube-controller-manager"
I0523 13:53:22.525978   16311 vfs_castore.go:731] Issuing new certificate: "master"
I0523 13:53:23.239116   16311 executor.go:91] Tasks: 57 done / 77 total; 18 can run
I0523 13:53:23.567858   16311 executor.go:91] Tasks: 75 done / 77 total; 2 can run
I0523 13:53:23.568794   16311 executor.go:91] Tasks: 77 done / 77 total; 0 can run
I0523 13:53:23.575171   16311 target.go:292] Terraform output is in .
I0523 13:53:23.896716   16311 update_cluster.go:291] Exporting kubecfg for cluster
kops has set your kubectl context to k8s-hardened.example.com
 
Terraform output has been placed into .
Run these commands to apply the configuration:
   cd .
   terraform plan
   terraform apply
 
Suggestions:
 * validate cluster: kops validate cluster
 * list nodes: kubectl get nodes --show-labels
 * ssh to the master: ssh -i ~/.ssh/id_rsa admin@api.k8s-hardened.example.com
 * the admin user is specific to Debian. If not using Debian please use the appropriate user based on your OS.
 * read about installing addons at: https://github.com/kubernetes/kops/blob/master/docs/addons.md.
```

A `kubernetes.tf` file has been created :
```bash
ls -l
total 44
-rw-rw-r-- 1 user user   525 May 23 13:50 cluster.spec
drwxr-xr-x 2 user user  4096 May 23 13:53 data
-rw-r--r-- 1 user user 19250 May 23 13:53 kubernetes.tf
```

So, we can curstomize you the Kubernetes cluster deployment via the HCL code, and apply it !

```bash
terraform plan
(...)
Plan: 39 to add, 0 to change, 0 to destroy.
```

```bash
terraform apply
 
An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create
 
Terraform will perform the following actions:
 
(...)
 
Plan: 39 to add, 0 to change, 0 to destroy.
 
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.
 
  Enter a value: yes
 
Apply complete! Resources: 39 added, 0 changed, 0 destroyed.
 
Outputs:
 
cluster_name = k8s-hardened.example.com
master_security_group_ids = [
    sg-xxxxxxxx
]
masters_role_arn = arn:aws:iam::xxxxxxxxxxxx:role/masters.k8s-hardened.example.com
masters_role_name = masters.k8s-hardened.example.com
node_security_group_ids = [
    sg-2e771b66
]
node_subnet_ids = [
    subnet-xxxxxxxx,
    subnet-xxxxxxxx,
    subnet-xxxxxxxx
]
nodes_role_arn = arn:aws:iam::xxxxxxxxxxxx:role/nodes.k8s-hardened.example.com
nodes_role_name = nodes.k8s-hardened.example.com
region = us-east-1
vpc_id = vpc-xxxxxxxx
```
