import requests
import os


# Ongoing build effort - all functions are translated from API calls documented
# within the following pages:
#   https://buildkite.com/docs/apis/rest-api

# URL encoding
import urllib.parse

# Handling different file/content types
import json

class BuildkiteSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(BuildkiteSession, self).__init__(*args, **kwargs)
    
    def init_basic_auth(self, api_access_token: str):
        self.headers.update(
            {
                'Authorization': f'Bearer {api_access_token}'
            }
        )

class BuildkiteClient:
    def __init__(self, api_access_token: str):
        # Initialize the session.
        self.__session = BuildkiteSession()

        self.__session.init_basic_auth(api_access_token)
        self.__endpoint = "https://api.buildkite.com"

    def __request(
        self,
        method: str,
        path: str,
        version: int = 2,
        params: dict = None,
        data: dict = None,
        headers: dict = None
    ):
        """Basic function to remove this snippet of code out of every other
        function.

        Args:
            method: what type of request is being made (ie - GET, POST, DELETE).

            path: the target API URL.

            version: the API version, default is 2.

            params: any data that needs to be sent through a query string.

            data: any data that needs to be sent through the message body rather
                than through parameters in the query string. Only required for
                POST, PUT, and PATCH.

            headers: any extra headers to add to the base auth headers.

        Returns:
            requests.Response: The response from the API call.
        """
        # There are a specific set of request types that can be executed.
        valid_methods = [
            "GET",
            "OPTIONS",
            "HEAD",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]
        if method not in valid_methods:
            raise ValueError(
                f'BuildkiteClient.__request: method must be one of {valid_methods}.'
            )

        if headers is None:
            headers = {}

        req = requests.Request(
            method=method,
            url=f"{self.__endpoint}/v{version}/{path}",
            params=params,
            data=data,
            headers=headers,
        )

        # If any data is being passed, it will need to have the Content-Type header set.
        if data is not None:
            req.headers['Content-Type'] = 'application/json'

        # Execute the request, and return the JSON payload.
        prep = self.__session.prepare_request(req)
        resp = self.__session.send(prep)
        return resp

    def list_organizations(self) -> requests.Response:
        """Returns a paginated list of the user's organizations.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='GET',
            path=f'organizations'
        )

    def get_organization(self, org_slug: str) -> requests.Response:
        """ Returns the details of a specific organization.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='GET',
            path=f'organizations/{org_slug}'
        )

    def list_pipelines(self, org_slug: str) -> requests.Response:
        """ Returns a paginated list of an organization's pipelines.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='GET',
            path=f'organizations/{org_slug}/pipelines'
        )

    def get_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """ Returns the details of an organization's specific pipeline.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='GET',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}'
        )

    def create_yaml_pipeline(self, org_slug: str, pipeline_definition: dict) -> requests.Response:
        """ Creates a YAML pipeline.

        YAML pipelines are the recommended way to manage your pipelines. To
        create a YAML pipeline using this function, set the configuration key in
        your json request body to the YAML you want in your pipeline.

        For example, to create a pipeline called "My Pipeline" containing the
        following command step:

            steps:
             - command: "script/release.sh"
               name: "Build :package:"

        make the following function call. Make sure to escape the quotes (") in
        your YAML, and to replace line breaks with \n:

            pipeline_definition = {
                "name": "My Pipeline X",
                "repository": "git@github.com:acme-inc/my-pipeline.git",
                "configuration": "env:\n \"FOO\": \"bar\"\nsteps:\n - command: \"script/release.sh\"\n   \"name\": \"Build 📦\""
            }

            buildkite_client.create_yaml_pipeline(org_slug, pipeline_definition)

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_definition: The pipeline definition.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='POST',
            path=f'organizations/{org_slug}/pipelines',
            data=json.dumps(pipeline_definition)
        )

    def create_visual_step_pipeline(self, org_slug: str, pipeline_definition: dict) -> requests.Response:
        """ Creates a visual step pipeline.

        YAML pipelines are the recommended way to manage your pipelines but if
        you're still using visual steps you can add them by setting the steps
        key in your json request body to an array of steps:

            pipeline_definition = {
                "name": "My Pipeline",
                "repository": "git@github.com:acme-inc/my-pipeline.git",
                "steps": [
                    {
                        "type": "script",
                        "name": "Build :package:",
                        "command": "script/release.sh"
                    },
                    {
                        "type": "waiter"
                    },
                    {
                        "type": "script",
                        "name": "Test :wrench:",
                        "command": "script/release.sh",
                        "artifact_paths": "log/*"
                    },
                    {
                        "type": "manual",
                        "label": "Deploy"
                    },
                    {
                        "type": "script",
                        "name": "Release :rocket:",
                        "command": "script/release.sh",
                        "branch_configuration": "master",
                        "env": {
                        "AMAZON_S3_BUCKET_NAME": "my-pipeline-releases"
                        },
                        "timeout_in_minutes": 10,
                        "agent_query_rules": ["aws=true"]
                    },
                    {
                        "type": "trigger",
                        "label": "Deploy :ship:",
                        "trigger_project_slug": "deploy",
                        "trigger_commit": "HEAD",
                        "trigger_branch": "master",
                        "trigger_async": true
                    }
                ]
            }

            buildkite_client.create_visual_step_pipeline(org_slug, pipeline_definition)

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_definition: The pipeline definition.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='POST',
            path=f'organizations/{org_slug}/pipelines',
            data=json.dumps(pipeline_definition)
        )

    def update_pipeline(self, org_slug: str, pipeline_slug: str, pipeline_definition: dict) -> requests.Response:
        """ Updates one or more properties of an existing pipeline.

        To update a pipeline's YAML steps, make the following function call,
        passing the configuration attribute in the pipeline_definition:

            pipeline_definition = {
                "repository": "git@github.com:acme-inc/new-repo.git",
                "configuration": "steps:\n  - command: \"new.sh\"\n    agents:\n    - \"myqueue=true\""
            }

            buildkite_client.update_pipeline(org_slug, pipeline_slug, pipeline_definition)


        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            pipeline_definition: The pipeline definition.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='PATCH',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}'
        )

    def archive_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """ Archived pipelines are read-only, and are hidden from Pipeline pages
        by default. Builds, build logs, and artifacts are preserved.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='POST',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}/archive'
        )

    def unarchive_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """ Unarchived pipelines are editable, and are shown on the Pipeline
        pages.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='POST',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}/unarchive'
        )

    def delete_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """ Delete a pipeline.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='DELETE',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}'
        )

    def add_webhook(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """ Create a GitHub webhook for an existing pipeline that is configured
        using the BuildKite GitHub App. Pushes to the linked GitHub repository
        will trigger builds.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method='POST',
            path=f'organizations/{org_slug}/pipelines/{pipeline_slug}/webhook'
        )


# Example for using the API.

# Fetch the Buildkite API Token from the env variable "BUILDKITE_TOKEN"
buildkite_token = os.environ["BUILDKITE_TOKEN"]

# Create the Buildkite Client object
bk_client = BuildkiteClient(buildkite_token)

# Fetch the slug of the first organization for the specified API token.
org_slug = bk_client.list_organizations().json()[0]['slug']

# Fetch the pipelines
org_pipelines = bk_client.list_pipelines(org_slug).json()

# Print the name of all pipelines for this organization.
for pipeline in org_pipelines:
    print(pipeline['name'])
