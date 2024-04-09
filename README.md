
# Project Overview
This project analyzes vertical and horizontal scaling strategies in cloud-native applications. By using metrics and Service Level Objectives (SLOs), providing insights into scaling practices in Kubernetes environments. In cloud-native applications, scalability is extremely important. This project aims to investigate the differences between vertical and horizontal scaling strategies. We will analyze their impact on application performance and cost-effectiveness, particularly under varying load conditions. By using a series of metrics and Service Level Objectives (SLOs), we hope to provide valuable insights into scaling practices within Kubernetes environments.

## Requirements
- For local testing, it is recommended to start with Minikube and then move on to Kind to familiarize yourself with worker/manager roles and kubectl commands. A configuration file for creating a multi-node cluster exists inside the help folder of this repository.
- Deployment for these test happend via **Digital Ocean Kubernetes**, with the deployment managed by abstract infrastrucutre (PaaS). Each node had 4 vCPU and 8GB ram, a total of **40 vCPU** and **80GB ram**.

###  Prometheus Query Language 
To address our research question, we focus on three key SLOs: **Throughput**, **Latency**, and **UILatency**. These metrics serve as indicators of an application's performance and reliability, providing a basis for comparing scaling strategies.


- **Throughput**: Measures the application's capability to handle users' requests simultaneously, offering insights into its load-handling efficiency.

```sh
sum(rate(osm_request_total[1m]))
```
This query calculates the sum of the rate of requests to the 'teastore-app' over a 1-minute window, providing an average request per minute (RPM) value.

- **Latency:** Tracking the response time of requests is crucial for a good user experience. 
  
```sh
histogram_quantile(0.95, sum(rate(osm_request_duration_ms_bucket[1m])) by (le))
```
This calculation identifies the 95th percentile of request latency by averaging the response times over a 1-minute window. Indicating that 95% of requests are processed within this threshold, with only 5% exceeding it. 

- **UILatency:**  This involves monitoring the response times of the WebUI service, with the aim of keeping it below 200ms.

```sh
histogram_quantile(0.95, sum(irate(osm_request_duration_ms_bucket{destination_name='teastore_webui'}[1m])) by (le, destination_name))
``` 
This calculation identifies the 95th percentile of request webui latency by averaging the response times over a 1-minute window. Indicating that 95% of requests are processed within this threshold, with only 5% exceeding it. 

### Benchmark
In each **results** folder, you will find the benchmark file that was used for the assessment. At the end of the benchmark file, you will find the SLO (Service Level Objective) defined, which determines whether the resource capacity should be increased or the resource demand should be increased. If the resource does not meet the SLO, then the resource capacity will be increased, otherwise, the load capacity will be increased.

This file also explains the mechanisms behind horizontal and vertical scaling. For instance, it outlines how vertical scaling functions, such as allocating 500Mi of CPU resulting in 1GB of memory allocation. You only need to define the CPU limit for each service. Additionally, the file specifies the "**instances**," allowing you to define the number of service instances you want for each test.


#### SLO example from benchmark.yaml

```yaml
  slos:
    - sloType: "generic"
      name: "throughput"
      prometheusUrl: "http://prometheus-operated:9090"
      offset: 0
      properties:
        externalSloUrl: "http://localhost:8082"
        promQLQuery: "sum(rate(osm_request_total[1m]))"
        warmup: 600
        queryAggregation: "mean"
        repetitionAggregation: "median"
        operator: "gte"
        thresholdFromExpression: "180 * L * 0.8"
```
Example of an dynamic relative the amount of users (180 RPM per user) with 80% threshold. Including a 10 minute warm up, to let all services to setup before a load test.

To request metrics using Prometheus Query Language (PromQL), you need to define a query that specifies the metrics you want to request and how the resulting time series should be evaluated. You can use the `promQLQuery` field for this (recommendation, test the PromQL query inside of the Grafana UI before running it inside of benchmark). Once you have defined the query, you can use `queryAggregation` to specify how the resulting time series should be aggregated to a single value and `repetitionAggregation` to describe how the results of multiple repetitions should be aggregated. The possible values for aggregation include mean, median, mode, sum, count, max etc. 

After aggregation, the result can be checked against a `threshold`, which you can set using the `operator` field. The operator specifies whether the result must be less than (`lt`), less than or equal to (`lte`), greater than (`gt`), or greater than or equal to (`gte`) the threshold.

If you don't want to set a static threshold, you can set it relative to the tested load with `thresholdRelToLoad` or relative to the tested resource value with `thresholdRelToResources`. For example, if you set `thresholdRelToLoad: 0.01`, the threshold will be 1% of the generated load in each experiment. You can also define more complex thresholds using `thresholdFromExpression`. This field accepts a mathematical expression with two variables `L` and `R`. Please check [this documentation](https://github.dev/cau-se/theodolite/tree/main/theodolite/src/main/kotlin/rocks/theodolite/core) for more information.


### Execution
```yaml
apiVersion: theodolite.rocks/v1beta1
kind: execution
metadata:
  name: teastore-vertical-3
spec:
  benchmark: teastore
  load:
    loadType: "NumUsers"
    loadValues: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
  resources:
    resourceType: "PodResources"
    resourceValues: [500, 1000, 1500, 2000, 2500, 2800]
  slos:
    - name: "throughput"
      properties:
        warmup: 600
        thresholdFromExpression: "180 * L * 0.8"
  execution:
    strategy:
      name: "RestrictionSearch"
      restrictions:
        - "LowerBound"
      searchStrategy: "LinearSearch"
    duration: 1200  # in seconds
    repetitions: 1
  configOverrides: []
```

This is an example execution configuration that showcases an approach to assess the scalability of the 'teastore' system. The evaluation consists of a series of tests conducted across a range of user numbers, from 1 to 21. The tests involve allocating resources ranging from 500 to 2800Mi CPU, and the RAM memory allocation is double the CPU for each test case.

The **RestrictionSearch** strategy, uses the **LowerBound** restriction. Which systematically searches for the lowest resource configuration that satisfies the SLO criteria. It utilizes a **LinearSearch** methodology, iterating through each resource levels and user counts, executing each test for 1200 seconds. If the SLO is fulfilled and true, then the resource demands decrease otherwise, resource capacity will increase.






