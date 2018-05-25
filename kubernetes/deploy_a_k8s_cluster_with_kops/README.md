# Deploy a Kubernetes cluster with KOPS

[KOPS](https://github.com/kubernetes/kops) allow to create  a cluster or instancegroup using a YAML configuration specification files ([ClusterSpec](https://godoc.org/k8s.io/kops/pkg/apis/kops#ClusterSpec)).

Here, we will demonstrate how to leverage this feature to deploy a customized Kubernetes cluster.

# Architecture

![architecture.png](https://raw.githubusercontent.com/julienlevasseur/playground/assets/master/images/architecture.png)

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

![k8s_dashboard.png](https://raw.githubusercontent.com/julienlevasseur/playground/assets/master/images/k8s_dashboard.png)

# The Terraform approach