# Management of archival and symlinking

import sys


def archive_link(config, filetype):
    """Archive plan and project into index and symlink them"""
    if not config.options.record:
        return

    fconf = config.__dict__[filetype]

    # Push without check if: User skipped check OR record not done
    if fconf.content.mod:
        with fconf.record.abs.open('wt') as outfile:
            outfile.write(fconf.content.new)
        fconf.current.abs.unlink(missing_ok=True)
        fconf.current.abs.symlink_to(fconf.record.rel)
        print(f'INFO: {filetype} file {fconf.record.rel} saved.',
            file=sys.stderr)
    else:
        print(f'WARNING: {filetype} file hasn\'t changed. '
                'Skipping archival step!', file=sys.stderr)
