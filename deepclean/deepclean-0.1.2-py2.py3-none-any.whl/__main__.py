"""Clean old versions of Docker images."""

import argparse
import re

import docker  # pylint: disable=import-error,useless-suppression

from . import __version__


def image_date(image):
    """Return the creation date of the image."""
    return image.history()[0]["Created"]


def include(images, includes, verbose):
    """Return only the images that match the regexes in the includes list."""
    regexes = [re.compile(r) for r in includes]
    included_images = {}
    for Id, image in images.items():  # noqa: N806 pylint: disable=invalid-name
        for tag in image.tags:
            for r in regexes:  # pylint: disable=invalid-name
                if r.match(tag):
                    if verbose:
                        print(f"Including image {Id}.")
                    included_images[Id] = image
                    break
    return included_images


def exclude(images, excludes, verbose):
    """Return the images that don't match the regexes in the excludes list."""
    remaining_images = images.copy()
    regexes = [re.compile(r) for r in excludes]
    # pylint: disable=invalid-name
    for (Id, image) in images.items():  # noqa: N806
        for tag in image.tags:
            for r in regexes:
                if r.match(tag):
                    if verbose:
                        print(f"Excluding image {Id}.")
                    remaining_images.pop(Id)
                    break
    return remaining_images


def not_in_use(client, images, verbose):
    """Return the images that aren't in use by containers right now."""
    in_use_images = [c.image.id for c in client.containers.list(all=True)]
    not_in_use_images = images.copy()
    # pylint: disable=invalid-name
    for Id in in_use_images:  # noqa: N806
        if verbose:
            print(f"Image {Id} is in use, ignoring.")
        if Id in not_in_use_images:
            not_in_use_images.pop(Id)
    return not_in_use_images


def normalize_names(images_by_name):
    """Normalize the different Docker hub registry names."""
    copy_of_images = {k: v[:] for k, v in images_by_name.items()}
    for name in images_by_name.keys():
        if name.startswith("registry.hub.docker.com"):
            new_name = name.replace("registry.hub.docker.com", "docker.io", 1)
            if new_name in copy_of_images:
                copy_of_images[new_name] = list(
                    set(copy_of_images[name] + copy_of_images[new_name])
                )
                copy_of_images[new_name].sort(key=image_date, reverse=True)
            else:
                copy_of_images[new_name] = copy_of_images[name]
            copy_of_images.pop(name)
    return copy_of_images


def deepclean(  # noqa: MC0001
    includes=None, excludes=None, verbose=False, dry_run=False
):
    """Clean old versions of Docker images."""
    client = docker.from_env()
    images = {i.id: i for i in client.images.list()}

    images = not_in_use(client, images, verbose)

    if includes:
        images = include(images, includes, verbose)

    if excludes:
        images = exclude(images, excludes, verbose)

    # First we build a dictionary with the image name as key and the value is
    # an empty list that later will contain the images that have that name.
    images_by_name = {
        docker.utils.parse_repository_tag(name)[0]: []
        for image in images.values()
        for name in image.tags
    }

    # Now we're populating the list of images for each image name.
    # We keep the list of images sorted from most recent to least.
    for image in images.values():
        for tag in image.tags:
            name = docker.utils.parse_repository_tag(tag)[0]
            images_by_name[name].append(image)
            images_by_name[name].sort(key=image_date, reverse=True)

    images_by_name = normalize_names(images_by_name)

    # noqa: LPY101
    for name in images_by_name.keys():
        kept = images_by_name[name][0].id
        if kept in images:
            if verbose:
                print(f"Keeping {kept}, the latest image for {name}.")
                images.pop(kept)

    # Now we've removed the images that are in use, kept the included ones,
    # removed the excluded ones and the latest image for each name. We're left
    # with images that are meant for deletion.

    # pylint: disable=invalid-name
    for Id in images.keys():  # noqa: N806
        if dry_run:
            print(f"Would have removed image {Id}.")
        else:
            print(f"Removing image {Id}.")
            try:
                client.images.remove(Id)
            except docker.errors.APIError as exc:
                if exc.status_code == 409:
                    print(f"Image {Id} has descendant images.")
                else:
                    raise exc


def main():
    # noqa: D401
    """The main entrypoint."""
    epilog = (
        "Regular Docker environment variables (like DOCKER_HOST) can be used."
        "-i and -e can be used multiple times."
    )
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=epilog,
    )
    parser.add_argument(
        "-i",
        "--include",
        help="Regular expression of images to exclusively prune.",
        action="append",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        help="Regular expression of images to ignore.",
        action="append",
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output", action="store_true"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"deepclean version {__version__}",
    )
    parser.add_argument(
        "-d", "--dry-run", help="Dry-run, don't delete", action="store_true"
    )
    args = parser.parse_args()
    try:
        deepclean(
            includes=args.include,
            excludes=args.exclude,
            verbose=args.verbose,
            dry_run=args.dry_run,
        )
    except Exception as ex:  # noqa: PIE786 pylint: disable=broad-except
        parser.error(str(ex))


if __name__ == "__main__":
    main()
