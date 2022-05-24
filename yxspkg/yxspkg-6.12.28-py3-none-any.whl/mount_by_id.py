import subprocess
import click

@click.command()
@click.argument('args',nargs=-1)
def main(args):
    assert len(args)>=2
    cmd = f'blkid | grep {args[0]}'
    out = subprocess.getoutput(cmd).split('\n')
    print(out)
    if len(out)>1:
        raise Exception("Too mandy disks are pointed")
    if len(out) == 1:
        out = out[0].strip().split()[0][:-1]
        cmd = f'mount {out} {args[1]}'
        print(cmd)
        stat = subprocess.call(cmd,shell=True)
        if stat != 0:
            print('mount failed')
    else:
        print('no disk')

if __name__=='__main__':
    main()