%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)
Name:          pesign
Summary:       Signing utility for UEFI binaries
Version:       0.113
Release:       6
License:       GPLv2
URL:           https://github.com/vathpela/pesign
Source0:       https://github.com/rhboot/pesign/archive/113.tar.gz
Source1:       certs.tar.xz
Source2:       pesign.py
Source3:       euleros-certs.tar.bz2
Obsoletes:     pesign-rh-test-certs <= 0.111-7
Requires:      nspr nss nss-util popt rpm
Requires(pre): shadow-utils
BuildRequires: nspr nss nss-util popt-devel nss-tools nspr-devel >= 4.9.2-1
BuildRequires: nss-devel >= 3.13.6-1 efivar-devel >= 31-1 libuuid-devel tar xz
BuildRequires: python3-rpm-macros python3 systemd python3-devel gcc

Patch0001:     Fix-the-build-with-nss-3.44.patch
Patch0002:     remove-superfluous-type-settings.patch
Patch0003:     Fix-CVE-2022-3560.patch

%description
pesign is a command line tool for manipulating signatures and
cryptographic digests of UEFI applications.

%package        help
Summary:        This package contains help documents
Requires:       %{name} = %{version}-%{release}

%description    help
Files for help with pesign.

%prep
%autosetup -n %{name}-113 -p1 -T -b 0 -D -c -a 1
tar -jxf %{SOURCE3}

%build
make PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
mkdir -p %{buildroot}/%{_libdir}
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install_systemd
install -D etc/pki/pesign/* %{buildroot}%{_sysconfdir}/pki/pesign/
install -D etc/pki/pesign-rh-test/* %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/
mv euleros-certs/etc/pki/pesign/euleros-pesign-db %{buildroot}/etc/pki/pesign/
install -D %{buildroot}%{_sysconfdir}/rpm/macros.pesign %{buildroot}%{macrosdir}/macros.pesign
rm -vf %{buildroot}/usr/share/doc/pesign-113/COPYING
install -d -m 0755 %{buildroot}%{python3_sitelib}/mockbuild/plugins/
install -m 0755 %{SOURCE2} %{buildroot}%{python3_sitelib}/mockbuild/plugins/

%pre
getent group pesign >/dev/null || groupadd -r pesign
getent passwd pesign >/dev/null || \
        useradd -r -g pesign -d /var/run/pesign -s /sbin/nologin \
                -c "Group for the pesign signing daemon" pesign
exit 0

%post
%systemd_post pesign.service

%preun
%systemd_preun pesign.service

%postun
%systemd_postun_with_restart pesign.service

%files
%doc COPYING
%{_bindir}/*
%dir %{_libexecdir}/pesign/
%dir %attr(0770,pesign,pesign) %{_sysconfdir}/pki/pesign/
%config(noreplace) %attr(0660,pesign,pesign) %{_sysconfdir}/pki/pesign/*
%dir %attr(0775,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/
%config(noreplace) %attr(0664,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/*
%{_libexecdir}/pesign/pesign-authorize
%config(noreplace)/%{_sysconfdir}/pesign/*
%{_sysconfdir}/popt.d/pesign.popt
%{macrosdir}/macros.pesign
%dir %attr(0770, pesign, pesign) %{_localstatedir}/run/%{name}
%dir %attr(0775,pesign,pesign) /etc/pki/pesign/euleros-pesign-db
%attr(0644,pesign,pesign) /etc/pki/pesign/euleros-pesign-db/*
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/socket
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/pesign.pid
%{_tmpfilesdir}/pesign.conf
%{_unitdir}/pesign.service
%{python3_sitelib}/mockbuild/plugins/*/pesign.*
%{python3_sitelib}/mockbuild/plugins/pesign.*
%exclude /boot
%exclude %{_sysconfdir}/rpm

%files help
%doc README TODO
%{_mandir}/man*/*

%changelog
* Tue Feb 14 2023 luopihui <luopihui@ncti-gba.cn> - 0.113-6
- Fix CVE-2022-3560

* Sat July 31 2021 Shenmei Tu <tushenmei@huawei.com> - 0.113-5
- remove-superfluous-type-settings.patch

* Mon May 31 2021 huanghaitao <huanghaitao8@huawei.com> - 0.113-4
- Completing build dependencies

* Thu Sep 10 2020 baizhonggui <baizhonggui@huawei.com> - 0.113-3
- Modify source0 and replace package

* Wed Aug 05 2020 lingsheng <lingsheng@huawei.com> - 0.113-2
- Fix the build with nss 3.44

* Mon Jan 13 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.113-1
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:update to 0.113

* Tue Dec 3 2019 gulining<gulining1@huawei.com> - 0.112-28
- rewrite spec

* Mon Dec 2 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.112.27
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:roll back to the 0.112-24

* Sat Nov 30 2019 gulining<gulining1@huawei.com> - 0.112-26
- Pakcage init
