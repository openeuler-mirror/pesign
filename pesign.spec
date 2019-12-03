%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)
Name:          pesign
Summary:       Signing utility for UEFI binaries
Version:       0.112
Release:       28
License:       GPLv2
URL:           https://github.com/vathpela/pesign
Source0:       pesign-%{version}.tar.bz2
Source1:       certs.tar.xz
Source2:       pesign.py
Source3:       euleros-certs.tar.bz2
Obsoletes:     pesign-rh-test-certs <= 0.111-7
Requires:      nspr nss nss-util popt rpm
Requires(pre): shadow-utils
BuildRequires: nspr nss nss-util popt-devel nss-tools nspr-devel >= 4.9.2-1
BuildRequires: nss-devel >= 3.13.6-1 efivar-devel >= 31-1 libuuid-devel tar xz
BuildRequires: python3-rpm-macros python3 systemd

Patch0001:     0001-cms-kill-generate_integer-it-doesn-t-build-on-i686-a.patch
Patch0002:     0002-Fix-command-line-parsing.patch
Patch0003:     0003-gcc-don-t-error-on-stuff-in-includes.patch
Patch0004:     0004-Fix-certficate-argument-name.patch
Patch0005:     0005-Fix-description-of-ascii-armor-option-in-manpage.patch
Patch0006:     0006-Make-ascii-work-since-we-documented-it.patch
Patch0007:     0007-Switch-pesign-client-to-also-accept-token-cert-macro.patch
Patch0008:     0008-pesigcheck-Verify-with-the-cert-as-an-object-signer.patch
Patch0009:     0009-pesigcheck-make-certfile-actually-work.patch
Patch0010:     0010-signerInfos-make-sure-err-is-always-initialized.patch
Patch0011:     0011-pesign-make-pesign-h-tell-you-the-file-name.patch
Patch0012:     0012-Add-coverity-build-scripts.patch
Patch0013:     0013-Document-implicit-fallthrough.patch
Patch0014:     0014-Actually-setfacl-each-directory-of-our-key-storage.patch
Patch0015:     0015-oid-add-SHIM_EKU_MODULE_SIGNING_ONLY-and-fix-our-arr.patch
Patch0016:     0016-efikeygen-add-modsign.patch
Patch0017:     0017-check_cert_db-try-even-harder-to-pick-a-reasonable-v.patch
Patch0018:     0018-show-which-db-we-re-checking.patch
Patch0019:     0019-more-about-the-time.patch
Patch0020:     0020-try-to-say-why-something-fails.patch
Patch0021:     0021-Fix-race-condition-in-SEC_GetPassword.patch
Patch0022:     0022-sysvinit-Create-the-socket-directory-at-runtime.patch
Patch0023:     0023-Better-authorization-scripts.-Again.patch
Patch0024:     0024-Make-the-daemon-also-try-to-give-better-errors-on-EP.patch
Patch0025:     0025-certdb-fix-PRTime-printfs-for-i686.patch
Patch0026:     0026-Clean-up-gcc-command-lines-a-little.patch
Patch0027:     0027-Make-pesign-users-groups-static-in-the-repo.patch
Patch0028:     0028-rpm-Make-the-client-signer-use-the-fedora-values-unl.patch
Patch0029:     0029-Make-macros.pesign-error-in-kojibuilder-if-we-don-t-.patch

%description
pesign is a command line tool for manipulating signatures and
cryptographic digests of UEFI applications.

%package        help
Summary:        This package contains help documents
Requires:       %{name} = %{version}-%{release}

%description    help
Files for help with pesign.

%prep
%autosetup -n %{name}-%{version} -p1 -T -b 0 -D -c -a 1
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
rm -vf %{buildroot}/usr/share/doc/pesign-%{version}/COPYING
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
%exclude /usr/include
%exclude %{_libdir}/libdpe*
%exclude %{_sysconfdir}/rpm

%files help
%doc README TODO
%{_mandir}/man*/*

%changelog
* Tue Dec 3 2019 gulining<gulining1@huawei.com> - 0.112-28
- rewrite spec

* Mon Dec 2 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.112.27
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:roll back to the 0.112-24

* Sat Nov 30 2019 gulining<gulining1@huawei.com> - 0.112-26
- Pakcage init