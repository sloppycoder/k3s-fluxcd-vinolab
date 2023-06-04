# restrict servicelb only to 2 nodes in the cluster

kubectl label nodes pie4 svccontroller.k3s.cattle.io/enablelb=true
