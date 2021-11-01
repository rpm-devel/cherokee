%global         home %{_var}/lib/%{name}
%global         shortversion   %(echo %{version} | sed -e 's/^\([0-9]+\.[0-9]+\)\.[0-9]+/\1/g')
%global         opensslversion 1.0.0r
%global         srcname webserver

Name:           cherokee
Version:        1.2.104
Release:        9%{?dist}
Summary:        Flexible and Fast Webserver

Group:          Applications/Internet
License:        GPLv2
URL:            http://www.cherokee-project.com/
Source0:        http://github.com/%{name}/%{srcname}/archive/%{srcname}-%{version}.tar.gz
Source1:        %{name}.init
Source2:        %{name}.logrotate
Source3:        %{name}.service

%if "%{rhel}" == "5"
Source100:      http://www.openssl.org/source/openssl-%{opensslversion}.tar.gz
%endif

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
%if "%{fedora}" >= "26"
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openssl-devel
%else
BuildRequires:  mysql-devel
BuildRequires:  openssl-devel
%endif
BuildRequires:  php-cli
BuildRequires:  gettext
BuildRequires:  autoconf libtool automake
%if "%{fedora}" >= "23"
BuildRequires:  python2
%endif
# For spawn-fcgi
Requires:        spawn-fcgi

%if ( 0%{?fedora} )
Requires(post): systemd systemd-units
Requires(preun): systemd systemd-units
Requires(postun): systemd systemd-units
BuildRequires: systemd
%else
Requires(post):  chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

Provides: webserver

%description
Cherokee is a very fast, flexible and easy to configure Web Server. It supports
the widespread technologies nowadays: FastCGI, SCGI, PHP, CGI, TLS and SSL
encrypted connections, Virtual hosts, Authentication, on the fly encoding,
Apache compatible log files, and much more.

%package devel
Group:         Development/Libraries
Summary:       Development files of cherokee
Requires:      %{name} = %{version}
%description devel
Cherokee is a very fast, flexible and easy to configure Web Server. It supports
the widespread technologies nowadays: FastCGI, SCGI, PHP, CGI, TLS and SSL
encrypted connections, Virtual hosts, Authentication, on the fly encoding,
Apache compatible log files, and much more.

This package holds the development files for cherokee.


%prep
%if "%{rhel}" == "5"
%setup -n %{srcname}-%{version} -q -a 100
%else
%setup -n %{srcname}-%{version} -q
%endif
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
%if "%{rhel}" == "5"
pushd openssl-%{opensslversion}
./config --prefix=/usr --openssldir=%{_sysconfdir}/pki/tls shared no-asm
make depend
make all
mkdir ./lib
for lib in *.a ; do
  ln -s ../$lib ./lib
done
popd
%endif

./autogen.sh
%configure --with-wwwroot=%{_var}/www/%{name} \
%if "%{rhel}" == "5"
   --with-libssl=$(pwd)/openssl-%{opensslversion} --enable-static-module=libssl \
%else
   --with-libssl \
%endif
   --disable-static
# Get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} -D -m 0644 pam.d_cherokee %{buildroot}%{_sysconfdir}/pam.d/%{name}
%{__install} -D -m 0644 %{SOURCE2}   %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -d %{buildroot}%{_var}/{log,lib}/%{name}/
%{__install} -d %{buildroot}%{_sysconfdir}/pki/%{name}
%if ( 0%{?fedora} )
%{__install} -d %{buildroot}%{_unitdir}
%{__install} -D -m 0644 %{SOURCE3}   %{buildroot}%{_unitdir}/%{name}.service
%else
%{__install} -D -m 0755 %{SOURCE1}   %{buildroot}%{_sysconfdir}/init.d/%{name}
%endif

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
%if ( 0%{?fedora} )
   %systemd_post cherokee.service
%else
   /sbin/ldconfig
   /sbin/chkconfig --add %{name}
%endif
%if "%{rhel}" == "5"
   /usr/bin/execstack --clear-execstack %{_libdir}/lib%{name}-server.so.*
%endif

%preun
%if ( 0%{?fedora} )
   %systemd_preun cherokee.service
%else
   if [ $1 = 0 ] ; then
      /sbin/service %{name} stop >/dev/null 2>&1
      /sbin/chkconfig --del %{name}
   fi
%endif

%postun
%if ( 0%{?fedora} )
   %systemd_postun_with_restart cherokee.service
%else
   /sbin/ldconfig
%endif

%files
%if ( 0%{?fedora} )
%{_unitdir}/%{name}.service
%else
%{_sysconfdir}/init.d/%{name}
%endif
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
%doc AUTHORS COPYING NEWS
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
- Resolves bz 961057 - RFE: Cherokee 1.2.103 is available
- Resolves bz 961056 - RFE: Cherokee 1.2.103 is available
- Resolves bz 954199 - cherokee 1.2.103 is available
- Resolves bz 958337 - Update request for Cherokee
- Resolves bz 858542 - Cherokee should not be built with trace/backtrace support for performance 
#- Resolves bz 925220 - cherokee: Does not support aarch64 in f19 and rawhide

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
- .spec corrections for optional build for systemd
- Resolves bz 710474
- Resolves bz 713307
- Resolves bz 680691

* Wed Sep 14 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.99-2
- .spec corrections for EL4 build

* Sat Sep 10 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.99-1
- Latest 1.2.x upstream release
- Resolves bz 713306
- Resolves bz 710473
- Resolves bz 728741
- Resolves bz 720515
- Resolves bz 701196
- Resolves bz 712555

* Wed Aug 10 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.98-1
- Latest 1.2.x upstream release

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 1.2.1-2
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Fri Feb 25 2011 Pavel Lisý <pali@fedoraproject.org> - 1.2.1-1
- Resolves bz 678243
- Resolves bz 680051
- Resolves bz 678838 (EPEL)
- Resolves bz 622514 (EPEL)

* Fri Feb 25 2011 Pavel Lisý <pali@fedoraproject.org> - 1.0.20-4
- Resolves bz 570317

* Tue Feb 22 2011 Pavel Lisý <pali@fedoraproject.org> - 1.0.20-3
- reenabled ppc build for el4/el5

* Tue Feb 22 2011 Pavel Lisý <pali@fedoraproject.org> - 1.0.20-2
- .spec corrections for el4

* Tue Feb 22 2011 Pavel Lisý <pali@fedoraproject.org> - 1.0.20-1
- Latest 1.0.x upstream release (1.0.20)
- Resolves bz 657085
- Resolves bz 678237

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep  1 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.8-2
- Merge changes to cherokee.init from Pavel Lisý (hide cherokee's
  stdout messages)

* Sun Aug 29 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.8-1
- New upstream release (1.0.8)
- Init script overhaul
- Relevant changes since 1.0.6:
- NEW: Enhanced 'Header' rule match
- NEW: Improved extensions rule
- FIX: SSL/TLS works with Firefox again
- FIX: Better SSL/TLS connection close
- FIX: Range requests work better now
- FIX: Hot-linking wizard w/o Referer
- FIX: Hot-linking wizard usability
- FIX: Minor CSS fix in the default dirlist theme
- FIX: POST management issue
- FIX: PHP wizard, better configuration
- FIX: admin, unresponsive button
- DOC: Misc improvements
- i18n: French translation updated

* Fri Aug 6 2010 Lorenzo Villani <lvillani@enterprise.binaryhelix.net> 1.0.6-1
- Relevant changes since 1.0.4
- NEW: Much better UTF-8 encoding
- NEW: Templates support slicing now (as in Python str)
- NEW: 'TLS/SSL' matching rule
- NEW: Reverse HTTP proxy can overwrite "Expire:" entries
- NEW: Redirection handler support the ${host} macro now
- FIX: POST support in the HTTP reverse proxy
- FIX: Some SSL/TLS were fixed. [unfinished]
- FIX: X-Forwarded-For parsing bug fixed
- FIX: Better php-fpm support in the PHP wizard
- FIX: Bundled PySCGI bumped to 1.14
- FIX: Random 100% CPU usage
- FIX: POST management regression in the proxy
- FIX: Connection RST/WAIT_FIN related fixes
- FIX: Dirlist bugfix: symbolic links handling
- FIX: POST status report bug-fixes
- DOC: Documentation updates
- i18n: Spanish translation updated
- i18n: Dutch translation updated
- i18n: Polish translation updated
- i18n: German translation updated

* Mon Jun 28 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.4-1
- Relevant changes since 1.0.0
- OLD: Dropped support for RFC 2817.
- NEW: MediaWiki wizard
- NEW: PHP wizard for Virtual Servers
- FIX: Fixes a regression in the SSL/TLS support
- FIX: Shorter SSL session names
- FIX: Content-Range management issue
- FIX: Content-Type (max-age) management issue fixed
- FIX: Better 'IPv6 is missing' report
- FIX: RRD for VServers with spaces in the name
- FIX: admin, Fixes uWSGI wizard
- FIX: admin, Adds extra path to find php-fpm
- FIX: admin, Fixes the Static content wizard
- FIX: admin, Fixes issue with the RoR wizard
- FIX: admin, Validation of executable files
- FIX: HTTP error codes bug
- FIX: Auth headers are added from error pages if needed
- FIX: Better fd limit management
- FIX: Duplicated Cache-Control header
- FIX: Safer TLS/SSL close.
- FIX: Trac wizard checking bug.
- FIX: NCSA/Combined log invalid length.
- FIX: Better inter-wizard dependencies management
- FIX: PID file management fix
- FIX: PHP wizard create functional vservers now
- FIX: Add WebM MIME types
- FIX: Admin, rule table style improved
- FIX: Reordering for vservers and rules
- FIX: Joomla wizard
- FIX: Validation for incoming ports/interfaces
- FIX: Regression: Document root can be defined per-rule
- FIX: 'Broken installation detected' error improved
- FIX: Handler common parameters work again
- FIX: PHP-fpm detection
- FIX: Better list validations
- FIX: File exists issue
- DOC: Various updates
- I18n: Spanish translation updated
- I18n: Brazilian Portuguese translation updated
- I18n: Polish updated
- I18n: Dutch updated
- I18n: New translation to Catalan

* Wed May 12 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 1.0.0-1
- First stable release

* Wed May  5 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.49-1
- Changes since 0.99.44:
- New cherokee-admin (rewritten from scratch)
- FIX: Reverse proxy bug
- FIX: Handler init bug: crashed on ARM
- FIX: Adds missing HTTP methods
- FIX: PTHREAD_RWLOCK_INITIALIZER usage
- FIX: uWSGI paths bug
- FIX: WordPress wizard bug
- FIX: Safer (synchronous) cherokee-admin start
- FIX: Keep-alive related bug
- FIX: Error log management has been fixed
- FIX: Re-integrates the phpMyAdmin wizard
- FIX: Cherokee-admin default timeout increased
- FIX: Wordpress wizard
- FIX: Flags in the GeoIP plug-in
- FIX: LOCK method detection
- FIX: upgrade_config.py was broken
- I18n: Chinese translation updated
- I18n: New translation to Polish
- I18n: Spanish translation updated
- I18n: Dutch translation updated
- DOC: Improves Server Info handler documentation
- DOC: Many documentation updates
- DOC: New screenshots
- DOC: PHP recipe improved

* Fri Apr 23 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.44-1
- FIX: Large POST support bug fixed
- FIX: UTF-8 requests bug fixed
- FIX: 7z MIME-type
- FIX: Added missing HTTP response codes
- FIX: Added missing HTTP methods
- FIX: Many documentation typos fixed
- I18N: Dutch translation updated

* Thu Mar 18 2010 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.43-1
- 0.99.43
- FIX: Performance related regression (Keep-alive w/o cache)
- FIX: Better lingering close
- FIX: PAM authentication module fixes: threading issue
- FIX: Cherokee-admin supports IPv6 by default
- FIX: Parsing IPv6 addresses in "allow from" restrictions
- FIX: Rule OR is slightly faster now
- FIX: Fixes a few accessibility issues in cherokee-admin
- FIX: Symfony wizard, fixed to use the new paths
- suppressed confusing output from init script

* Tue Feb 2 2010 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.42-1
- 0.99.42
- Compilation and last-minute fixes
- NEW: POST managing subsystem has been rewritten from scratch
- NEW: New POST (uploads) status reporting mechanism
- NEW: Rules can be configured to forbid the use of certain encoders
- NEW: Custom logger: Adds ${response_size} support
- FIX: File descriptor leak fixed in the HTTP reverse proxy
- FIX: Error pages with UTF8 encoded errors work now
- FIX: Safer file descriptor closing
- FIX: getpwuid_r() detection
- FIX: Original query strings (and requests) are logged now
- FIX: Misc cherokee-admin fixes
- FIX: uWSCGI: Endianess fixes and protocol modifiers
- FIX: Chinese translation updated
- FIX: Cherokee-admin: Display custom error if the doc. is missing
- FIX: Early logging support is not supported any longer
- FIX: QA and Cherokee-Admin: Bumps PySCGI to version 1.11
- FIX: The 'fastcgi' handler has been deprecated in favor of 'fcgi'
- FIX: PATH_INFO generation on merging non-final rules (corner case)
- DOC: Installation updated

* Tue Dec 29 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.39-1
- 0.99.39

* Mon Dec 28 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.38-1
- 0.99.38

* Wed Dec 23 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.37-1
- 0.99.37

* Thu Dec  3 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.31-1
- New upstream release: 0.99.31

* Tue Dec  1 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.30-1
- 0.99.30

* Sun Nov 22 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.29-1
- 0.99.29

* Sat Nov 07 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.27-1
- 0.99.27

* Sat Sep  5 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 0.99.24-1
- 0.99.24

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 0.99.20-3
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.99.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat Jul 11 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.20-1
- updated to 0.99.20

* Sun Jun 14 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.17-2
- .spec changes in files section

* Sun Jun 14 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.17-1
- updated to 0.99.17

* Tue Apr 21 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.11-2
- added BuildRequires: gettext

* Mon Apr 20 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.11-1
- updated to 0.99.11

* Sat Mar 07 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.99.0-1
- updated to 0.99.0

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.98.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Pavel Lisy <pavel.lisy@gmail.com> - 0.98.1-1
- updated to 0.98.1

* Sat Jan 24 2009 Caolán McNamara <caolanm@redhat.com> - 0.11.6-2
- rebuild for dependencies

* Tue Dec 30 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.11.6-1
- Resolves bz 478488, updated to 0.11.6

* Tue Dec 30 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.11.2-4
- Resolves bz 472749 and 472747, changed Requires: spawn-fcgi

* Tue Dec 16 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.11.2-3
- ppc arch excluded only for el4

* Tue Dec 16 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.11.2-2
- ppc arch excluded

* Tue Dec 16 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.11.2-1
- updated to 0.11.2

* Tue Dec 16 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.10.0-3
- Unowned directories, Resolves bz 474634

* Thu Nov  6 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.10.0-2
- do not package spawn-fcgi files (lighttpd-fastcgi provides them)
  Resolves bz 469947
- get rid of rpath in compiled files

* Fri Oct 31 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.10.0-1
- updated to 0.10.0

* Sun Sep 07 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.8.1-2
- corrections in spec

* Sun Sep 07 2008 Pavel Lisy <pavel.lisy@gmail.com> - 0.8.1-1
- first build
