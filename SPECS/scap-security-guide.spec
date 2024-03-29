# Base name of static rhel6 content tarball
%global _static_rhel6_content %{name}-0.1.52-2.el7_9-rhel6
# https://fedoraproject.org/wiki/Changes/CMake_to_do_out-of-source_builds
%global _vpath_builddir build
# global _default_patch_fuzz 2  # Normally shouldn't be needed as patches should apply cleanly

Name:                 scap-security-guide
Version:              0.1.66
Release:              2%{?dist}.rocky.0.1
Summary:              Security guidance and baselines in SCAP formats
License:              BSD-3-Clause
Group:                Applications/System
URL:                  https://github.com/ComplianceAsCode/content/
Source0:              https://github.com/ComplianceAsCode/content/releases/download/v%{version}/scap-security-guide-%{version}.tar.bz2
# Include tarball with last released rhel6 content
Source1:              %{_static_rhel6_content}.tar.bz2
# Patch prevents cjis, rht-ccp and standard profiles in RHEL8 datastream
Patch0:               disable-not-in-good-shape-profiles.patch
# Rsyslog files rules remediations
Patch1:               scap-security-guide-0.1.67-rsyslog_files_rules_remediations-PR_9789.patch
# Extends rsyslog_logfiles_attributes_modify template for permissions
Patch2:               scap-security-guide-0.1.67-rsyslog_files_permissions_template-PR_10139.patch
# Change custom zones check in firewalld_sshd_port_enabled
Patch3:               scap-security-guide-0.1.67-firewalld_sshd_port_enabled_tests-PR_10162.patch
# Accept required and requisite control flag for pam_pwhistory
Patch4:               scap-security-guide-0.1.67-pwhistory_control-PR_10175.patch
# remove rule logind_session_timeout and associated variable from profiles
Patch5:               scap-security-guide-0.1.67-remove_logind_session_timeout_from_profiles-PR_10202.patch
Patch6:               0001-Add-Rocky-Linux-as-a-derivative-of-RHEL.patch

BuildArch:            noarch

BuildRequires:        libxslt
BuildRequires:        expat
BuildRequires:        openscap-scanner >= 1.2.5
BuildRequires:        cmake >= 2.8
# To get python3 inside the buildroot require its path explicitly in BuildRequires
BuildRequires:        /usr/bin/python3
BuildRequires:        python%{python3_pkgversion}
BuildRequires:        python%{python3_pkgversion}-jinja2
BuildRequires:        python%{python3_pkgversion}-PyYAML
Requires:             xml-common, openscap-scanner >= 1.2.5
Obsoletes:            openscap-content < 0:0.9.13
Provides:             openscap-content

%description
The scap-security-guide project provides a guide for configuration of the
system from the final system's security point of view. The guidance is specified
in the Security Content Automation Protocol (SCAP) format and constitutes
a catalog of practical hardening advice, linked to government requirements
where applicable. The project bridges the gap between generalized policy
requirements and specific implementation guidelines. The system
administrator can use the oscap CLI tool from openscap-scanner package, or the
scap-workbench GUI tool from scap-workbench package to verify that the system
conforms to provided guideline. Refer to scap-security-guide(8) manual page for
further information.

%package	doc
Summary:              HTML formatted security guides generated from XCCDF benchmarks
Group:                System Environment/Base
Requires:             %{name} = %{version}-%{release}

%description	doc
The %{name}-doc package contains HTML formatted documents containing
hardening guidances that have been generated from XCCDF benchmarks
present in %{name} package.

%if %{defined rhel}
%package	rule-playbooks
Summary:              Ansible playbooks per each rule.
Group:                System Environment/Base
Requires:             %{name} = %{version}-%{release}

%description	rule-playbooks
The %{name}-rule-playbooks package contains individual ansible playbooks per rule.
%endif

%prep
%autosetup -p1 -b1

%build
mkdir -p build
cd build
%cmake \
-DSSG_PRODUCT_DEFAULT:BOOLEAN=FALSE \
-DSSG_PRODUCT_RHEL7:BOOLEAN=TRUE \
-DSSG_PRODUCT_RHEL8:BOOLEAN=TRUE -DSSG_ROCKY_LINUX_DERIVATIVES_ENABLED:BOOLEAN=TRUE:BOOLEAN=TRUE \
-DSSG_PRODUCT_FIREFOX:BOOLEAN=TRUE \
-DSSG_PRODUCT_JRE:BOOLEAN=TRUE \
%if %{defined centos}
-DSSG_CENTOS_DERIVATIVES_ENABLED:BOOL=ON \
%else
-DSSG_CENTOS_DERIVATIVES_ENABLED:BOOL=OFF \
%endif
-DSSG_SCIENTIFIC_LINUX_DERIVATIVES_ENABLED:BOOL=OFF \
%if %{defined rhel}
-DSSG_ANSIBLE_PLAYBOOKS_PER_RULE_ENABLED:BOOL=ON \
%endif
../
%cmake_build

%install
cd build
%cmake_install

# Manually install pre-built rhel6 content
cp -r %{_builddir}/%{_static_rhel6_content}/usr %{buildroot}
cp -r %{_builddir}/%{_static_rhel6_content}/tables %{buildroot}%{_docdir}/%{name}
cp -r %{_builddir}/%{_static_rhel6_content}/guides %{buildroot}%{_docdir}/%{name}

%files
%{_datadir}/xml/scap/ssg/content
%{_datadir}/%{name}/kickstart
%{_datadir}/%{name}/ansible
%{_datadir}/%{name}/bash
%{_datadir}/%{name}/tailoring
%lang(en) %{_mandir}/man8/scap-security-guide.8.*
%doc %{_docdir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/Contributors.md
%if %{defined rhel}
%exclude %{_datadir}/%{name}/ansible/rule_playbooks
%endif

%files doc
%doc %{_docdir}/%{name}/guides/*.html
%doc %{_docdir}/%{name}/tables/*.html

%if %{defined rhel}
%files rule-playbooks
%defattr(-,root,root,-)
%{_datadir}/%{name}/ansible/rule_playbooks
%endif

%changelog
* Tue May 16 2023 Release Engineering <releng@rockylinux.org> - 0.1.66-2.rocky.0.1
- Make Rocky Linux a derivative of RHEL

* Mon Feb 13 2023 Watson Sato <wsato@redhat.com> - 0.1.66-2
- Unselect rule logind_session_timeout (RHBZ#2158404)

* Mon Feb 06 2023 Watson Sato <wsato@redhat.com> - 0.1.66-1
- Rebase to a new upstream release 0.1.66 (RHBZ#2158404)
- Update RHEL8 STIG profile to V1R9 (RHBZ#2152658)
- Fix levels of CIS rules (RHBZ#2162803)
- Remove unused RHEL8 STIG control file (RHBZ#2156192)
- Fix accounts_password_pam_unix_remember's check and remediations (RHBZ#2153547)
- Fix handling of space in sudo_require_reauthentication (RHBZ#2152208)
- Add rule for audit immutable login uids (RHBZ#2151553)
- Fix remediation of audit watch rules (RHBZ#2119356)
- Align file_permissions_sshd_private_key with DISA Benchmark (RHBZ#2115343)
- Fix applicability of kerberos rules (RHBZ#2099394)
- Add support rainer scripts in rsyslog rules (RHBZ#2072444)

* Tue Jan 10 2023 Watson Sato <wsato@redhat.com> - 0.1.63-5
- Update RHEL8 STIG profile to V1R8 (RHBZ#2148446)
- Add rule warning for sysctl IPv4 forwarding config (RHBZ#2118758)
- Fix remediation for firewalld_sshd_port_enabled (RHBZ#2116474)
- Fix compatibility with Ansible 2.14

* Wed Aug 17 2022 Watson Sato <wsato@redhat.com> - 0.1.63-4
- Fix check of enable_fips_mode on s390x (RHBZ#2070564)

* Mon Aug 15 2022 Watson Sato <wsato@redhat.com> - 0.1.63-3
- Fix Ansible partition conditional (RHBZ#2032403)

* Wed Aug 10 2022 Vojtech Polasek <vpolasek@redhat.com> - 0.1.63-2
- aligning with the latest STIG update (RHBZ#2112937)
- OSPP: use Authselect minimal profile (RHBZ#2117192)
- OSPP: change rules for protecting of boot (RHBZ#2116440)
- add warning about configuring of TCP queues to rsyslog_remote_loghost (RHBZ#2078974)
- fix handling of Defaults clause in sudoers (RHBZ#2083109)
- make rules checking for mount options of /tmp and /var/tmp applicable only when the partition really exists (RHBZ#2032403)
- fix handling of Rsyslog include directives (RHBZ#2075384)

* Mon Aug 01 2022 Vojtech Polasek <vpolasek@redhat.com> - 0.1.63-1
- Rebase to a new upstream release 0.1.63 (RHBZ#2070564)

* Wed Jun 01 2022 Matej Tyc <matyc@redhat.com> - 0.1.62-1
- Rebase to a new upstream release (RHBZ#2070564)

* Tue May 17 2022 Watson Sato <wsato@redhat.com> - 0.1.60-9
- Fix validation of OVAL 5.10 content (RHBZ#2079241)
- Fix Ansible sysctl remediation (RHBZ#2079241)

* Tue May 03 2022 Watson Sato <wsato@redhat.com> - 0.1.60-8
- Update to ensure a sysctl option is not defined in multiple files (RHBZ#2079241)
- Update RHEL8 STIG profile to V1R6 (RHBZ#2079241)

* Thu Feb 24 2022 Watson Sato <wsato@redhat.com> - 0.1.60-7
- Resize ANSSI kickstart partitions to accommodate GUI installs (RHBZ#2058033)

* Wed Feb 23 2022 Matthew Burket <mburket@redhat.com> - 0.1.60-6
- Fix another issue with getting STIG items in create_scap_delta_tailoring.py (RHBZ#2014485)

* Mon Feb 21 2022 Gabriel Becker <ggasparb@redhat.com> - 0.1.60-5
- Remove tmux process runinng check in configure_bashrc_exec_tmux (RHBZ#2055860)
- Fix issue with getting STIG items in create_scap_delta_tailoring.py (RHBZ#2014485)
- Update rule enable_fips_mode to check only for technical state (RHBZ#2014485)

* Wed Feb 16 2022 Watson Sato <wsato@redhat.com> - 0.1.60-4
- Fix Ansible service disabled tasks (RHBZ#2014485)
- Set rule package_krb5-workstation_removed as not applicable on RHV (RHBZ#2055149)

* Mon Feb 14 2022 Gabriel Becker <ggasparb@redhat.com> - 0.1.60-3
- Update sudoers rules in RHEL8 STIG V1R5 (RHBZ#2049555)
- Add missing SRG references in RHEL8 STIG V1R5 rules (RHBZ#2049555)
- Update chronyd_or_ntpd_set_maxpoll to disregard server and poll directives (RHBZ#2026301)
- Fix GRUB2 rule template to configure the module correctly on RHEL8 (RHBZ#2030966)
- Update GRUB2 rule descriptions (RHBZ#2014485)
- Make package_rear_installed not applicable on AARCH64 (RHBZ#2014485)

* Fri Feb 11 2022 Watson Sato <wsato@redhat.com> - 0.1.60-2
- Update RHEL8 STIG profile to V1R5 (RHBZ#2049555)
- Align audit rules for OSPP profile (RHBZ#2000264)
- Fix rule selection in ANSSI Enhanced profile (RHBZ#2053587)

* Thu Jan 27 2022 Watson Sato <wsato@redhat.com> - 0.1.60-1
- Rebase to a new upstream release (RHBZ#2014485)

* Wed Dec 01 2021 Watson Sato <wsato@redhat.com> - 0.1.59-1
- Rebase to a new upstream release (RHBZ#2014485)

* Fri Oct 15 2021 Matej Tyc <matyc@redhat.com> - 0.1.58-1
- Rebase to a new upstream release. (RHBZ#2014485)
- Add a VM wait handling to fix issues with tests.

* Tue Aug 24 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.57-4
- Fix a value selector in RHEL8 CIS L1 profiles (RHBZ#1993197)

* Mon Aug 23 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.57-3
- Fix remaining audit rules file permissions (RHBZ#1993056)
- Mark a STIG service rule as machine only (RHBZ#1993056)
- Fix a remaining broken RHEL7 documentation link. (RHBZ#1966577)

* Fri Aug 20 2021 Marcus Burghardt <maburgha@redhat.com> - 0.1.57-2
- Update Ansible login banner fixes to avoid unnecessary updates (RHBZ#1857179)
- Include tests for Ansible Playbooks that remove and reintroduce files.
- Update RHEL8 STIG profile to V1R3 (RHBZ#1993056) 
- Improve Audit Rules remediation to group similar syscalls (RHBZ#1876483)
- Reestructure RHEL7 and RHEL8 CIS profiles according to the policy (RHBZ#1993197)
- Add Kickstart files for ISM profile (RHBZ#1955373)
- Fix broken RHEL7 documentation links (RHBZ#1966577)

* Fri Jul 30 2021 Matej Tyc <matyc@redhat.com> - 0.1.57-1
- Update to the latest upstream release (RHBZ#1966577)
- Enable the ISM profile.

* Tue Jun 8 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.56-2
- Create subpackage to hold ansible playbooks per rule (RHBZ#1966604)

* Tue Jun 01 2021 Watson Sato <wsato@redhat.com> - 0.1.56-1
- Update to the latest upstream release (RHBZ#1966577)
- Add ANSSI High Profile (RHBZ#1955183)

* Wed Feb 17 2021 Watson Sato <wsato@redhat.com> - 0.1.54-5
- Remove Kickstart for not shipped profile (RHBZ#1778188)

* Tue Feb 16 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.54-4
- Remove auditd_data_retention_space_left from RHEL8 STIG profile (RHBZ#1918742)

* Tue Feb 16 2021 Vojtech Polasek <vpolasek@redhat.com> - 0.1.54-3
- drop kernel_module_vfat_disabled from CIS profiles (RHBZ#1927019)

* Fri Feb 12 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.54-2
- Add initial RHEL8 STIG V1R1 profile (RHBZ#1918742)

* Thu Feb 04 2021 Watson Sato <wsato@redhat.com> - 0.1.54-1
- Update to the latest upstream release (RHBZ#1889344)
- Add Minimal, Intermediary and Enhanced ANSSI Profiles (RHBZ#1778188)

* Fri Jan 08 2021 Gabriel Becker <ggasparb@redhat.com> - 0.1.53-4
- Fix description of rule installed_OS_is_vendor_supported (RHBZ#1914193)
- Fix RHEL6 CPE dictionary (RHBZ#1899059)
- Fix SRG mapping references for ssh_client_rekey_limit and use_pam_wheel_for_su (RHBZ#1914853)

* Tue Dec 15 2020 Gabriel Becker <ggasparb@redhat.com> - 0.1.53-3
- Enforce pam_wheel for "su" in the OSPP profile (RHBZ#1884062)
- Fix case insensitive checking in rsyslog_remote_tls (RHBZ#1899032)
- Exclude kernel_trust_cpu_rng related rules on s390x (RHBZ#1899041)
- Create a SSH_USE_STRONG_RNG rule for SSH client and select it in OSPP profile (RHBZ#1884067)
- Disable usbguard rules on s390x architecture (RHBZ#1899059)

* Thu Dec 03 2020 Watson Sato <wsato@redhat.com> - 0.1.53-2
- Update list of profiles built (RHBZ#1889344)

* Wed Nov 25 2020 Vojtech Polasek <vpolasek@redhat.com> - 0.1.53-1
- Update to the latest upstream release (RHBZ#1889344)

* Wed Sep 02 2020 Matěj Týč <matyc@redhat.com> - 0.1.50-14
- Added a kickstart for the RHEL-8 CUI Profile (RHBZ#1762962)

* Tue Aug 25 2020 Watson Sato <wsato@redhat.com> - 0.1.50-13
- Enable build of RHEL-8 CUI Profile (RHBZ#1762962)

* Fri Aug 21 2020 Matěj Týč <matyc@redhat.com> - 0.1.50-12
- remove rationale from rules that contain defective links (rhbz#1854854)

* Thu Aug 20 2020 Matěj Týč <matyc@redhat.com> - 0.1.50-11
- fixed link in a grub2 rule description (rhbz#1854854)
- fixed selinux_all_devicefiles_labeled rule (rhbz#1852367)
- fixed no_shelllogin_for_systemaccounts on ubi8 (rhbz#1836873)

* Mon Aug 17 2020 Matěj Týč <matyc@redhat.com> - 0.1.50-10
- Update the scapval invocation (RHBZ#1815007)
- Re-added the SSH Crypto Policy rule to OSPP, and added an SRG to the rule (RHBZ#1815007)
- Change the spec file macro invocation from patch to Patch
- Fix the rekey limit in ssh/sshd rules (RHBZ#1813066)

* Wed Aug 05 2020 Vojtech Polasek <vpolasek@redhat.com> - 0.1.50-9
- fix description of HIPAA profile (RHBZ#1867559)

* Fri Jul 17 2020 Watson Sato <wsato@redhat.com> - 0.1.50-8
- Add rule to harden OpenSSL crypto-policy (RHBZ#1852928)
  - Remove CCM from TLS Ciphersuites

* Mon Jun 29 2020 Matěj Týč <matyc@redhat.com> - 0.1.50-7
- Fix the OpenSSL Crypto Policy rule (RHBZ#1850543)

* Mon Jun 22 2020 Gabriel Becker <ggasparb@redhat.com> - 0.1.50-6
- Fix rsyslog permissions/ownership rules (RHBZ#1781606)

* Thu May 28 2020 Gabriel Becker <ggasparb@redhat.com> - 0.1.50-5
- Fix SELinux remediation to detect properly current configuration. (RHBZ#1750526)

* Tue May 26 2020 Watson Sato <wsato@redhat.com> - 0.1.50-4
- CIS Ansible fixes (RHBZ#1760734)
- HIPAA Ansible fixes (RHBZ#1832760)

* Mon May 25 2020 Watson Sato <wsato@redhat.com> - 0.1.50-3
 - HIPAA Profile (RHBZ#1832760)
  - Enable build of RHEL8 HIPAA Profile
  - Add kickstarts for HIPAA
- CIS Profile (RHBZ#1760734)
  - Add Ansible fix for sshd_set_max_sessions
  - Add CIS Profile content attribution to Center for Internet Security

* Fri May 22 2020 Watson Sato <wsato@redhat.com> - 0.1.50-2
- Fix Ansible for no_direct_root_logins
- Fix Ansible template for SELinux booleans
- Add CCEs to rules in RHEL8 CIS Profile (RHBZ#1760734)

* Wed May 20 2020 Watson Sato <wsato@redhat.com> - 0.1.50-2
- Update selections in RHEL8 CIS Profile (RHBZ#1760734)

* Tue May 19 2020 Watson Sato <wsato@redhat.com> - 0.1.50-1
- Update to the latest upstream release (RHBZ#1815007)

* Thu Mar 19 2020 Gabriel Becker <ggasparb@redhat.com> - 0.1.49-1
- Update to the latest upstream release (RHBZ#1815007)

* Tue Feb 11 2020 Watson Sato <wsato@redhat.com> - 0.1.48-7
- Update baseline package list of OSPP profile

* Thu Feb 06 2020 Watson Sato <wsato@redhat.com> - 0.1.48-6
- Rebuilt with correct spec file

* Thu Feb 06 2020 Watson Sato <wsato@redhat.com> - 0.1.48-5
- Add SRG references to STIG rules (RHBZ#1755447)

* Mon Feb 03 2020 Vojtech Polasek <vpolasek@redhat.com> - 0.1.48-4
- Drop rsyslog rules from OSPP profile
- Update COBIT URI
- Add rules for strong source of RNG entropy
- Enable build of RHEL8 STIG Profile (RHBZ#1755447)
- STIG profile: added rsyslog rules and updated SRG mappings
- Split audit rules according to audit component (RHBZ#1791312)

* Tue Jan 21 2020 Watson Sato <wsato@redhat.com> - 0.1.48-3
- Update crypto-policy test scenarios
- Update max-path-len test to skip tests/logs directory

* Fri Jan 17 2020 Watson Sato <wsato@redhat.com> - 0.1.48-2
- Fix list of tables that are generated for RHEL8

* Fri Jan 17 2020 Watson Sato <wsato@redhat.com> - 0.1.48-1
- Update to latest upstream SCAP-Security-Guide-0.1.48 release

* Tue Nov 26 2019 Matěj Týč <matyc@redhat.com> - 0.1.47-2
- Improved the e8 profile (RHBZ#1755194)

* Mon Nov 11 2019 Vojtech Polasek <vpolasek@redhat.com> - 0.1.47-1
- Update to latest upstream SCAP-Security-Guide-0.1.47 release (RHBZ#1757762)

* Wed Oct 16 2019 Gabriel Becker <ggasparb@redhat.com> - 0.1.46-3
- Align SSHD crypto policy algorithms to Common Criteria Requirements. (RHBZ#1762821)

* Wed Oct 09 2019 Watson Sato <wsato@redhat.com> - 0.1.46-2
- Fix evaluaton and remediation of audit rules in PCI-DSS profile (RHBZ#1754919)

* Mon Sep 02 2019 Watson Sato <wsato@redhat.com> - 0.1.46-1
- Update to latest upstream SCAP-Security-Guide-0.1.46 release
- Align OSPP Profile with Common Criteria Requirements (RHBZ#1714798)

* Wed Aug 07 2019 Milan Lysonek <mlysonek@redhat.com> - 0.1.45-2
- Use crypto-policy rules in OSPP profile.
- Re-enable FIREFOX and JRE product in build.
- Change test suite logging message about missing profile from ERROR to WARNING.
- Build only one version of SCAP content at a time.

* Tue Aug 06 2019 Milan Lysonek <mlysonek@redhat.com> - 0.1.45-1
- Update to latest upstream SCAP-Security-Guide-0.1.45 release

* Mon Jun 17 2019 Matěj Týč <matyc@redhat.com> - 0.1.44-2
- Ported changelog from late 8.0 builds.
- Disabled build of the OL8 product, updated other components of the cmake invocation.

* Fri Jun 14 2019 Matěj Týč <matyc@redhat.com> - 0.1.44-1
- Update to latest upstream SCAP-Security-Guide-0.1.44 release

* Mon Mar 11 2019 Gabriel Becker <ggasparb@redhat.com> - 0.1.42-11
- Assign CCE to rules from OSPP profile which were missing the identifier.
- Fix regular expression for Audit rules ordering
- Account for Audit rules flags parameter position within syscall
- Add remediations for Audit rules file path
- Add Audit rules for modification of /etc/shadow and /etc/gshadow
- Add Ansible and Bash remediations for directory_access_var_log_audit rule
- Add a Bash remediation for Audit rules that require ordering

* Thu Mar 07 2019 Gabriel Becker <ggasparb@redhat.com> - 0.1.42-10
- Assign CCE identifier to rules used by RHEL8 profiles.

* Thu Feb 14 2019 Matěj Týč <matyc@redhat.com> - 0.1.42-9
- Fixed Crypto Policy OVAL for NSS
- Got rid of rules requiring packages dropped in RHEL8.
- Profile descriptions fixes.

* Tue Jan 22 2019 Jan Černý <jcerny@redhat.com> - 0.1.42-8
- Update applicable platforms in crypto policy tests

* Mon Jan 21 2019 Jan Černý <jcerny@redhat.com> - 0.1.42-7
- Introduce Podman backend for SSG Test suite
- Update bind and libreswan crypto policy test scenarios

* Fri Jan 11 2019 Matěj Týč <matyc@redhat.com> - 0.1.42-6
- Further fix of profiles descriptions, so they don't contain literal '\'.
- Removed obsolete sshd rule from the OSPP profile.

* Tue Jan 08 2019 Matěj Týč <matyc@redhat.com> - 0.1.42-5
- Fixed profiles descriptions, so they don't contain literal '\n'.
- Made the configure_kerberos_crypto_policy OVAL more robust.
- Made OVAL for libreswan and bind work as expected when those packages are not installed.

* Wed Jan 02 2019 Matěj Týč <matyc@redhat.com> - 0.1.42-4
- Fixed the regression of enable_fips_mode missing OVAL due to renamed OVAL defs.

* Tue Dec 18 2018 Matěj Týč <matyc@redhat.com> - 0.1.42-3
- Added FIPS mode rule for the OSPP profile.
- Split the installed_OS_is certified rule.
- Explicitly disabled OSP13, RHV4 and Example products.

* Mon Dec 17 2018 Gabriel Becker <ggasparb@redhat.com> - 0.1.42-2
- Add missing kickstart files for RHEL8
- Disable profiles that are not in good shape for RHEL8

* Wed Dec 12 2018 Matěj Týč <matyc@redhat.com> - 0.1.42-1
- Update to latest upstream SCAP-Security-Guide-0.1.42 release:
  https://github.com/ComplianceAsCode/content/releases/tag/v0.1.42
- System-wide crypto policies are introduced for RHEL8
- Patches introduced the RHEL8 product were dropped, as it has been upstreamed.

* Wed Oct 10 2018 Watson Yuuma Sato <wsato@redhat.com> - 0.1.41-2
- Fix man page and package description

* Mon Oct 08 2018 Watson Yuuma Sato <wsato@redhat.com> - 0.1.41-1
- Update to latest upstream SCAP-Security-Guide-0.1.41 release:
  https://github.com/ComplianceAsCode/content/releases/tag/v0.1.41
- Add RHEL8 Product with OSPP4.2 and PCI-DSS Profiles

* Mon Aug 13 2018 Watson Sato <wsato@redhat.com> - 0.1.40-3
- Use explicit path BuildRequires to get /usr/bin/python3 inside the buildroot
- Only build content for rhel8 products

* Fri Aug 10 2018 Watson Sato <wsato@redhat.com> - 0.1.40-2
- Update build of rhel8 content

* Fri Aug 10 2018 Watson Sato <wsato@redhat.com> - 0.1.40-1
- Enable build of rhel8 content

* Fri May 18 2018 Jan Černý <jcerny@redhat.com> - 0.1.39-1
- Update to latest upstream SCAP-Security-Guide-0.1.39 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.39
- Fix spec file to build using Python 3
- Fix License because upstream changed to BSD-3

* Mon Mar 05 2018 Watson Yuuma Sato <wsato@redhat.com> - 0.1.38-1
- Update to latest upstream SCAP-Security-Guide-0.1.38 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.38

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.37-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 04 2018 Watson Yuuma Sato <wsato@redhat.com> - 0.1.37-1
- Update to latest upstream SCAP-Security-Guide-0.1.37 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.37

* Wed Nov 01 2017 Watson Yuuma Sato <wsato@redhat.com> - 0.1.36-1
- Update to latest upstream SCAP-Security-Guide-0.1.36 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.36

* Tue Aug 29 2017 Watson Sato <wsato@redhat.com> - 0.1.35-1
- Update to latest upstream SCAP-Security-Guide-0.1.35 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.35

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.34-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 03 2017 Watson Sato <wsato@redhat.com> - 0.1.34-1
- updated to latest upstream release

* Mon May 01 2017 Martin Preisler <mpreisle@redhat.com> - 0.1.33-1
- updated to latest upstream release

* Thu Mar 30 2017 Martin Preisler <mpreisle@redhat.com> - 0.1.32-1
- updated to latest upstream release

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.31-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 28 2016 Martin Preisler <mpreisle@redhat.com> - 0.1.31-2
- use make_build and make_install RPM macros

* Mon Nov 28 2016 Martin Preisler <mpreisle@redhat.com> - 0.1.31-1
- update to the latest upstream release
- new default location for content /usr/share/scap/ssg
- install HTML tables in the doc subpackage

* Mon Jun 27 2016 Jan iankko Lieskovsky <jlieskov@redhat.com> - 0.1.30-2
- Correct currently failing parallel SCAP Security Guide build

* Mon Jun 27 2016 Jan iankko Lieskovsky <jlieskov@redhat.com> - 0.1.30-1
- Update to latest upstream SCAP-Security-Guide-0.1.30 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.30
- Drop shell library for remediation functions since it is not required
  starting from 0.1.30 release any more

* Thu May 05 2016 Jan iankko Lieskovsky <jlieskov@redhat.com> - 0.1.29-1
- Update to latest upstream SCAP-Security-Guide-0.1.29 release:
  https://github.com/OpenSCAP/scap-security-guide/releases/tag/v0.1.29
- Do not ship Firefox/DISCLAIMER documentation file since it has been removed
  in 0.1.29 upstream release

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.28-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Šimon Lukašík <slukasik@redhat.com> - 0.1.28-1
- upgrade to the latest upstream release

* Fri Dec 11 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.27-1
- update to the latest upstream release

* Tue Oct 20 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.26-1
- update to the latest upstream release

* Sat Sep 05 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.25-1
- update to the latest upstream release

* Thu Jul 09 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.24-1
- update to the latest upstream release
- created doc sub-package to ship all the guides
- start distributing centos and scientific linux content
- rename java content to jre

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 05 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.22-1
- update to the latest upstream release
- only DataStream file is now available for Fedora
- start distributing security baseline for Firefox
- start distributing security baseline for Java RunTime deployments

* Wed Mar 04 2015 Šimon Lukašík <slukasik@redhat.com> - 0.1.21-1
- update to the latest upstream release
- move content to /usr/share/scap/ssg/content

* Thu Oct 02 2014 Šimon Lukašík <slukasik@redhat.com> - 0.1.19-1
- update to the latest upstream release

* Mon Jul 14 2014 Šimon Lukašík <slukasik@redhat.com> - 0.1.5-4
- require only openscap-scanner, not whole openscap-utils package

* Tue Jul 01 2014 Šimon Lukašík <slukasik@redhat.com> - 0.1.5-3
- Rebase the RHEL part of SSG to the latest upstream version (0.1.18)
- Add STIG DISCLAIMER to the shipped documentation

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Feb 27 2014 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1.5-1
- Fix fedora-srpm and fedora-rpm Make targets to work again
- Include RHEL-6 and RHEL-7 datastream files to support remote RHEL system scans
- EOL for Fedora 18 support
- Include Fedora datastream file for remote Fedora system scans

* Mon Jan 06 2014 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1.4-2
- Drop -compat package, provide openscap-content directly (RH BZ#1040335#c14)

* Fri Dec 20 2013 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1.4-1
- Fix remediation for sshd set keepalive (ClientAliveCountMax) and move
  it to /shared
- Add shared remediations for sshd disable empty passwords and
  sshd set idle timeout
- Shared remediation for sshd disable root login
- Add empty -compat subpackage to ensure backward-compatibility with
  openscap-content and firstaidkit-plugin-openscap packages (RH BZ#1040335)
- OVAL check for sshd disable root login
- Fix typo in OVAL check for sshd disable empty passwords
- OVAL check for sshd disable empty passwords
- Unselect no shelllogin for systemaccounts rule from being run by default
- Rename XCCDF rules
- Revert Set up Fedora release name and CPE based on build system properties
- Shared OVAL check for Verify that Shared Library Files Have Root Ownership
- Shared OVAL check for Verify that System Executables Have Restrictive Permissions
- Shared OVAL check for Verify that System Executables Have Root Ownership
- Shared OVAL check for Verify that Shared Library Files Have Restrictive
  Permissions
- Fix remediation for Disable Prelinking rule
- OVAL check and remediation for sshd's ClientAliveCountMax rule
- OVAL check for sshd's ClientAliveInterval rule
- Include descriptions for permissions section, and rules for checking
  permissions and ownership of shared library files and system executables
- Disable selected rules by default
- Add remediation for Disable Prelinking rule
- Adjust service-enable-macro, service-disable-macro XSLT transforms
  definition to evaluate to proper systemd syntax
- Fix service_ntpd_enabled OVAL check make validate to pass again
- Include patch from Šimon Lukašík to obsolete openscap-content
  package (RH BZ#1028706)
- Add OVAL check to test if there's is remote NTP server configured for
  time data
- Add system settings section for the guide (to track system wide
  hardening configurations)
- Include disable prelink rule and OVAL check for it
- Initial OVAL check if ntpd service is enabled. Add package_installed
  OVAL templating directory structure and functionality.
- Include services section, and XCCDF description for selected ntpd's
  sshd's service rules
- Include remediations for login.defs' based password minimum, maximum and
  warning age rules
- Include directory structure to support remediations
- Add SCAP "replace or append pattern value in text file based on variable"
  remediation script generator
- Add remediation for "Set Password Minimum Length in login.defs" rule

* Mon Nov 18 2013 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1.3-1
- Update versioning scheme - move fedorassgrelease to be part of
  upstream version. Rename it to fedorassgversion to avoid name collision
  with Fedora package release.

* Tue Oct 22 2013 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1-3
- Add .gitignore for Fedora output directory
- Set up Fedora release name and CPE based on build system properties
- Use correct file paths in scap-security-guide(8) manual page
  (RH BZ#1018905, c#10)
- Apply further changes motivated by scap-security-guide Fedora RPM review
  request (RH BZ#1018905, c#8):
  * update package description,
  * make content files to be owned by the scap-security-guide package,
  * remove Fedora release number from generated content files,
  * move HTML form of the guide under the doc directory (together
    with that drop fedora/content subdir and place the content
    directly under fedora/ subdir).
- Fixes for scap-security-guide Fedora RPM review request (RH BZ#1018905):
  * drop Fedora release from package provided files' final path (c#5),
  * drop BuildRoot, selected Requires:, clean section, drop chcon for
    manual page, don't gzip man page (c#4),
  * change package's description (c#4),
  * include PD license text (#c4).

* Mon Oct 14 2013 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1-2
- Provide manual page for scap-security-guide
- Remove percent sign from spec's changelog to silence rpmlint warning
- Convert RHEL6 'Restrict Root Logins' section's rules to Fedora
- Convert RHEL6 'Set Password Expiration Parameter' rules to Fedora
- Introduce 'Account and Access Control' section
- Convert RHEL6 'Verify Proper Storage and Existence of Password Hashes' section's
  rules to Fedora
- Set proper name of the build directory in the spec's setup macro.
- Replace hard-coded paths with macros. Preserve attributes when copying files.

* Tue Sep 17 2013 Jan iankko Lieskovsky <jlieskov@redhat.com> 0.1-1
- Initial Fedora SSG RPM.
