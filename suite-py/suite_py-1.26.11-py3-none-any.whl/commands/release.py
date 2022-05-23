# -*- coding: utf-8 -*-
import re
import sys

import semver
from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.drone_handler import DroneHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.version_handler import DEFAULT_VERSION, VersionHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class Release:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, action, project, config, tokens, flags=None):
        self._action = action
        self._project = project
        self._flags = flags
        self._config = config
        self._tokens = tokens
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = CaptainHook(config)
        self._github = GithubHandler(tokens)
        self._repo = self._github.get_repo(project)
        self._git = GitHandler(project, config)
        self._drone = DroneHandler(config, tokens, repo=project)
        self._countries = _parse_available_countries(self._drone)
        self._version = VersionHandler(self._repo, self._git, self._github)

    def run(self):
        self._stop_if_prod_locked()
        self._git.fetch()

        if len(self._countries) == 0:
            logger.error(
                "Can't determine which countries can be deployed. Try to run `suite-py deploy` instead."
            )
            sys.exit(1)

        if self._action == "create":
            self._create()
        elif self._action == "deploy":
            self._deploy()
        else:
            self._rollback()

    def _stop_if_prod_locked(self):
        request = self._captainhook.status(self._project, "production")
        if request.status_code != 200:
            logger.error("Unable to determine lock status on master.")
            sys.exit(-1)

        request_object = request.json()
        if request_object["locked"]:
            logger.error(
                f"The project is locked in production by {request_object['by']}. Unable to continue."
            )
            sys.exit(-1)

    def _get_release(self, tag):
        with Halo(text="Loading...", spinner="dots", color="magenta"):
            latest_release = self._github.get_latest_release_if_exists(self._repo)
            if latest_release and latest_release.title == tag:
                return latest_release
        return None

    def _create(self):
        latest = self._version.get_latest_version()
        if latest != "":
            logger.info(f"The current release is {latest}")
            commits = self._github.get_commits_since_release(self._repo, latest)

            _check_migrations_deploy(commits)

            message = "\n".join(
                ["* " + c.commit.message.splitlines()[0] for c in commits]
            )

            logger.info(f"\nCommits list:\n{message}\n")

            if not prompt_utils.ask_confirm("Do you want to continue?"):
                sys.exit()

            new_version = self._version.select_new_version(latest)

        else:
            # Se non viene trovata la release e non ci sono tag, viene saltato il check delle migrations e l'update delle card su youtrack
            logger.warning(
                f"No tags found, I'm about to push the tag {DEFAULT_VERSION}"
            )
            if not prompt_utils.ask_confirm(
                "Are you sure you want to continue?", default=False
            ):
                sys.exit()
            new_version = DEFAULT_VERSION
            message = f"First release with tag {new_version}"

        self._create_release(new_version, message)

        if "deploy" in self._flags and self._flags["deploy"]:
            self._deploy(new_version)

    def _deploy(self, version=""):
        if len(self._countries) > 1:
            countries = prompt_utils.ask_multiple_choices(
                "Which countries do you want to deploy to?",
                self._countries,
            )
        else:
            countries = self._countries

        versions = {}

        for country in countries:
            versions[country] = {}
            versions[country] = self._get_current_version(country)

        if self._tags_drifted(versions):
            logger.warning("NOTE: one or more countries runs older tags.")

        if not version:
            releases = self._extract_releases(versions)
            if len(releases) == 0:
                logger.error(f"No new release found for project {self._project}!")
                sys.exit(0)

            version = prompt_utils.ask_choices(
                "Which version do you want to deploy?",
                [{"name": f"{r.title}", "value": r.title} for r in releases],
            )

        if not prompt_utils.ask_confirm(
            f"You're about to deploy {self._project} release {version} in {countries}, do you confirm?",
            default=False,
        ):
            sys.exit(0)

        self._start_deploy(version, countries)
        self._manage_youtrack_card(version, countries)

    def _rollback(self):
        country = prompt_utils.ask_choices(
            "Which country do you want to rollback?",
            self._countries,
        )

        if not country:
            logger.error("You must select at least one country!")
            self._rollback()
            return

        current = self._get_current_version(country)
        releases = self._get_releases_before(current)
        if not releases:
            logger.error(f"No previous releases found for project {self._project}!")
            sys.exit(-1)
        version = prompt_utils.ask_choices(
            "Which version do you want to roll back to?",
            [{"name": f"{r.tag_name}", "value": r.tag_name} for r in releases],
        )

        if not prompt_utils.ask_confirm(
            f"You're about to roll back {self._project} to version {version} in {country}, do you confirm?",
            default=False,
        ):
            sys.exit(0)

        self._start_deploy(version, [country], rollback=True)

    def _get_current_version(self, country):
        try:
            # get latest 10 tags
            tags = self._github.get_tags(self._project)[0:9]
            # retrieve specific promotion for all tags
            builds = []
            for tag in tags:
                for b in self._drone.get_builds_from_tag(tag.name):
                    if (
                        b["event"] == "promote"
                        and b["status"] == "success"
                        and b["deploy_to"] == f"deploy-{country}-production"
                        and "params" in b
                        and "DRONE_TAG" in b["params"]
                    ):
                        builds.append(b)

            # get latest build using build number as key
            current_build = max(builds, key=lambda x: x["number"])

            if not current_build:
                logger.error(
                    f"Unable to determine current version for country {country}"
                )
                return None

            v = semver.VersionInfo.parse(current_build["params"]["DRONE_TAG"])
            logger.info(f"Current version for country {country}: {v}")

            return v
        except Exception:
            return None

    def _create_release(self, new_version, message):
        new_release = self._repo.create_git_release(
            new_version,
            new_version,
            self._youtrack.replace_card_names_with_md_links(message),
        )
        if new_release:
            logger.info(f"The release has been created! Link: {new_release.html_url}")

            build_number = self._drone.get_build_number_from_tag(new_version)
            if build_number:
                drone_url = self._drone.get_build_url(build_number)
                logger.info(f"You can follow the build status here: {drone_url}")

    def _start_deploy(self, version, countries, rollback=False):
        for country in countries:
            if rollback:
                promotion = self._drone.promote_production(
                    version,
                    f"deploy-{country}-production",
                    f"DRONE_TAG={version}&ROLLBACK=true",
                )
            else:
                promotion = self._drone.promote_production(
                    version,
                    f"deploy-{country}-production",
                    f"DRONE_TAG={version}",
                )

            if "number" not in promotion:
                logger.warning(f"Unable to promote drone build. Response: {promotion}")
                return

            logger.info("Drone build started successfully!")
            logger.info(
                f"You can follow the build status here: {self._drone.get_build_url(promotion['number'])}"
            )

            if rollback:
                self._post_rollback()

    def _get_releases_since(self, threshold):
        releases = self._repo.get_releases().get_page(0)

        return [rel for rel in releases if threshold.compare(rel.tag_name) == -1][0:4]

    def _get_releases_before(self, threshold):
        releases = self._repo.get_releases().get_page(0)

        return [rel for rel in releases if threshold.compare(rel.tag_name) == 1][0:4]

    def _manage_youtrack_card(self, version, countries):
        release_state = self._config.youtrack["release_state"]

        release_body = self._repo.get_release(version).body

        issue_ids = self._youtrack.get_ids_from_release_body(release_body)

        if len(issue_ids) > 0:
            update_youtrack_state = prompt_utils.ask_confirm(
                f"Do you want to move the associated cards to {release_state} state?",
                default=False,
            )

            for issue_id in issue_ids:
                try:
                    self._youtrack.comment(
                        issue_id,
                        f"Deploy in production of {self._project} in countries {countries} done with the release {version}",
                    )
                    if update_youtrack_state:
                        self._youtrack.update_state(issue_id, release_state)
                        logger.info(f"{issue_id} moved to {release_state}")
                except Exception:
                    logger.warning(
                        f"An error occurred while moving the card {issue_id} to {release_state}"
                    )
                repos_status = self._get_repos_status_from_issue(issue_id)
                if all(r["deployed"] for r in repos_status.values()):
                    try:
                        self._youtrack.update_deployed_field(issue_id)
                        logger.info("Custom field Deployed updated on YouTrack")
                    except Exception:
                        logger.warning(
                            "An error occurred while updating the custom field Deployed"
                        )

    def _get_repos_status_from_issue(self, issue_id):
        regex_pr = r"^PR .* -> https:\/\/github\.com\/primait\/(.*)\/pull\/([0-9]*)$"
        regex_deploy = r"^Deploy in production of (.*) in countries"
        comments = self._youtrack.get_comments(issue_id)
        repos_status = {}

        for c in comments:
            m = re.match(regex_pr, c["text"])
            if m:
                project = m.group(1)
                pr_number = int(m.group(2))
                repos_status[project] = {}
                repos_status[project]["pr"] = pr_number
                repos_status[project]["deployed"] = False
            m = re.match(regex_deploy, c["text"])
            if m:
                project = m.group(1)
                try:
                    repos_status[project]["deployed"] = True
                except Exception:
                    pass
        return repos_status

    def _post_rollback(self):
        logger.warning("--- !!!! ---")
        logger.warning("Remember to revert git commit(s) if needed!")

        if prompt_utils.ask_confirm(
            "Do you want to lock production?",
            default=True,
        ):
            self._captainhook.lock_project(self._project, "production")

    def _tags_drifted(self, versions):
        for country, version in versions.items():
            for c, v in versions.items():
                if country == c:
                    continue
                if version.compare(v) != 0:
                    return True
        return False

    def _extract_releases(self, versions):
        r = []
        for _, version in versions.items():
            releases = None
            if version:
                releases = self._get_releases_since(version)
            else:
                releases = self._get_releases_since(
                    semver.VersionInfo.parse("0.1.0")
                )  # default

            if releases:
                # check if releases already exist in the list, if not: append
                if not self._is_release_duplicated(r, releases):
                    r = r + releases

        return r

    def _is_release_duplicated(self, current, releases):
        for c in current:
            for rel in releases:
                if c.title == rel.title:
                    return True
        return False


def _check_migrations_deploy(commits):
    if not commits:
        logger.error("ERROR: no commit found")
        sys.exit(-1)
    elif len(commits) == 1:
        files_changed = git.files_changed_between_commits("--raw", f"{commits[0].sha}~")
    else:
        files_changed = git.files_changed_between_commits(
            f"{commits[-1].sha}~", commits[0].sha
        )
    if git.migrations_found(files_changed):
        logger.warning("WARNING: migrations detected in the code")
        if not prompt_utils.ask_confirm(
            "Are you sure you want to continue?", default=False
        ):
            sys.exit()


def _parse_available_countries(drone):
    pipelines = drone.parse_yaml()

    if pipelines is None:
        logger.error("The file .drone.yml was not found. Unable to continue.")
        sys.exit(1)

    countries = []
    REGEX = re.compile(r"deploy-([a-z]+)-.*")
    for pipeline in pipelines:
        if "name" in pipeline:
            c = REGEX.findall(pipeline["name"])
            if len(c) > 0 and c[0] is not None and c[0] not in countries:
                countries.append(c[0])

    return countries
