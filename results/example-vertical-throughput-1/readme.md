# Reflection over benchmark

The reason for having a throughput greater than or equal to 150 is because, through the Grafana UI, I noticed that a single user on average made 200 requests. Therefore, I thought it would be reasonable to set the threshold at 150 with the mean as the query aggregation. However, since the mean is always higher than 150, the scalability assessment of this threshold needs to be adjusted dynamically based on the loading, instead of using a static value.

Based on this assessment, the system can handle up to 5 users with half a CPU and 1GB memory, and up to 21 users with 1 CPU and 2GB memory, with an average of 200 requests per minute from each user.