# Module dealing with directories

import sys
from datetime import datetime
from calendar import month_abbr
from pathlib import Path
from types import SimpleNamespace as SNS


def read_workfiles(config):
    """Make sure work files exist and read it"""
    def read_file(path, ftype):
        if not path.is_file():
            print(f'ERROR: {ftype} file {path} is missing!',
                  file=sys.stderr)
            sys.exit(1)
        else:
            with path.open('rt') as file:
                content = file.read()
        content = content.strip() if content else None
        return SNS(new=content)

    config.plan.content = read_file(config.plan.work.abs, 'Plan')
    config.project.content = read_file(config.project.work.abs, 'Project')


def create_index(config):
    """Create index path. Index is based on date hierarchy"""
    now = datetime.today()
    mnum = now.month
    mon = f'{mnum:02d}-{month_abbr[mnum]}'
    config.index = SNS()
    config.index.rel = Path(f'{now.year:04d}/{mon}/{now.day:}')
    config.index.abs = config.archive.abs / config.index.rel
    # Create index directory if needed
    if config.options.record:
        config.index.abs.mkdir(parents=True, exist_ok=True)


def read_current(config):
    """Read currently loaded plan/project if they exist"""
    def read_file(path):
        if path.is_file():
            with path.open('rt') as file:
                return file.read().strip()
        else:
            return None

    file = config.archive.abs / 'plan.current'
    config.plan.content.cur = read_file(file)
    config.plan.current = SNS(abs=file)
    config.plan.content.mod = \
        config.plan.content.new != config.plan.content.cur

    file = config.archive.abs / 'project.current'
    config.project.content.cur = read_file(file)
    config.project.current = SNS(abs=file)
    config.project.content.mod = \
        config.project.content.new != config.project.content.cur


def name_record(config):
    """Determine name for record files"""
    def filename(index, prefix):
        serials = [f.suffix[1:] for f in index.glob(f'{prefix}.??')]
        serials = [int(x) for x in serials if x.isnumeric()]
        serials.sort(reverse=True)
        serial = serials[0] + 1 if len(serials) != 0 else 1
        return f'{prefix}.{serial:02d}'

    plan = filename(config.index.abs, 'plan')
    config.plan.record = SNS()
    config.plan.record.rel = config.index.rel / plan
    config.plan.record.abs = config.index.abs / plan

    proj = filename(config.index.abs, 'project')
    config.project.record = SNS()
    config.project.record.rel = config.index.rel / proj
    config.project.record.abs = config.index.abs / proj
