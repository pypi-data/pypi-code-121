#!/usr/bin/python3
# -*- coding: utf-8 -*-

# templates.py file is part of sbo-templates.

# Copyright 2015-2022 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# SBo tool for managing templates.

# https://gitlab.com/dslackw/sbo-templates

# sbo-templates is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


bg = "\x1b[48;5;4m"
fg = "\x1b[38;5;7m"
cl = bg + fg

doinst = """
%s################################################################################
%s#             COPY A TEMPLATE AND PASTE IT INTO THE TEXT EDITOR                #
%s#                          PRESS \"q or Q\" TO EXIT                              #
%s################################################################################

config() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  # If there's no config file by that name, mv it over:
  if [ ! -r $OLD ]; then
    mv $NEW $OLD
  elif [ "$(cat $OLD | md5sum)" = "$(cat $NEW | md5sum)" ]; then
    # toss the redundant copy
    rm $NEW
  fi
  # Otherwise, we leave the .new copy for the admin to consider...
}

preserve_perms() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  if [ -e $OLD ]; then
    cp -a $OLD ${NEW}.incoming
    cat $NEW > ${NEW}.incoming
    mv ${NEW}.incoming $NEW
  fi
  config $NEW
}

schema_install() {
  SCHEMA="$1"
  GCONF_CONFIG_SOURCE="xml::etc/gconf/gconf.xml.defaults" \\
  chroot . gconftool-2 --makefile-install-rule \\
    /etc/gconf/schemas/$SCHEMA \\
    1>/dev/null
}

schema_install blah.schemas
preserve_perms etc/rc.d/rc.INIT.new
config etc/configfile.new

if [ -x /usr/bin/update-desktop-database ]; then
  /usr/bin/update-desktop-database -q usr/share/applications >/dev/null 2>&1
fi

if [ -x /usr/bin/update-mime-database ]; then
  /usr/bin/update-mime-database usr/share/mime >/dev/null 2>&1
fi

# If other icon themes are installed, then add to/modify this as needed
if [ -e usr/share/icons/hicolor/icon-theme.cache ]; then
  if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache usr/share/icons/hicolor >/dev/null 2>&1
  fi
fi

if [ -e usr/share/glib-2.0/schemas ]; then
  if [ -x /usr/bin/glib-compile-schemas ]; then
    /usr/bin/glib-compile-schemas usr/share/glib-2.0/schemas >/dev/null 2>&1
  fi
fi

# If needed -- be sure to sed @LIBDIR@ inside the build script
chroot . /usr/bin/gio-querymodules @LIBDIR@/gio/modules/ 1> /dev/null 2> /dev/null

if [ -x /usr/bin/install-info ]; then
  chroot . /usr/bin/install-info --info-dir=/usr/info /usr/info/blah.gz 2> /dev/null
fi

%s################################################################################
""" % (cl, cl, cl, cl, cl)


class SlackBuilds(object):

    def __init__(self, app_name, version, year, maint_name, live):
        self.app_name = app_name
        self.version = version
        self.year = year
        self.maint_name = maint_name
        self.live = live

    def autotools(self):

        autotools_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

if [ -z "$ARCH" ]; then
case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
    *) ARCH=$( uname -m ) ;;
esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}"  ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $PRGNAM-$VERSION
tar xvf $CWD/$PRGNAM-$VERSION.tar.gz
cd $PRGNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

CFLAGS="$SLKCFLAGS" \\
CXXFLAGS="$SLKCFLAGS" \\
./configure \\
  --prefix=/usr \\
  --libdir=/usr/lib${LIBDIRSUFFIX} \\
  --sysconfdir=/etc \\
  --localstatedir=/var \\
  --mandir=/usr/man \\
  --docdir=/usr/doc/$PRGNAM-$VERSION \\
  --build=$ARCH-slackware-linux

make
make install DESTDIR=$PKG

rm -f $PKG/{,usr/}lib${LIBDIRSUFFIX}/*.la

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

find $PKG/usr/man -type f -exec gzip -9 {} \\;
for i in $( find $PKG/usr/man -type l ) ; do ln -s $( readlink $i ).gz $i.gz ; rm $i ; done

rm -f $PKG/usr/info/dir
gzip -9 $PKG/usr/info/*.info*

find $PKG -name perllocal.pod \\
  -o -name ".packlist" \
  -o -name "*.bs" \\
  | xargs rm -f

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a <documentation> $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version)
        return autotools_template

    def cmake(self):

        cmake_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

if [ -z "$ARCH" ]; then
  case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
       *) ARCH=$( uname -m ) ;;
  esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $PRGNAM-$VERSION
tar xvf $CWD/$PRGNAM-$VERSION.tar.gz
cd $PRGNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

mkdir -p build
cd build
  cmake \\
    -DCMAKE_C_FLAGS:STRING="$SLKCFLAGS" \\
    -DCMAKE_CXX_FLAGS:STRING="$SLKCFLAGS" \\
    -DCMAKE_INSTALL_PREFIX=/usr \\
    -DLIB_SUFFIX=${LIBDIRSUFFIX} \\
    -DMAN_INSTALL_DIR=/usr/man \\
    -DCMAKE_BUILD_TYPE=Release ..
  make
  make install DESTDIR=$PKG
cd ..

rm -f $PKG/{,usr/}lib${LIBDIRSUFFIX}/*.la

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

find $PKG/usr/man -type f -exec gzip -9 {} \\;
for i in $( find $PKG/usr/man -type l ) ; do ln -s $( readlink $i ).gz $i.gz ; rm $i ; done

rm -f $PKG/usr/info/dir
gzip -9 $PKG/usr/info/*.info*

find $PKG -name perllocal.pod -o -name ".packlist" -o -name "*.bs" | xargs rm -f || true

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a  <documentation> $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version)
        return cmake_template

    def perl(self):

        perl_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

SRCNAM="$(printf $PRGNAM | cut -d- -f2-)"

if [ -z "$ARCH" ]; then
  case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
       *) ARCH=$( uname -m ) ;;
  esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $SRCNAM-$VERSION
tar xvf $CWD/$SRCNAM-$VERSION.tar.gz
cd $SRCNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

# Build method #1 (preferred)
perl Makefile.PL \\
  PREFIX=/usr \\
  INSTALLDIRS=vendor \\
  INSTALLVENDORMAN1DIR=/usr/man/man1 \\
  INSTALLVENDORMAN3DIR=/usr/man/man3
make
make test
make install DESTDIR=$PKG

# Build method #2
# requires perl-Module-Build or perl-Module-Build-Tiny
perl Build.PL \
  --installdirs vendor \
  --config installvendorman1dir=/usr/man/man1 \
  --config installvendorman3dir=/usr/man/man3
./Build
./Build test
./Build install \
  --destdir $PKG

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

find $PKG/usr/man -type f -exec gzip -9 {} \\;
for i in $( find $PKG/usr/man -type l ) ; do ln -s $( readlink $i ).gz $i.gz ; rm $i ; done

find $PKG -name perllocal.pod -o -name ".packlist" -o -name "*.bs" | xargs rm -f || true

find $PKG -depth -type d -empty -delete || true

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a  <documentation>  $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version)
        return perl_template

    def python(self):

        python_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

if [ -z "$ARCH" ]; then
  case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
       *) ARCH=$( uname -m ) ;;
  esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $PRGNAM-$VERSION
tar xvf $CWD/$PRGNAM-$VERSION.tar.gz
cd $PRGNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

# For python2
python2 setup.py install --root=$PKG

# For python3
python3 setup.py install --root=$PKG

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

find $PKG/usr/man -type f -exec gzip -9 {} \\;
for i in $( find $PKG/usr/man -type l ) ; do ln -s $( readlink $i ).gz $i.gz ; rm $i ; done

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a <documentation> $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version)
        return python_template

    def rubygem(self):

        rubygem_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

SRCNAM=appname

if [ -z "$ARCH" ]; then
  case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
       *) ARCH=$( uname -m ) ;;
  esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP

DESTDIR=$( ruby -r rbconfig -e '
include RbConfig
printf("%s/%s/gems/%s\n",
	CONFIG["libdir"],
	CONFIG["RUBY_INSTALL_NAME"],
	CONFIG["ruby_version"]
      )
')

gem specification $CWD/$SRCNAM-$VERSION.gem | \\
	ruby -r yaml -r rbconfig -e '
c = RbConfig::CONFIG
path = sprintf("%s/%s/gems/%s",
        c["libdir"],
        c["RUBY_INSTALL_NAME"],
        c["ruby_version"])
sys_gemspecs = Dir.glob(path + "/specifications/*").map {|g| gs = Gem::Specification.load(g);
gs.name }
obj = Gem::Specification.from_yaml($stdin)
obj.dependencies.each {|dep|
        if not(dep.type == :runtime)
                next
        end
        if not(sys_gemspecs.include?(dep.name))
                $stderr.write("WARNING:
                sleep 0.5
        end

}'

gem install \\
	--local \\
	--no-update-sources \\
	--ignore-dependencies \\
	--backtrace \\
	--install-dir $PKG/$DESTDIR \\
	--bindir $PKG/usr/bin \\
	$CWD/$SRCNAM-$VERSION.gem

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
tar -x -O --file=$CWD/$SRCNAM-$VERSION.gem data.tar.gz \\
  | tar -xz -C $PKG/usr/doc/$PRGNAM-$VERSION --file=- \\
  <documentation>
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version, "%s", "%s", "%s", "%s", "%s", "%s")
        return rubygem_template


    def haskell(self):

        haskell_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

SRCNAM="$( echo $PRGNAM | cut -d- -f2- )"

GHC_VERSION=$(ghc --numeric-version)

if [ -z "$ARCH" ]; then
  case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
       *) ARCH=$( uname -m ) ;;
  esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $SRCNAM-$VERSION
tar xvf $CWD/$SRCNAM-$VERSION.tar.gz
cd $SRCNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

CFLAGS="$SLKCFLAGS" \\
CXXFLAGS="$SLKCFLAGS" \\
runghc Setup configure \\
  --prefix=/usr \\
  --libdir=/usr/lib${LIBDIRSUFFIX} \\
  --libsubdir=ghc-${GHC_VERSION}/$SRCNAM-$VERSION \\
  --enable-shared \\
  --enable-library-profiling \\
  --docdir=/usr/doc/$PRGNAM-$VERSION

runghc Setup build
runghc Setup haddock
runghc Setup copy --destdir=$PKG
runghc Setup register --gen-pkg-config

PKGCONFD=/usr/lib${LIBDIRSUFFIX}/ghc-${GHC_VERSION}/package.conf.d
PKGID=$( grep -E "^id: " $SRCNAM-$VERSION.conf | cut -d" " -f2 )
mkdir -p $PKG/$PKGCONFD
mv $SRCNAM-$VERSION.conf $PKG/$PKGCONFD/$PKGID.conf

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a <documentation> $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
           self.version)
        return haskell_template

    def meson(self):

        autotools_template = """#!/bin/bash

# Slackware build script for %s

# Copyright %s %s %s
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cd $(dirname $0) ; CWD=$(pwd)

PRGNAM=%s
VERSION=${VERSION:-%s}
BUILD=${BUILD:-1}
TAG=${TAG:-_SBo}
PKGTYPE=${PKGTYPE:-tgz}

if [ -z "$ARCH" ]; then
case "$( uname -m )" in
    i?86) ARCH=i586 ;;
    arm*) ARCH=arm ;;
    *) ARCH=$( uname -m ) ;;
esac
fi

# If the variable PRINT_PACKAGE_NAME is set, then this script will report what
# the name of the created package would be, and then exit. This information
# could be useful to other scripts.
if [ ! -z "${PRINT_PACKAGE_NAME}" ]; then
  echo "$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE"
  exit 0
fi

CWD=$(pwd)
TMP=${TMP:-/tmp/SBo}
PKG=$TMP/package-$PRGNAM
OUTPUT=${OUTPUT:-/tmp}

if [ "$ARCH" = "i586" ]; then
  SLKCFLAGS="-O2 -march=i586 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "i686" ]; then
  SLKCFLAGS="-O2 -march=i686 -mtune=i686"
  LIBDIRSUFFIX=""
elif [ "$ARCH" = "x86_64" ]; then
  SLKCFLAGS="-O2 -fPIC"
  LIBDIRSUFFIX="64"
else
  SLKCFLAGS="-O2"
  LIBDIRSUFFIX=""
fi

set -e

rm -rf $PKG
mkdir -p $TMP $PKG $OUTPUT
cd $TMP
rm -rf $PRGNAM-$VERSION
tar xvf $CWD/$PRGNAM-$VERSION.tar.gz
cd $PRGNAM-$VERSION
chown -R root:root .
find -L . \\
 \( -perm 777 -o -perm 775 -o -perm 750 -o -perm 711 -o -perm 555 \\
  -o -perm 511 \) -exec chmod 755 {} \; -o \\
 \( -perm 666 -o -perm 664 -o -perm 640 -o -perm 600 -o -perm 444 \\
  -o -perm 440 -o -perm 400 \) -exec chmod 644 {} \\;

mkdir build
cd build
  CFLAGS="$SLKCFLAGS" \
  CXXFLAGS="$SLKCFLAGS" \
  meson .. \
    --buildtype=release \
    --infodir=/usr/info \
    --libdir=/usr/lib${LIBDIRSUFFIX} \
    --localstatedir=/var \
    --mandir=/usr/man \
    --prefix=/usr \
    --sysconfdir=/etc \
    -Dstrip=true
  "${NINJA:=ninja}"
  DESTDIR=$PKG $NINJA install
cd ..

rm -f $PKG/{,usr/}lib${LIBDIRSUFFIX}/*.lacd ..

find $PKG -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF \\
  | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

find $PKG/usr/man -type f -exec gzip -9 {} \\;
for i in $( find $PKG/usr/man -type l ) ; do ln -s $( readlink $i ).gz $i.gz ; rm $i ; done

rm -f $PKG/usr/info/dir
gzip -9 $PKG/usr/info/*.info*

find $PKG -name perllocal.pod \\
  -o -name ".packlist" \
  -o -name "*.bs" \\
  | xargs rm -f

mkdir -p $PKG/usr/doc/$PRGNAM-$VERSION
cp -a <documentation> $PKG/usr/doc/$PRGNAM-$VERSION
cat $CWD/$PRGNAM.SlackBuild > $PKG/usr/doc/$PRGNAM-$VERSION/$PRGNAM.SlackBuild

mkdir -p $PKG/install
cat $CWD/slack-desc > $PKG/install/slack-desc
cat $CWD/doinst.sh > $PKG/install/doinst.sh

cd $PKG
/sbin/makepkg -l y -c n $OUTPUT/$PRGNAM-$VERSION-$ARCH-$BUILD$TAG.$PKGTYPE
""" % (self.app_name, self.year, self.maint_name, self.live, self.app_name,
            self.version)
        return autotools_template
