""" TODO: Module docstring."""
import json
import logging
from typing import Callable
import requests


class BuildkiteError(Exception):
    """TODO: Class docstring."""


class BuildkiteSession(requests.Session):
    """TODO: Class docstring."""

    def init_basic_auth(self, api_access_token: str):
        """TODO: Function docstring."""
        self.headers.update(
            {
                "Authorization": f"Bearer {api_access_token}",
            }
        )


class BuildkiteClient:
    """TODO: Class docstring."""
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
        headers: dict = None,
    ) -> requests.Response:
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
                f"BuildkiteClient.__request: method must be one of {valid_methods}.",
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
            req.headers["Content-Type"] = "application/json"

        # Execute the request, and return the JSON payload.
        prep = self.__session.prepare_request(req)
        resp = self.__session.send(prep)
        return resp

    # Access Token API
    # https://buildkite.com/docs/apis/rest-api/access-token

    # The Access Token API allows you to inspect and revoke an API Access Token.
    # This can be useful if you find a token, can't identify its owner, and you
    # want to revoke it.

    def get_current_token(self) -> requests.Response:
        """Get the current token
        https://buildkite.com/docs/apis/rest-api/access-token#get-the-current-token

        Returns details about the API Access Token that was used to authenticate
        the request.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path="access-token",
        )

    def revoke_current_token(self) -> requests.Response:
        """Revoke the current token
        https://buildkite.com/docs/apis/rest-api/access-token#revoke-the-current-token

        Revokes the API Access Token that was used to authenticate the request.
        Once revoked, the token can no longer be used for further requests.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="DELETE",
            path="access-token",
        )

    # Organizations API
    # https://buildkite.com/docs/apis/rest-api/organizations

    def list_organizations(self) -> requests.Response:
        """List organizations
        https://buildkite.com/docs/apis/rest-api/organizations#list-organizations

        Returns a paginated list of the user's organizations.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path="organizations",
        )

    def get_organization(self, org_slug: str) -> requests.Response:
        """Get an organization
        https://buildkite.com/docs/apis/rest-api/organizations#get-an-organization

        Returns the details of a specific organization.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}",
        )

    # Pipelines API
    # https://buildkite.com/docs/apis/rest-api/pipelines

    def list_pipelines(self, org_slug: str) -> requests.Response:
        """List pipelines
        https://buildkite.com/docs/apis/rest-api/pipelines#list-pipelines

        Returns a paginated list of an organization's pipelines.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines",
        )

    def get_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """Get a pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#get-a-pipeline

        Returns the details of an organization's specific pipeline.

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
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}",
        )

    def create_yaml_pipeline(
        self, org_slug: str, pipeline_definition: dict
    ) -> requests.Response:
        """Create a YAML pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#create-a-yaml-pipeline

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
            method="POST",
            path=f"organizations/{org_slug}/pipelines",
            data=json.dumps(pipeline_definition),
        )

    def create_visual_step_pipeline(
        self, org_slug: str, pipeline_definition: dict
    ) -> requests.Response:
        """Create a visual step pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#create-a-visual-step-pipeline

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
            method="POST",
            path=f"organizations/{org_slug}/pipelines",
            data=json.dumps(pipeline_definition),
        )

    def update_pipeline(
        self, org_slug: str, pipeline_slug: str, pipeline_definition: dict
    ) -> requests.Response:
        """Update a pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#update-a-pipeline

        Updates one or more properties of an existing pipeline.

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
            method="PATCH",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}",
            data=json.dumps(pipeline_definition),
        )

    def archive_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """Archive a pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#archive-a-pipeline

        Archived pipelines are read-only, and are hidden from Pipeline pages by
        default. Builds, build logs, and artifacts are preserved.

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
            method="POST",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/archive",
        )

    def unarchive_pipeline(
        self, org_slug: str, pipeline_slug: str
    ) -> requests.Response:
        """Unarchive a pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#unarchive-a-pipeline

        Unarchived pipelines are editable, and are shown on the Pipeline pages.

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
            method="POST",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/unarchive",
        )

    def delete_pipeline(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """Delete a pipeline
        https://buildkite.com/docs/apis/rest-api/pipelines#delete-a-pipeline

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
            method="DELETE",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}",
        )

    def add_webhook(self, org_slug: str, pipeline_slug: str) -> requests.Response:
        """Add a webhook
        https://buildkite.com/docs/apis/rest-api/pipelines#add-a-webhook

        Create a GitHub webhook for an existing pipeline that is configured
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
            method="POST",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/webhook",
        )

    # Builds API
    # https://buildkite.com/docs/apis/rest-api/builds

    # Build number vs build ID

    # All builds have both an ID which is unique within the whole of Buildkite
    # (build ID), and a sequential number which is unique to the pipeline (build
    # number).

    # For example build number 27 of the Test pipeline might have a build ID of
    # f62a1b4d-10f9-4790-bc1c-e2c3a0c80983.

    def list_all_builds(self, params: dict = None) -> requests.Response:
        """List all builds
        https://buildkite.com/docs/apis/rest-api/builds#list-all-builds

        Returns a paginated list of all builds across all the user's
        organizations and pipelines. If usingtoken-based authentication the list
        of builds will be for the authorized organizations only. Builds are
        listed in the order they were created (newest first).

        Args:
            params (OPTIONAL):
                branch: Filters the results by the given branch or branches.
                    Example: {'branch':'master'} returns all builds on the master branch
                    Example: {'branch[]':['master','testing']} returns all builds on master and testing branches
                commit: Filters the results by the commit (only works for full SHA, not for shortened ones).
                    Example: {'commit':'long-hash'}
                    Example: {'commit[]':['sha2','sha1']} query for multiple commits using Rails array syntax
                created_from: Filters the results by builds created on or after the given time (in ISO 8601 format)
                    Example: {'created_from':'2022-07-23T02:42:43Z'}
                created_to: Filters the results by builds created before the given time (in ISO 8601 format)
                    Example: {'created_to':'2022-08-28T02:42:43Z'}
                creator: Filters the results by the user who created the build
                    Example: {'creator':'5acb99cf-d349-4189-b361-d1b9f36d70d7'}
                finished_from: Filters the results by builds finished on or after the given time (in ISO 8601 format)
                    Example: {'finished_from':'2022-07-26T02:42:43Z'}
                include_retried_jobs: Include all retried job executions in each build's jobs list. Without this parameter, you'll see only the most recently run job for each step.
                    Example: {'include_retried_jobs':'true'}
                meta_data: Filters the results by the given meta-data.
                    Example: {'meta_data[some-key]':'some-value'}
                state: Filters the results by the given build state. The finished state is a shortcut to automatically search for builds with passed, failed, blocked, canceled states.
                    Valid states: running, scheduled, passed, failed, blocked, canceled, canceling, skipped, not_run, finished
                    Example: {'state':'passed'} returns all passed builds
                    Example: {'state[]':['scheduled','running']} returns all scheduled and running builds

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path="builds",
            params=params,
        )

    def list_organization_builds(
        self, org_slug: str, params: dict = None
    ) -> requests.Response:
        """List builds for an organization
        https://buildkite.com/docs/apis/rest-api/builds#list-builds-for-an-organization

        Returns a paginated list of an organization's builds across all of an
        organization's pipelines. Builds are listed in the order they were
        created (newest first).

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            params (OPTIONAL):
                branch: Filters the results by the given branch or branches.
                    Example: {'branch':'master'} returns all builds on the master branch
                    Example: {'branch[]':['master','testing']} returns all builds on master and testing branches
                commit: Filters the results by the commit (only works for full SHA, not for shortened ones).
                    Example: {'commit':'long-hash'}
                    Example: {'commit[]':['sha2','sha1']} query for multiple commits using Rails array syntax
                created_from: Filters the results by builds created on or after the given time (in ISO 8601 format)
                    Example: {'created_from':'2022-07-23T02:42:43Z'}
                created_to: Filters the results by builds created before the given time (in ISO 8601 format)
                    Example: {'created_to':'2022-08-28T02:42:43Z'}
                creator: Filters the results by the user who created the build
                    Example: {'creator':'5acb99cf-d349-4189-b361-d1b9f36d70d7'}
                finished_from: Filters the results by builds finished on or after the given time (in ISO 8601 format)
                    Example: {'finished_from':'2022-07-26T02:42:43Z'}
                include_retried_jobs: Include all retried job executions in each build's jobs list. Without this parameter, you'll see only the most recently run job for each step.
                    Example: {'include_retried_jobs':'true'}
                meta_data: Filters the results by the given meta-data.
                    Example: {'meta_data[some-key]':'some-value'}
                state: Filters the results by the given build state. The finished state is a shortcut to automatically search for builds with passed, failed, blocked, canceled states.
                    Valid states: running, scheduled, passed, failed, blocked, canceled, canceling, skipped, not_run, finished
                    Example: {'state':'passed'} returns all passed builds
                    Example: {'state[]':['scheduled','running']} returns all scheduled and running builds

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/builds",
            params=params,
        )

    def list_pipeline_builds(
        self, org_slug: str, pipeline_slug: str, params: dict = None
    ) -> requests.Response:
        """List builds for a pipeline
        https://buildkite.com/docs/apis/rest-api/builds#list-builds-for-a-pipeline

        Returns a paginated list of a pipeline's builds. Builds are listed in
        the order they were created (newest first).

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            params (OPTIONAL):
                branch: Filters the results by the given branch or branches.
                    Example: {'branch':'master'} returns all builds on the master branch
                    Example: {'branch[]':['master','testing']} returns all builds on master and testing branches
                commit: Filters the results by the commit (only works for full SHA, not for shortened ones).
                    Example: {'commit':'long-hash'}
                    Example: {'commit[]':['sha2','sha1']} query for multiple commits using Rails array syntax
                created_from: Filters the results by builds created on or after the given time (in ISO 8601 format)
                    Example: {'created_from':'2022-07-23T02:42:43Z'}
                created_to: Filters the results by builds created before the given time (in ISO 8601 format)
                    Example: {'created_to':'2022-08-28T02:42:43Z'}
                creator: Filters the results by the user who created the build
                    Example: {'creator':'5acb99cf-d349-4189-b361-d1b9f36d70d7'}
                finished_from: Filters the results by builds finished on or after the given time (in ISO 8601 format)
                    Example: {'finished_from':'2022-07-26T02:42:43Z'}
                include_retried_jobs: Include all retried job executions in each build's jobs list. Without this parameter, you'll see only the most recently run job for each step.
                    Example: {'include_retried_jobs':'true'}
                meta_data: Filters the results by the given meta-data.
                    Example: {'meta_data[some-key]':'some-value'}
                state: Filters the results by the given build state. The finished state is a shortcut to automatically search for builds with passed, failed, blocked, canceled states.
                    Valid states: running, scheduled, passed, failed, blocked, canceled, canceling, skipped, not_run, finished
                    Example: {'state':'passed'} returns all passed builds
                    Example: {'state[]':['scheduled','running']} returns all scheduled and running builds

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds",
            params=params,
        )

    def get_build(
        self, org_slug: str, pipeline_slug: str, build_number: str, params: dict = None
    ) -> requests.Response:
        """Get a build
        https://buildkite.com/docs/apis/rest-api/builds#get-a-build

        Returns a paginated list of a pipeline's builds. Builds are listed in
        the order they were created (newest first).

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            params (OPTIONAL):
                include_retried_jobs: Include all retried job executions in each build's jobs list. Without this parameter, you'll see only the most recently run job for each step.
                Example: {'include_retried_jobs':'true'}

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}",
            params=params,
        )

    def create_build(
        self, org_slug: str, pipeline_slug: str, build_number: str, params: dict = None
    ) -> requests.Response:
        """Create a build
        https://buildkite.com/docs/apis/rest-api/builds#create-a-build

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            params (REQUIRED):
                commit: Ref, SHA or tag to be built.
                    Example: {'commit':'HEAD'}
                    Note: Before running builds on tags, make sure your agent is fetching git tags .
                branch: Branch the commit belongs to. This allows you to take advantage of your pipeline and step-level branch filtering rules.
                    Example: {'branch':'master'}
            params (OPTIONAL):
                author: A hash with a "name" and "email" key to show who created this build.
                    Default value: the user making the API request.
                    Example: {'author': {'name': 'John Doe', 'email': 'john.doe@anonymail.io'}}
                clean_checkout: Force the agent to remove any existing build directory and perform a fresh checkout.
                    Default value: false.
                    Example: {'clean_checkout':'false'}
                env: Environment variables to be made available to the build.
                    Default value: {}.
                    Example: {'env': {'MY_ENV_VAR':'some_value'}}
                ignore_pipeline_branch_filters: Run the build regardless of the pipeline's branch filtering rules. Step branch filtering rules will still apply.
                    Default value: false.
                    Example: {'ignore_pipeline_branch_filters':'false'}
                message: Message for the build.
                    Example: {'message':'Testing all the things :rocket:'}
                meta_data 	A hash of meta-data to make available to the build.
                    Default value: {}.
                    Example: {'meta_data': {'some build data': 'value', 'other build data': 'true'}}
                pull_request_base_branch: For a pull request build, the base branch of the pull request.
                    Example: {'pull_request_base_branch': 'master'}
                pull_request_id: For a pull request build, the pull request number.
                    Example: {'pull_request_id':'42'}
                pull_request_repository: For a pull request build, the git repository of the pull request.
                    Example: {'pull_request_repository':'git://github.com/my-org/my-repo.git'}

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="POST",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}",
            params=params,
        )

    def cancel_build(
        self, org_slug: str, pipeline_slug: str, build_number: str
    ) -> requests.Response:
        """Cancel a build
        https://buildkite.com/docs/apis/rest-api/builds#cancel-a-build

        Cancels the build if its state is either scheduled or running.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="PUT",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/cancel",
        )

    def rebuild_build(
        self, org_slug: str, pipeline_slug: str, build_number: str
    ) -> requests.Response:
        """Rebuild a build
        https://buildkite.com/docs/apis/rest-api/builds#rebuild-a-build

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="PUT",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/rebuild",
        )

    # Jobs API
    # https://buildkite.com/docs/apis/rest-api/jobs

    def retry_job(
        self, org_slug: str, pipeline_slug: str, build_number: str, job_id: str
    ) -> requests.Response:
        """Retry a job
        https://buildkite.com/docs/apis/rest-api/jobs#retry-a-job

        Retries a failed or timed_out job. You can only retry each job.id
        once. To retry a "second time" use the new job.id returned in the first
        retry query.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="PUT",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/retry",
        )

    def unblock_job(
        self,
        org_slug: str,
        pipeline_slug: str,
        build_number: str,
        job_id: str,
        params: dict = None,
    ) -> requests.Response:
        """Unblock a job
        https://buildkite.com/docs/apis/rest-api/jobs#unblock-a-job

        Unblocks a build's "Block pipeline" job. The job's unblockable property
        indicates whether it is able to be unblocked, and the unblock_url
        property points to this endpoint.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

            params (OPTIONAL):
                unblocker: The user id of the person activating the job.
                    Default value: the user making the API request.
                fields: The values for the block step's fields: https://buildkite.com/docs/pipelines/block-step#block-step-attributes.
                    Example: {'release-name':'Flying Dolpin'}

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="PUT",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/unblock",
            params=params,
        )

    def get_job_log(
        self, org_slug: str, pipeline_slug: str, build_number: str, job_id: str
    ) -> requests.Response:
        """Get a job's log output
        https://buildkite.com/docs/apis/rest-api/jobs#get-a-jobs-log-output

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/log",
        )

    def delete_job_log(
        self, org_slug: str, pipeline_slug: str, build_number: str, job_id: str
    ) -> requests.Response:
        """Delete a job's log output
        https://buildkite.com/docs/apis/rest-api/jobs#delete-a-jobs-log-output

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="DELETE",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/log",
        )

    def get_job_env_vars(
        self, org_slug: str, pipeline_slug: str, build_number: str, job_id: str
    ) -> requests.Response:
        """Get a job's environment variables
        https://buildkite.com/docs/apis/rest-api/jobs#get-a-jobs-environment-variables

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/env",
        )

    # Agents API
    # https://buildkite.com/docs/apis/rest-api/agents

    def list_agents(self, org_slug: str, params: dict = None) -> requests.Response:
        """List agents
        https://buildkite.com/docs/apis/rest-api/agents#list-agents

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            params (OPTIONAL):
                name: Filters the results by the given agent name
                    Example: {'name':'ci-agent-1'}
                hostname: Filters the results by the given hostname
                    Example: {'hostname':'ci-box-1'}
                version: Filters the results by the given exact version number
                    Example: {'version':'2.1.0'}

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/agents",
            params=params,
        )

    def get_agent(self, org_slug: str, agent_id: str) -> requests.Response:
        """Get an agent
        https://buildkite.com/docs/apis/rest-api/agents#get-an-agent

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().
            agent_id: All agent have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/agents/{agent_id}",
        )

    def stop_agent(
        self, org_slug: str, agent_id: str, params: dict = None
    ) -> requests.Response:
        """Stop an agent
        https://buildkite.com/docs/apis/rest-api/agents#stop-an-agent

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().
            agent_id: All agent have a unique ID.

            params (OPTIONAL):
                force: If the agent is currently processing a job, the job and the build will be canceled.
                    Default: true
                    Example: {'force':'false'}

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="PUT",
            path=f"organizations/{org_slug}/agents/{agent_id}/stop",
            params=params,
        )

    # Artifacts API
    # https://buildkite.com/docs/apis/rest-api/artifacts

    # Artifact data model

    # An artifact is a file uploaded by your agent during the execution of a
    # build's job. The contents of the artifact can be retrieved using the
    # download_url and the artifact download API.
    #     id:      	        ID of the artifact
    #     job_id: 	        ID of the job
    #     url:     	        Canonical API URL of the artifact
    #     download_url: 	Artifact Download API URL for the artifact
    #     state:            State of the artifact (new, error, finished,
    #                           deleted, expired)
    #     path:             Path of the artifact
    #     dirname:     	    Path of the artifact excluding the filename
    #     filename:    	    Filename of the artifact
    #     mime_type:   	    Mime type of the artifact
    #     file_size:   	    File size of the artifact in bytes
    #     sha1sum:     	    SHA-1 hash of artifact contents as calculated by the
    #                           agent

    def list_build_artifacts(
        self, org_slug: str, pipeline_slug: str, build_number: str
    ) -> requests.Response:
        """List artifacts for a build
        https://buildkite.com/docs/apis/rest-api/artifacts#list-artifacts-for-a-build

        Returns a paginated list of a build's artifacts across all of its jobs.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/artifacts",
        )

    def list_job_artifacts(
        self, org_slug: str, pipeline_slug: str, build_number: str, job_id: str
    ) -> requests.Response:
        """List artifacts for a job
        https://buildkite.com/docs/apis/rest-api/artifacts#list-artifacts-for-a-job

        Returns a paginated list of a job's artifacts.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/artifacts",
        )

    def get_artifact(
        self,
        org_slug: str,
        pipeline_slug: str,
        build_number: str,
        job_id: str,
        artifact_id: str,
    ) -> requests.Response:
        """Get an artifact
        https://buildkite.com/docs/apis/rest-api/artifacts#get-an-artifact

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

            artifact_id: All artifacts have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/artifacts/{artifact_id}",
        )

    def download_artifact(
        self,
        org_slug: str,
        pipeline_slug: str,
        build_number: str,
        job_id: str,
        artifact_id: str,
    ) -> requests.Response:
        """Download an artifact
        https://buildkite.com/docs/apis/rest-api/artifacts#download-an-artifact

        Returns a 302 response to a URL for downloading an artifact. The URL
        will be returned in the response body and the Location HTTP header.

        You should assume the URL returned will only be valid for 60 seconds,
        unless you've used your own S3 bucket where the URL will be the standard
        public S3 URL to the artifact object.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

            artifact_id: All artifacts have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/artifacts/{artifact_id}/download",
        )

    def delete_artifact(
        self,
        org_slug: str,
        pipeline_slug: str,
        build_number: str,
        job_id: str,
        artifact_id: str,
    ) -> requests.Response:
        """Delete an artifact
        https://buildkite.com/docs/apis/rest-api/artifacts#delete-an-artifact

        The artifact record is marked as deleted in the Buildkite database, and
        the artifact itself is removed from the Buildkite AWS S3 bucket. It will
        no longer be displayed in the job or build artifact lists, and it will
        not be returned by the artifact APIs.

        If the artifact was uploaded using the agent's custom AWS S3, Google
        Cloud, or Artifactory storage support, the file will not be
        automatically deleted from that storage. You must delete the file from
        your private storage yourself.

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

            job_id: All jobs have a unique ID.

            artifact_id: All artifacts have a unique ID.

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="DELETE",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/jobs/{job_id}/artifacts/{artifact_id}",
        )

    # Annotations API
    # https://buildkite.com/docs/apis/rest-api/annotations

    # Annotation data model

    # An annotation is a snippet of Markdown uploaded by your agent during the
    # execution of a build's job. Annotations are created using the
    # buildkite-agent annotate command from within a job.
    #     id:         ID of the annotation
    #     context:    The "context" specified when annotating the build. Only one
    #                 annotation per build may have any given context value.
    #     style:      The style of the annotation. Can be `success`, `info`,
    #                 `warning` or `error`.
    #     body_html:  Rendered HTML of the annotation's body
    #     created_at:	When the annotation was first created
    #     updated_at:	When the annotation was last added to or replaced

    def list_build_annotations(
        self, org_slug: str, pipeline_slug: str, build_number: str
    ) -> requests.Response:
        """List annotations for a build
        https://buildkite.com/docs/apis/rest-api/annotations#list-annotations-for-a-build

        Args:
            org_slug: The organization slug is a simplified version of the
                organisation name. You can find this within the full details of
                an organization using list_organizations().

            pipeline_slug: The pipeline slug is a simplified version of the
                pipeline name. You can find this within the full details of a
                pipeline using list_pipelines().

            build_number: All builds have both an ID which is unique within the
                whole of Buildkite (build ID), and a sequential number which is
                unique to the pipeline (build number).

        Returns:
            requests.Response: The response from the API call.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/pipelines/{pipeline_slug}/builds/{build_number}/annotations",
        )

    # Emojis API
    # https://buildkite.com/docs/apis/rest-api/emojis

    # Buildkite supports emojis (using the :emoji: syntax) in build step names and
    # build log header groups. The Emoji API allows you to fetch the list of
    # emojis for an organization so you can display emojis correctly in your own
    # integrations.

    # Emojis can be found in text using the pattern /:([\w+-]+):/

    def list_emojis(self, org_slug: str) -> requests.Response:
        """Returns a list of all the emojis for a given organization, including
        custom emojis and aliases. This list is not paginated.
        """
        return self.__request(
            method="GET",
            path=f"organizations/{org_slug}/emojis",
        )

    # User API
    # https://buildkite.com/docs/apis/rest-api/user

    # The User API endpoint allows you to inspect details about the user account
    # that owns the API token that is currently being used.

    def get_current_user(self) -> requests.Response:
        """Returns basic details about the user account that sent the request."""
        return self.__request(
            method="GET",
            path="user",
        )

    # Meta API
    # https://buildkite.com/docs/apis/rest-api/meta

    # The Meta API provides information about Buildkite, including a list of
    # Buildkite's IP addresses.

    # It does not require authentication.

    def get_meta_information(self) -> requests.Response:
        """Returns an object with properties describing Buildkite.

        webhook_ips is a list of IP addresses in CIDR notation that Buildkite
        uses to send outbound traffic such as webhooks and commit statuses.
        These are subject to change from time to time. Buildkite recommend
        checking for new addresses daily, and will try to advertise new
        addresses for at least 7 days before they are used.
        """
        return self.__request(
            method="GET",
            path="meta",
        )


if __name__ == "__main__":
    print("Please import the module to interface with the classes and functions.")
