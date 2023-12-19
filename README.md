# py-buildkite
A simple Python-based SDK for the Buildkite API.

> [!NOTE]
> :construction: Be aware that this is an ongoing build effort. Please feel free to submit a PR or reach out if you have any suggestions.

# Introduction
Buildkite is a platform for running fast, secure, and scalable continuous integration pipelines on your own infrastructure.

# API Reference
The API reference for Buildkite can be found within the [Buildkite REST API Documentation](https://buildkite.com/docs/apis/rest-api).

## Usage
``` Python
import os

# Fetch the Buildkite API Token from the env variable "BUILDKITE_TOKEN"
buildkite_token = os.environ["BUILDKITE_TOKEN"]

# Create the Buildkite Client object
buildkite_client = BuildkiteClient(buildkite_token)

# Fetch the slug of the first organization for the specified API token.
org_slug = buildkite_client.list_organizations().json()[0]["slug"]

# Fetch the pipelines
org_pipelines = buildkite_client.list_pipelines(org_slug).json()

# Print the name of all pipelines for this organization.
for pipeline in org_pipelines:
    print(pipeline["name"])
```