'''Creates or overwrites a version.txt file in the current working directory
containing the "full version" of the current AlazarTech project. The full
version is a string that respects Semantic Versioning, with the following
scheme:

- for official releases, the version is "X.Y.Z" with X the major, Y the minor
  and Z the patch version number
- for "internal" releases, the version is "X.Y.Z-<pre>" with "X.Y.Z" as before,
  and <pre> a prerelease identifier, for example "1.2.3-beta2".
- otherwise, the version should be "X.Y.Z+<build>" with "X.Y.Z" as before and
  <build> the build identifier, e.g. "1.2.3+34082b74".

Official and internal releases are identified by tags in the ${CI_COMMIT_TAG}
environment variable. Note that these tags have a "v" prefix. Otherwise, the
root of the version number is found by parsing the CHANGELOG.md change log
file, and the SHA of the current commit is found in the ${CI_COMMIT_SHORT_SHA}
environment variable

'''


from subprocess import check_output, CalledProcessError
import os
import re

try:
    from . import changelogparser
except:
    import changelogparser


def git_get_info():
    '''Returns a tuple of three elements:

     - the name of the current commit's closest tag
     - the distance in commits to that tag (or 0 if we are on the tag)
     - the short SHA of the current commit'''
    out = check_output(['git', 'describe', '--tags', '--long']).decode('ascii')
    m = re.search('(.*)-([0-9]+)-g(.*)', out)
    if not m:
        raise ValueError("Could not parse git command's output: {}".format(out))
    return (m.group(1), int(m.group(2)), m.group(3))

def get_version_from_tag(tag):
    return tag.lstrip('v')

def get_changelog_version(filename):
    with open(filename, 'r') as clfile:
        changelog = changelogparser.ChangeLogRuleVisitor().parse(clfile.read())
        return changelogparser.version_string(
            changelogparser.changelog_version(changelog))

def get_version_using_git_describe():
    tag, tag_distance, sha = git_get_info()
    if tag_distance == 0:
        return get_version_from_tag(tag)
    return "{}+{}".format(get_changelog_version("CHANGELOG.md"), sha)

def get_version_using_git_rev_parse():
    sha = check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    return "{}+{}".format(get_changelog_version("CHANGELOG.md"), sha)


def get_version():
    if "CI_COMMIT_TAG" in os.environ:
        return get_version_from_tag(os.environ["CI_COMMIT_TAG"])

    if "CI_COMMIT_SHORT_SHA" not in os.environ:
        try:
            return get_version_using_git_describe()
        except CalledProcessError:
            return get_version_using_git_rev_parse()


    return "{}+{}".format(get_changelog_version("CHANGELOG.md"),
                          os.environ["CI_COMMIT_SHORT_SHA"])

def main():
    with open("version.txt", "w") as vfile:
        vfile.write(get_version() + '\n')

if __name__ == "__main__":
    main()
