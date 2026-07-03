%global         home %{_var}/lib/%{name}
%global         shortversion   %(echo %{version} | sed -e 's/^\([0-9]+\.[0-9]+\)\.[0-9]+/\1/g')
%global         opensslversion 1.0.0r
%global         srcname webserver

Name:           cherokee
Version:        1.2.104
Release:        9%{?dist}
Summary:        Flexible and Fast Webserver

License:        GPL-2.0-only
URL:            https://github.com/cherokee/webserver
ExclusiveArch:  x86_64 aarch64
Source0:        https://github.com/cherokee/%{srcname}/archive/refs/tags/v%{version}.tar.gz
Source1:        %{name}.init
Source2:        %{name}.logrotate
Source3:        %{name}.service

# Temporary replacement images for cherokee logos due to :
# https://fedorahosted.org/fesco/ticket/1230
#
# Unless noted, images from openclipart with license:
# https://openclipart.org/share
# http://creativecommons.org/publicdomain/zero/1.0/

# Replaces admin logos
# https://openclipart.org/detail/34951/architetto----utensili-chiave-e-cacci-by-anonymous
Source101: cherokee-admin-launcher.svg
Source102: cherokee-admin-launcher-256.png
Source103: cherokee-admin-launcher-128.png
Source104: cherokee-admin-launcher-96.png
Source105: cherokee-admin-launcher-48.png
Source106: cherokee-admin-launcher-512.png
Source107: cherokee-admin-launcher-32.png
Source108: cherokee-admin-launcher-16.png

# Replaces Cherokee logo (image only, no name)
# https://openclipart.org/detail/35389/tango-applications-internet-by-warszawianka
Source109: favicon.ico

# Modified Cherokee images to omit logo
# image + name.  Replacement keeps name, just removes logo
Source110: logo.png
Source111: cherokee-logo.png

# Modified Cherokee images to remove logo in documentation files
Source112: admin_handler_dirlist_ex.png
Source113: admin_handler_onlylisting_ex.png
Source114: admin_index.png
Source115: admin_launch.png

# Replaces screencast image
# https://openclipart.org/detail/172871/tango-styled-video-player-icon-by-flooredmusic-172871
Source116: screencast.png

# Drop privileges to cherokee:cherokee after startup
Patch0: 01-drop-privileges.patch
# Patch1: http://ausil.fedorapeople.org/aarch64/cherokee/cherokee-aarch64.patch
# Patch2: cherokee-1.2.103_CVE-2014-4668.patch
Patch3: cherokee-openssl-1.1.patch


BuildRequires:  pam-devel pcre-devel GeoIP-devel openldap-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openssl-devel
BuildRequires:  php-cli
BuildRequires:  gettext
BuildRequires:  autoconf libtool automake
BuildRequires:  python3
# For spawn-fcgi
Requires:        spawn-fcgi

Requires(pre):  shadow-utils
%{?systemd_requires}
BuildRequires: systemd-rpm-macros

Provides: webserver

%description
Cherokee is a very fast, flexible and easy to configure Web Server. It supports
the widespread technologies nowadays: FastCGI, SCGI, PHP, CGI, TLS and SSL
encrypted connections, Virtual hosts, Authentication, on the fly encoding,
Apache compatible log files, and much more.

%package devel
Summary:       Development files of cherokee
Requires:      %{name} = %{version}
%description devel
Cherokee is a very fast, flexible and easy to configure Web Server. It supports
the widespread technologies nowadays: FastCGI, SCGI, PHP, CGI, TLS and SSL
encrypted connections, Virtual hosts, Authentication, on the fly encoding,
Apache compatible log files, and much more.

This package holds the development files for cherokee.


%prep
%setup -n %{srcname}-%{version} -q
%patch0 -p1 -b .privs
# patch1 -p1 -b .aarch64
# patch2 -p1 -b .cve-2014-4668
%patch3 -p1 -b .openssl-1.1

# Replace upstream logos: https://fedorahosted.org/fesco/ticket/1230
for i in admin/icons/cherokee-admin-launcher-* \
         admin/static/images/favicon.ico \
         themes/default/logo.png \
         www/cherokee-logo.png \
         www/favicon.ico \
         doc/media/images/admin_handler_dirlist_ex.png \
         doc/media/images/admin_handler_onlylisting_ex.png \
         doc/media/images/admin_index.png \
         doc/media/images/admin_launch.png \
         doc/media/images/screencast.png    ; do
  rm $i
done
cp %{SOURCE101} admin/icons/
cp %{SOURCE102} admin/icons/
cp %{SOURCE103} admin/icons/
cp %{SOURCE104} admin/icons/
cp %{SOURCE105} admin/icons/
cp %{SOURCE106} admin/icons/
cp %{SOURCE107} admin/icons/
cp %{SOURCE108} admin/icons/

cp %{SOURCE109} www/favicon.ico
cp %{SOURCE109} admin/static/images/favicon.ico

cp %{SOURCE110} themes/default/
cp %{SOURCE111} www/

cp %{SOURCE112} doc/media/images/
cp %{SOURCE113} doc/media/images/
cp %{SOURCE114} doc/media/images/
cp %{SOURCE115} doc/media/images/
cp %{SOURCE116} doc/media/images/

%build
./autogen.sh
%configure --with-wwwroot=%{_var}/www/%{name} \
   --with-libssl \
   --disable-static
# Get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make_build


%install
%make_install

%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} -D -m 0644 pam.d_cherokee %{buildroot}%{_sysconfdir}/pam.d/%{name}
%{__install} -D -m 0644 %{SOURCE2}   %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d %{buildroot}%{_var}/{log,lib}/%{name}/
%{__install} -d %{buildroot}%{_sysconfdir}/pki/%{name}
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -D -m 0644 %{SOURCE3}   %{buildroot}%{_unitdir}/%{name}.service

%{__sed} -i -e 's#log/%{name}\.access#log/%{name}/access_log#' \
            -e 's#log/%{name}\.error#log/%{name}/error_log#' \
            %{buildroot}%{_sysconfdir}/%{name}/cherokee.conf
%{__sed} -i -e 's#log/%{name}\.access#log/%{name}/access_log#' \
            -e 's#log/%{name}\.error#log/%{name}/error_log#' \
            %{buildroot}%{_sysconfdir}/%{name}/cherokee.conf.perf_sample

touch %{buildroot}%{_var}/log/%{name}/access_log \
      %{buildroot}%{_var}/log/%{name}/error_log

find  %{buildroot}%{_libdir} -name *.la -exec rm -rf {} \;

chmod -x COPYING

# Get rid of spawn-fcgi bits, they conflict with the lighttpd-fastcgi package
# but are otherwise identical.
rm -rf %{buildroot}%{_bindir}/spawn-fcgi
rm -rf %{buildroot}%{_mandir}/man1/spawn-fcgi.*



%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
useradd -r -g %{name} -d %{home} -s /sbin/nologin \
   -c "%{name} web server" %{name}
exit 0

%post
%systemd_post cherokee.service

%preun
%systemd_preun cherokee.service

%postun
%systemd_postun_with_restart cherokee.service

%files
%{_unitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/pki/%{name}
%attr(0644,%{name},%{name}) %config(noreplace) %{_sysconfdir}/%{name}/cherokee.conf
%attr(0644,%{name},%{name}) %config(noreplace) %{_sysconfdir}/%{name}/cherokee.conf.perf_sample
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/cget
%{_bindir}/cherokee-panic
%{_bindir}/cherokee-tweak
%{_bindir}/cherokee-admin-launcher
%{_bindir}/cherokee-macos-askpass
%{_bindir}/CTK-run
# %%{_bindir}/spawn-fcgi
%{_sbindir}/cherokee
%{_sbindir}/cherokee-admin
%{_sbindir}/cherokee-worker
%{_libdir}/%{name}
%{_libdir}/lib%{name}-*.so.*
%{_datadir}/locale/*/LC_MESSAGES/cherokee.mo
%{_datadir}/%{name}
## Since we drop privileges to cherokee:cherokee, change permissions on these
# log files.
%attr(-,%{name},%{name}) %dir %{_var}/log/%{name}/
%attr(-,%{name},%{name}) %{_var}/log/%{name}/error_log
%attr(-,%{name},%{name}) %{_var}/log/%{name}/access_log
%attr(-,%{name},%{name}) %dir %{_var}/lib/%{name}/
%license COPYING
%doc AUTHORS NEWS
%doc %{_datadir}/doc/%{name}
%doc %{_mandir}/man1/cget.1*
%doc %{_mandir}/man1/cherokee.1*
%doc %{_mandir}/man1/cherokee-tweak.1*
%doc %{_mandir}/man1/cherokee-admin.1*
%doc %{_mandir}/man1/cherokee-worker.1*
%doc %{_mandir}/man1/cherokee-admin-launcher.1*
# doc {_mandir}/man1/spawn-fcgi.1*
%dir %{_var}/www/
%dir %{_var}/www/%{name}/
%dir %{_var}/www/%{name}/images/
%config(noreplace) %{_var}/www/%{name}/images/cherokee-logo.png
%config(noreplace) %{_var}/www/%{name}/images/default-bg.png
%config(noreplace) %{_var}/www/%{name}/images/powered_by_cherokee.png
%config(noreplace) %{_var}/www/%{name}/images/favicon.ico
%config(noreplace) %{_var}/www/%{name}/index.html

%files devel
%{_mandir}/man1/cherokee-config.1*
%{_bindir}/cherokee-config
%dir %{_includedir}/%{name}/
%{_includedir}/%{name}/*.h
%{_libdir}/pkgconfig/%{name}.pc
%{_datadir}/aclocal/%{name}.m4
%{_libdir}/lib%{name}-*.so


%changelog
* Thu Jul 03 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.2.104-9
- URL: http → https (GitHub); Source0: fix GitHub archive URL to refs/tags format (v1.2.104, verified 302→200)
- Drop %if rhel >= 8 conditional; always BuildRequires: systemd-rpm-macros (EL8+ only)
- SPDX: GPLv2 → GPL-2.0-only; ExclusiveArch; Requires(pre): shadow-utils; %%make_build/%%make_install; %%license COPYING

* Fri Apr 24 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.2.104-9
- Modernize spec for AlmaLinux 10; remove Group, %clean, replace python2 with python3
- Simplify conditional blocks, target systemd and mariadb-connector-c-devel unconditionally

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.104-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.104-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 1.2.104-7
- Rebuilt for switch to libxcrypt

* Mon Jan 15 2018 Pavel Lisý <pali@fedoraproject.org> - 1.2.104-6
- Resolves bz 1494076 - fixed for  Use mariadb-connector-c-devel instead of mysql-devel or mariadb-devel

* Wed Dec 13 2017 Pavel Lisý <pali@fedoraproject.org> - 1.2.104-5
- Resolves bz 1423254 - fixed for openssl 1.1

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.104-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.104-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.104-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jul 04 2016 Pavel Lisý <pali@fedoraproject.org> - 1.2.104-1
- new release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.103-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.103-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 15 2015 Pavel Lisý <pali@fedoraproject.org> - 1.2.103-6
- Resolves bz 1114461 - CVE-2014-4668 cherokee: authentication bypass when LDAP server allows unauthenticated binds
- Resolves bz 1094901 - cherokee: script and/or trigger should not directly enable systemd units
- Resolves bz  959170 - cherokee-worker and cherokee-admin want to use execstack (EL5)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.103-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.103-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Mar  5 2014 Toshio Kuratomi <toshio@fedoraproject.org> - 1.2.103-3
- Remove the upstream cherokee logo due to: https://fedorahosted.org/fesco/ticket/1230

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.103-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu May 16 2013 Pavel Lisý <pali@fedoraproject.org> - 1.2.103-1
- latest 1.2.x upstream release

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.101-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.101-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 21 2012 Pavel Lisý <pali@fedoraproject.org> - 1.2.101-3
- Resolves bz 786748 - systemd service script seems broken

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.101-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 19 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.101-1
- Latest 1.2.x upstream release

* Tue Oct 18 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.100-2
- Resolves bz 746532 - put some deps back: GeoIP-devel openldap-devel

* Mon Oct 10 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.100-1
- Latest 1.2.x upstream release

* Sun Sep 10 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.99-1
- Latest 1.2.x upstream release

* Wed Aug 10 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.98-1
- Latest 1.2.x upstream release

* Fri Feb 25 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.1-1
- Resolves bz 678243

* Tue Feb 22 2011 Pavel Lisý <pali@fedoraproject.org> - 1.0.20-1
- Latest 1.0.x upstream release (1.0.20)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Aug 29 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.8-1
- New upstream release (1.0.8)

* Mon Jun 28 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.4-1
- Relevant changes since 1.0.0

* Wed May 12 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.0-1
- First stable release

* Sun Sep 07 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.8.1-1
- first build
