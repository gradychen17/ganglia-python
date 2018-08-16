# Ganglia Customized Python Module Design

## Ganglia python module framework
gmond通过[mod_python](https://github.com/ganglia/monitor-core/tree/master/gmond/modules/python), 提供了以python module方式扩展自定义的metric.

要开发gmond python module, ganglia规定须提供以下两个文件:
    - /etc/ganglia/conf.d/<module name>.pyconf
    - /usr/lib64/ganglia/python_modules/<module name>.py
    
.pyconf 配置文件格式
```shell
modules {
  module {
    name     = "my_stats"           # 对应.py文件名
    language = "python"
    params myparam {
        value = 'my param value'    # 传递给.py文件中的 metric_init()函数
    }
  }
}

collection_group {                  # 可以定义多个 collection_group
  collect_every  = 60   
  time_threshold = 15

  metric {
    name = "docker_ps"              # 须对应 metric_init() 函数返回值
    title = "Docker ps status"    
  }
  
  metric {
    name = "metric2"
    title = "Metric title on graph"
  }
 
}
```    

.py 文件须包含三个函数
```python
def metric_init(params):     # params 是.pyconf中的modules.module.params
    listOfDict []           # 每个metric metadata放到一个dictionary里
    d = {'name': '<name>',                  # metric name, 对应pyconf文件的collection_group.metric.name
        'call_back': <handler_function>,    # 返回metric值的函数，gmond会调用这个函数
        'time_max': int(<time_max>),        # Maximum metric value gathering interval
        'value_type': '<data_type>',        # Data type (string, uint, float, double)
        'units': '<label>',                 # Units label
        'slope': '<slope_type>',            # Slope ('zero' constant values, 'both' numeric values)
        'format': '<format>',               # String formatting ('%s', '%u','%f')
        'description': '<description>'}     # Free form metric description
        
    listOfDict.append(d)    
    return listOfDict       # 返回一个包含各个metric metadata的list
    
    
def metric_cleanup():       # gmond shutdown 时会调用这个函数
    pass

def func(name):             # 获取metric value的函数，由gmond调用
                            # name 是对应metric_init函数返回的每个dictionary中的name
    metric_value = ''
    
    return metric_value     # 返回值的类型必须符合metadata定义中的 value_type 和 format
    
```

## My gmond python module interface design
.pyconf 定义module, 以及module中的metric
.py     定义一个接口:
    metric_init(params)  调用一个类MetricFactory，所有的metric metadata定义由类返回
    metric_handler(name) 调用类实例中的实际的函数，用于获取metric value    
    metric_cleanup()
MetricBook.py 接口类的实现    
    metrics 一个常量，定义所有的metric metadata
        def __init__(self):    
                self.metrics =  {
                    'docker_ps': {
                                    'call_back'   : 'getDockerPs',
                                    'time_max'    : 10,
                                    'value_type'  : 'float',
                                    'format'      : '%f',
                                    'units'       : 'XXX',
                                    'slope'       : 'both',  # zero|positive|negative|both
                                    'description' : 'XXX',
                                    'groups'      : 'testgroup',    
                                    },
                    'kubelet': {}                        
                }        
                
        def getDockerPs(self):  metric_handler实现
            pass

## Steps to add a new metric through my gpm interface
1. Add metric configurations in .pyconf, like :
    ```shell
    modules {
        module {
            name = 'my_stats'
            language = 'python'
            params ...
        }
    }
    
    collection_group {
        # Add metric here
        metric {        
            name = "metric2"
            title = "Metric title on graph"
        }
        
    }
    ```

2. Add metric metadata in MetricFactory.py

3. 3rd-party modules 
	requests_unixsocket
