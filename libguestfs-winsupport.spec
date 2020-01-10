%global         ntfs_version 2015.3.14

# debuginfo makes no sense for this package, so disable it
%global         debug_package %{nil}

Name:           libguestfs-winsupport
Version:        7.2
Release:        3%{?dist}
Summary:        Add support for Windows guests to virt-v2v and virt-p2v

URL:            http://www.ntfs-3g.org/
License:        GPLv2+
ExclusiveArch:  aarch64 x86_64

# This package shouldn't be installed without installing the base
# libguestfs package.
Requires:       libguestfs >= 1:1.28.1

# Source and patches for ntfs.  Try to keep this in step with Fedora.
Source0:        http://tuxera.com/opensource/ntfs-3g_ntfsprogs-%{ntfs_version}.tgz

Patch0:         ntfs-3g_ntfsprogs-2011.10.9-RC-ntfsck-unsupported-return-0.patch
Patch1:         CVE-2015-3202.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1301593#c8
Patch2:         0001-unistr.c-Enable-encoding-broken-UTF-16-into-broken-U.patch
Patch3:         0002-unistr.c-Unify-the-two-defines-NOREVBOM-and-ALLOW_BR.patch
# CVE-2019-9755 (https://bugzilla.redhat.com/show_bug.cgi?id=1698502)
Patch4:         0001-Fixed-reporting-an-error-when-failed-to-build-the-mo.patch

BuildRequires:  libtool, libattr-devel
BuildRequires:  libconfig-devel, libgcrypt-devel, gnutls-devel, libuuid-devel


%description
This optional package adds support for Windows guests (NTFS) to the
virt-v2v and virt-p2v programs.


%prep
%setup -q -n ntfs-3g_ntfsprogs-%{ntfs_version}
%patch0 -p1 -b .unsupported
%patch1 -p1 -b .cve
%patch2 -p1
%patch3 -p1
%patch4 -p1


%build
CFLAGS="$RPM_OPT_FLAGS -D_FILE_OFFSET_BITS=64"
%configure \
        --disable-static \
        --disable-ldconfig \
        --exec-prefix=/ \
        --enable-crypto \
        --enable-extras \
        --enable-quarantined
make %{?_smp_mflags} LIBTOOL=%{_bindir}/libtool


%install
# Build it into a destdir which is not the final buildroot.
mkdir destdir
make LIBTOOL=%{_bindir}/libtool DESTDIR=$(pwd)/destdir install
rm -rf destdir/%{_libdir}/*.la
rm -rf destdir/%{_libdir}/*.a

rm -rf destdir/%{_sbindir}/mount.ntfs-3g
cp -a destdir/%{_bindir}/ntfs-3g destdir/%{_sbindir}/mount.ntfs-3g

# Actually make some symlinks for simplicity...
# ... since we're obsoleting ntfsprogs-fuse
pushd destdir/%{_bindir}
ln -s ntfs-3g ntfsmount
popd
pushd destdir/%{_sbindir}
ln -s mount.ntfs-3g mount.ntfs-fuse
# And since there is no other package in Fedora that provides an ntfs 
# mount...
ln -s mount.ntfs-3g mount.ntfs
# Need this for fsck to find it
ln -s ../bin/ntfsck fsck.ntfs
popd
mv destdir/sbin/* destdir/%{_sbindir}
rmdir destdir/sbin

# We get this on our own, thanks.
rm -r destdir/%{_defaultdocdir}

# Remove development files.
rm -r destdir/%{_includedir}
rm -r destdir/%{_libdir}/pkgconfig

# Take the destdir and put it into a tarball for the libguestfs appliance.
mkdir -p %{buildroot}%{_libdir}/guestfs/supermin.d
pushd destdir
tar zcf %{buildroot}%{_libdir}/guestfs/supermin.d/zz-winsupport.tar.gz .
popd


%files
%doc AUTHORS ChangeLog COPYING CREDITS NEWS README

%{_libdir}/guestfs/supermin.d/zz-winsupport.tar.gz


%changelog
* Wed Apr 10 2017 Richard W.M. Jones <rjones@redhat.com> - 7.2-3
- Fix for CVE-2019-9755
  (heap-based buffer overflow leads to local root privilege escalation)
  resolves: rhbz#1698502

* Wed Feb 22 2017 Richard W.M. Jones <rjones@redhat.com> - 7.2-2
- Fix for handling guest filenames with invalid or incomplete
  multibyte or wide characters
  resolves: rhbz#1301593

* Tue Jul 07 2015 Richard W.M. Jones <rjones@redhat.com> - 7.2-1
- Rebase and rebuild for RHEL 7.2
  resolves: rhbz#1240278

* Tue Jun 30 2015 Richard W.M. Jones <rjones@redhat.com> - 7.1-6
- Bump version and rebuild.
  related: rhbz#1221583

* Fri May 15 2015 Richard W.M. Jones <rjones@redhat.com> - 7.1-5
- Enable aarch64 architecture.
  resolves: rhbz#1221583

* Thu Aug 28 2014 Richard W.M. Jones <rjones@redhat.com> - 7.1-4
- Enable debuginfo support and stripping.
  resolves: rhbz#1100319

* Thu Aug 28 2014 Richard W.M. Jones <rjones@redhat.com> - 7.1-3
- Add patches from Fedora package which add fstrim support.
  resolves: rhbz#1100319

* Mon Jul 21 2014 Richard W.M. Jones <rjones@redhat.com> - 7.1-2
- New package for RHEL 7.1
- Rebase to ntfs-3g 2014.2.15
  resolves: rhbz#1100319
- Change the package so it works with supermin5.
- Remove dependency on external FUSE.

* Wed Apr  3 2013 Richard W.M. Jones <rjones@redhat.com> - 7.0-2
- Resync against Rawhide package (ntfs-3g 2013.1.13).
- Drop HAL file since HAL is dead.
  resolves: rhbz#819939

* Thu Dec 20 2012 Richard W.M. Jones <rjones@redhat.com> - 7.0-1
- New package for RHEL 7
  resolves: rhbz#819939
- Resync against Rawhide package.

* Mon Mar 28 2011 Richard W.M. Jones <rjones@redhat.com> - 1.0-7
- Disable debuginfo package.
  resolves: RHBZ#691555.

* Tue Mar  8 2011 Richard W.M. Jones <rjones@redhat.com> - 1.0-6
- Require libguestfs 1.7.17 (newer version in RHEL 6.1).
- Require febootstrap-supermin-helper instead of febootstrap
  resolves: RHBZ#670299.

* Thu Jul  1 2010 Richard W.M. Jones <rjones@redhat.com> - 1.0-5
- Make sure intermediate lib* directories are created in hostfiles (RHBZ#603429)

* Thu Jun  3 2010 Richard W.M. Jones <rjones@redhat.com> - 1.0-4
- Requires fuse-libs (RHBZ#599300).

* Fri May 21 2010 Richard W.M. Jones <rjones@redhat.com> - 1.0-3
- ExclusiveArch x86_64.

* Tue May 18 2010 Richard W.M. Jones <rjones@redhat.com> - 1.0-2
- Package Windows support for libguestfs.
