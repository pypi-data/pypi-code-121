# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""High level utilities for Mercurial manifest handling.

The purpose is both to provide exactly what the HGitaly services need
and to abstract away from the actual manifest implementation: we might
at some point switch to some version of Tree Manifest if one appears that
fills our basic needs (namely to be a peer implementation detail, having no
effect on changeset IDs).

The module is meant to harbour several classes, according to the
underlying Mercurial core implementations. The dispatching is done by
the :func:`miner` fatory function.

It is legitimate to optimize each class according to the (stable) properties
of the core manifest object it works on.
"""
import attr


@attr.s
class ManifestMiner:
    """High level data extraction for basic Mercurial manifest.
    """
    changeset = attr.ib()

    def ls_dir(self, path):
        """List direct directory contents of path at given changeset.

        Anything from inside subdirectories of ``path`` is ignored.

        :param changeset: a :class:`changectx` instance
        :param bytes path: path in the repository of the directory to list.
           Can be empty for the root directory, but not ``b'/'``.
        :returns: a pair ``(subdirs, filepaths)`` of lists, where
          ``subdirs`` contains the sub directories and ``filepaths`` the direct
          file entries within ``path``.
          Both lists are lexicographically sorted.
          All elements are given by their full paths from the root.
        """
        subtrees = set()
        file_paths = []
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        for file_path in self.changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                continue
            split = file_path[prefix_len:].split(b'/', 1)
            if len(split) > 1:
                subtrees.add(prefix + split[0])
            else:
                file_paths.append(file_path)
        file_paths.sort()
        return sorted(subtrees), file_paths

    def iter_dir_recursive(self, path):
        """Iterate on recursive directory contents of path in order.

        :returns: yields pairs (path, is_directory)
        """
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        changeset = self.changeset

        in_dir = False
        seen_subdirs = set()

        for file_path in changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                if in_dir:
                    break
                continue  # pragma no cover (see coverage#198 and PEP626)

            in_dir = True

            split = file_path[prefix_len:].rsplit(b'/', 1)

            # accumulate ancestor dirs that need to be yielded
            acc = []
            while len(split) > 1:
                subdir = split[0]
                if subdir in seen_subdirs:
                    # if yielded yet, all its ancestors also are
                    break
                acc.append(subdir)
                seen_subdirs.add(subdir)
                split = subdir.rsplit(b'/', 1)

            for subdir in reversed(acc):
                yield (prefix + subdir, True)

            yield (file_path, False)

    def iter_dir_with_flat_paths(self, path):
        """Iterate on directory direct contents with "flat_path" information.

        :returns: yields triplets (full path, is_dir, flat_path) where
                  ``full_path`` is the path of a file or directory from
                  the repo root, ``is_dir`` indicates whether it is a
                  directory and ``flat_path`` is as explained below.

        About ``flat_path``, here is a comment from the current version of
        commit.proto::

          // Relative path of the first subdir that doesn't have only
          // one directory descendant


        Gitaly reference implementation (Golang)::

          func populateFlatPath(ctx context.Context, c catfile.Batch,
                                entries []*gitalypb.TreeEntry) error {
            for _, entry := range entries {
              entry.FlatPath = entry.Path

              if entry.Type != gitalypb.TreeEntry_TREE {
                continue
              }

              for i := 1; i < defaultFlatTreeRecursion; i++ {
                subEntries, err := treeEntries(
                    ctx, c, entry.CommitOid,
                    string(entry.FlatPath), "", false)

                if err != nil {
                  return err
                }

                if (len(subEntries) != 1 ||
                    subEntries[0].Type != gitalypb.TreeEntry_TREE) {
                  break
                }

                entry.FlatPath = subEntries[0].Path
              }
            }

            return nil
          }

        Implementation for the standard Mercurial manifest has of course
        to be very different, since it lists full paths to leaf
        (non-directory) files. In particular, there are no empty directories.

        The interpretation (would have to be formally proven) is that
        the "flat path" is the longest common directory ancestor of all file
        entries that are inside the considered directory entry.

        This implementation relies on manifest to emit paths in sorted manner.
        """
        prefix = path.rstrip(b'/') + b'/' if path else path
        prefix_len = len(prefix)
        changeset = self.changeset

        in_dir = False
        subdir, flat_path = None, ()

        for file_path in changeset.manifest().iterkeys():
            if not file_path.startswith(prefix):
                if in_dir:
                    break
                continue  # pragma no cover (see coverage#198 and PEP626)

            in_dir = True

            split = file_path[prefix_len:].split(b'/')
            if subdir is not None and split[0] != subdir:
                # we are leaving subdir, yield it
                dir_path = prefix + subdir
                yield (dir_path, True,
                       prefix + b'/'.join(flat_path) if flat_path else dir_path
                       )
                subdir, flat_path = None, ()

            if len(split) == 1:
                yield (file_path, False, file_path)
                subdir, flat_path = None, ()
            elif subdir is None:
                subdir, flat_path = split[0], split[:-1]
                continue

            flat_path = [
                segments[0] for segments in zip(flat_path, split)
                if segments[0] == segments[1]
            ]

        if subdir is not None:
            dir_path = prefix + subdir
            yield (dir_path, True,
                   prefix + b'/'.join(flat_path) if flat_path else dir_path
                   )


def miner(changeset):
    """Return an appropriate manifest extractor for the given changeset.

    This factory function abstracts over possible future manifest
    types, for which we might write different implementations
    """
    return ManifestMiner(changeset)
