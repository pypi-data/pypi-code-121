import os
from .site import establish_site, build_site

def main():
    # create a dummy site if none exists
    if not os.path.isdir("pages"):
        establish_site()
    # this should build your site
    build_site()

if __name__ == "__main__":
    main()

