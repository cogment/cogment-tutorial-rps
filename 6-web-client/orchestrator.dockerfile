FROM cogment/orchestrator:v2.0.0
ADD cogment.yaml .
ADD *.proto .
CMD ["--params=cogment.yaml"]
