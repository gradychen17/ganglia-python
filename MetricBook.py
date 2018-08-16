import requests_unixsocket
import commands

class MetricBook(object):
    def __init__(self):    
        self.metrics =  {
            'docker_ps': {
                            'call_back'   : 'getDockerPs',
                            'time_max'    : 10,
                            'value_type'  : 'uint',
                            'format'      : '%d',
                            'units'       : 'XXX',
                            'slope'       : 'both',  # zero|positive|negative|both
                            'description' : 'XXX',
                            'groups'      : 'testgroup',    
                            },
            # 'kubelet': {}   
            'node_ready': {
                            'call_back'   : 'getNodeStatus',
                            'time_max'    : 10,
                            'value_type'  : 'uint',
                            'format'      : '%d',
                            'units'       : 'XXX',
                            'slope'       : 'both',  # zero|positive|negative|both
                            'description' : 'XXX',
                            'groups'      : 'testgroup',                                
            }
        }

    def getNodeStatus(self):
        metric_value = 2    # '2' as defined by Chen Xin, indicated a success (node status is good)
        # check every node and report status for each one
        # for node in $(kubectl get nodes|grep -v NAME|awk '{print $1}'|grep -v master);do echo -n "$node  ";kubectl describe node $node|egrep -q "\s+Ready\s+False";echo $?;done
        # cmd = 'for node in $(kubectl get nodes|grep -v NAME|awk \'{print $1}\'|grep -v master);do echo -n \"$node  \";kubectl describe node $node|egrep -q \"\s+Ready\s+False\";echo $?;done'
        
        # check all nodes, see it as failed if any one node failed
        cmd = 'for node in $(kubectl get nodes|grep -v NAME|awk \'{print $1}\'|grep -v master);do kubectl describe node $node;done|egrep \"\s+Ready\" |egrep -q \"\s+Ready\s+[False|Unknown]\";echo $?'        
        # cmd = 'journalctl -n 10000 -u kubelet | grep -q \'PLEG is not healthy\';echo $?'  # run on each node 
        if commands.getstatusoutput(cmd) == '0':  # found 'False' 
            metric_value = 0                        # '0' as defined by Chen xin indicating failed 
        return metric_value

        
    def getDockerPs(self):
        metric_value = 2
        url = 'http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json'  # requirement: chmod a+rw /var/run/docker.sock
        s = requests_unixsocket.Session()
        r = s.get(url)
        # requests_unixsocket.monkeypatch()
        # r = requests.get(url)
        # docker_ps_status = r.status_code        
        # return int(docker_ps_status)
        if r.status_code != 200:
            metric_value = 0
        return metric_value
        
if __name__ == '__main__':
    mf = MetricBook()
    func = getattr(mf,mf.metrics['docker_ps']['call_back'])
    rt = func()
    print rt
    print 'ok'
