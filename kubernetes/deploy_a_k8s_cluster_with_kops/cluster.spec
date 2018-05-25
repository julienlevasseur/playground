apiVersion: kops/v1alpha2
kind: Cluster
metadata:
  creationTimestamp: 2018-05-23T17:53:14Z
  name: k8s-hardened.example.com
  labels:
    kops.k8s.io/cluster: k8s-hardened.example.com
spec:
  api:
    dns: {}
  authorization:
    rbac: {}
  channel: stable
  cloudProvider: aws
  clusterDNSDomain: cluster.local
  configBase: s3://example-kubernetes-states/k8s-hardened.example.com
  configStore: s3://example-kubernetes-states/k8s-hardened.example.com
  dnsZone: example.com
  adminAccess:
  - 0.0.0.0/0
  docker:
    bridge: ""
    ipMasq: false
    ipTables: false
    logDriver: json-file
    logLevel: warn
    logOpt:
    - max-size=10m
    - max-file=5
    storage: overlay,aufs
    version: 17.03.2
  etcdClusters:
  - etcdMembers:
    - instanceGroup: master-us-east-1b
      name: b
    image: gcr.io/google_containers/etcd:2.2.1
    name: main
    version: 2.2.1
  - etcdMembers:
    - instanceGroup: master-us-east-1b
      name: b
    image: gcr.io/google_containers/etcd:2.2.1
    name: events
    version: 2.2.1
  iam:
    allowContainerRegistry: true
    legacy: false
  keyStore: s3://example-kubernetes-states/k8s-hardened.example.com/pki
  kubeAPIServer:
    address: 127.0.0.1
    admissionControl:
    - Initializers
    - NamespaceLifecycle
    - LimitRanger
    - ServiceAccount
    - PersistentVolumeLabel
    - DefaultStorageClass
    - DefaultTolerationSeconds
    - MutatingAdmissionWebhook
    - ValidatingAdmissionWebhook
    - NodeRestriction
    - ResourceQuota
    allowPrivileged: true
    anonymousAuth: false
    apiServerCount: 1
    authorizationMode: RBAC
    etcdQuorumRead: false
    etcdServers:
    - http://127.0.0.1:4001
    etcdServersOverrides:
    - /events#http://127.0.0.1:4002
    image: gcr.io/google_containers/kube-apiserver:v1.9.3
    insecurePort: 8080
    kubeletPreferredAddressTypes:
    - InternalIP
    - Hostname
    - ExternalIP
    logLevel: 2
    requestheaderAllowedNames:
    - aggregator
    requestheaderExtraHeaderPrefixes:
    - X-Remote-Extra-
    requestheaderGroupHeaders:
    - X-Remote-Group
    requestheaderUsernameHeaders:
    - X-Remote-User
    securePort: 443
    serviceClusterIPRange: 100.64.0.0/13
    storageBackend: etcd2
  kubeControllerManager:
    allocateNodeCIDRs: true
    attachDetachReconcileSyncPeriod: 1m0s
    clusterCIDR: 100.96.0.0/11
    clusterName: k8s-hardened.example.com
    configureCloudRoutes: true
    image: gcr.io/google_containers/kube-controller-manager:v1.9.3
    leaderElection:
      leaderElect: true
    logLevel: 2
    useServiceAccountCredentials: true
  kubeDNS:
    cacheMaxConcurrent: 150
    cacheMaxSize: 1000
    domain: cluster.local
    replicas: 2
    serverIP: 100.64.0.10
  kubeProxy:
    clusterCIDR: 100.96.0.0/11
    cpuRequest: 100m
    hostnameOverride: '@aws'
    image: gcr.io/google_containers/kube-proxy:v1.9.3
    logLevel: 2
  kubeScheduler:
    image: gcr.io/google_containers/kube-scheduler:v1.9.3
    leaderElection:
      leaderElect: true
    logLevel: 2
  kubelet:
    allowPrivileged: true
    cgroupRoot: /
    clusterDNS: 100.64.0.10
    clusterDomain: cluster.local
    enableDebuggingHandlers: true
    evictionHard: memory.available<100Mi,nodefs.available<10%,nodefs.inodesFree<5%,imagefs.available<10%,imagefs.inodesFree<5%
    featureGates:
      ExperimentalCriticalPodAnnotation: "true"
    hostnameOverride: '@aws'
    kubeconfigPath: /var/lib/kubelet/kubeconfig
    logLevel: 2
    networkPluginMTU: 9001
    networkPluginName: kubenet
    nonMasqueradeCIDR: 100.64.0.0/10
    podInfraContainerImage: gcr.io/google_containers/pause-amd64:3.0
    podManifestPath: /etc/kubernetes/manifests
  kubernetesApiAccess:
  - 0.0.0.0/0
  kubernetesVersion: 1.9.3
  masterInternalName: api.internal.k8s-hardened.example.com
  masterKubelet:
    allowPrivileged: true
    cgroupRoot: /
    clusterDNS: 100.64.0.10
    clusterDomain: cluster.local
    enableDebuggingHandlers: true
    evictionHard: memory.available<100Mi,nodefs.available<10%,nodefs.inodesFree<5%,imagefs.available<10%,imagefs.inodesFree<5%
    featureGates:
      ExperimentalCriticalPodAnnotation: "true"
    hostnameOverride: '@aws'
    kubeconfigPath: /var/lib/kubelet/kubeconfig
    logLevel: 2
    networkPluginMTU: 9001
    networkPluginName: kubenet
    nonMasqueradeCIDR: 100.64.0.0/10
    podInfraContainerImage: gcr.io/google_containers/pause-amd64:3.0
    podManifestPath: /etc/kubernetes/manifests
    registerSchedulable: false
  masterPublicName: api.k8s-hardened.example.com
  networkCIDR: 172.20.0.0/16
  networking:
    kubenet: {}
  nonMasqueradeCIDR: 100.64.0.0/10
  secretStore: s3://example-kubernetes-states/k8s-hardened.example.com/secrets
  serviceClusterIPRange: 100.64.0.0/13
  sshAccess:
  - 0.0.0.0/0
  subnets:
  - cidr: 172.20.32.0/19
    name: us-east-1b
    type: Public
    zone: us-east-1b
  - cidr: 172.20.64.0/19
    name: us-east-1c
    type: Public
    zone: us-east-1c
  - cidr: 172.20.96.0/19
    name: us-east-1d
    type: Public
    zone: us-east-1d
  topology:
    dns:
      type: Public
    masters: public
    nodes: public
# Master InstanceGroup
---
apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: 2018-05-23T17:53:14Z
  labels:
    kops.k8s.io/cluster: k8s-hardened.example.com
  name: master-us-east-1b
spec:
  image: ami-9462dbeb 								# CIS Level 1 CentOS 7
  machineType: m3.medium
  maxSize: 1
  minSize: 1
  nodeLabels:
    kops.k8s.io/instancegroup: master-us-east-1b
  role: Master
  subnets:
  - us-east-1b
# Nodes InstanceGroup
---
apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: 2018-05-23T17:53:14Z
  labels:
    kops.k8s.io/cluster: k8s-hardened.example.com
  name: nodes
spec:
  image: ami-9462dbeb 								# CIS Level 1 CentOS 7
  machineType: t2.medium
  maxSize: 2
  minSize: 2
  nodeLabels:
    kops.k8s.io/instancegroup: nodes
  role: Node
  subnets:
  - us-east-1b
  - us-east-1c
  - us-east-1d