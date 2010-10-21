%global gname haclient
%global uname hacluster
%global pcmk_docdir %{_docdir}/%{name}

%global specversion 1
#global upstream_version tip
%global upstream_prefix pacemaker

# Keep around for when/if required
#global alphatag %{upstream_version}.hg

%global pcmk_release %{?alphatag:0.}%{specversion}%{?alphatag:.%{alphatag}}%{?dist}

# Compatibility macros for distros (fedora) that don't provide Python macros by default
# Do this instead of trying to conditionally %include %{_rpmconfigdir}/macros.python
%{!?py_ver:     %{expand: %%global py_ver      %%(echo `python -c "import sys; print sys.version[:3]"`)}}
%{!?py_prefix:  %{expand: %%global py_prefix   %%(echo `python -c "import sys; print sys.prefix"`)}}
%{!?py_libdir:  %{expand: %%global py_libdir   %%{expand:%%%%{py_prefix}/%%%%{_lib}/python%%%%{py_ver}}}}
%{!?py_sitedir: %{expand: %%global py_sitedir  %%{expand:%%%%{py_libdir}/site-packages}}}

# Compatibility macro wrappers for legacy RPM versions that do not
# support conditional builds
%{!?bcond_without: %{expand: %%global bcond_without() %%{expand:%%%%{!?_without_%%{1}:%%%%global with_%%{1} 1}}}}
%{!?bcond_with:    %{expand: %%global bcond_with()    %%{expand:%%%%{?_with_%%{1}:%%%%global with_%%{1} 1}}}}
%{!?with:          %{expand: %%global with()          %%{expand:%%%%{?with_%%{1}:1}%%%%{!?with_%%{1}:0}}}}
%{!?without:       %{expand: %%global without()       %%{expand:%%%%{?with_%%{1}:0}%%%%{!?with_%%{1}:1}}}}

# Conditionals
# Invoke "rpmbuild --without <feature>" or "rpmbuild --with <feature>"
# to disable or enable specific features

# Supported cluster stacks, must support at least one
%bcond_with cman
%bcond_without ais
%bcond_without heartbeat

# ESMTP is not available in RHEL, only in EPEL. Allow people to build
# the RPM without ESMTP in case they choose not to use EPEL packages
%bcond_without esmtp
%bcond_without snmp

# Build with/without support for profiling tools
%bcond_with profiling
%bcond_with gcov

%if %{with profiling}
# This disables -debuginfo package creation and also the stripping binaries/libraries
# Useful if you want sane profiling data
%global debug_package %{nil}
%endif

# Support additional trace logging
%bcond_with tracedata

# We generate some docs using Publican, but its not available everywhere
%bcond_without publican

Name:		pacemaker
Summary:	Scalable High-Availability cluster resource manager
Version:	1.1.4
Release:	%{pcmk_release}
License:	GPLv2+ and LGPLv2+
Url:		http://www.clusterlabs.org
Group:		System Environment/Daemons
Source0:	pacemaker.tar.bz2
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
AutoReqProv:	on
Requires(pre):	cluster-glue >= 1.0.6
Requires:	resource-agents
Requires:	python >= 2.4
Conflicts:      heartbeat < 2.99

%if 0%{?fedora} || 0%{?centos} > 4 || 0%{?rhel} > 4
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:  help2man libtool-ltdl-devel
%endif

%if 0%{?suse_version}
# net-snmp-devel on SLES10 does not suck in tcpd-devel automatically
BuildRequires:  help2man tcpd-devel
# Suse splits this off into a separate package
Requires:       python-curses python-xml
BuildRequires:  python-curses python-xml
%endif

# Required for core functionality
BuildRequires:  automake autoconf libtool pkgconfig python
BuildRequires:	glib2-devel cluster-glue-libs-devel libxml2-devel libxslt-devel 
BuildRequires:	pkgconfig python-devel gcc-c++ bzip2-devel gnutls-devel pam-devel

# Enables optional functionality
BuildRequires:	ncurses-devel openssl-devel libselinux-devel docbook-style-xsl resource-agents


%ifarch alpha %{ix86} x86_64
BuildRequires:  lm_sensors-devel
%endif

%if %{with cman}
BuildRequires:	clusterlib-devel
%endif

%if %{with esmtp}
BuildRequires:	libesmtp-devel
%endif

%if %{with snmp}
BuildRequires:	net-snmp-devel
%endif

%if %{with ais}
# Do not require corosync, the admin should select which stack to use and install it
BuildRequires:	corosynclib-devel
%endif

%if %{with heartbeat}
# Do not require heartbeat, the admin should select which stack to use and install it
BuildRequires:	heartbeat-devel heartbeat-libs >= 3.0.0
%endif

%if %{with publican}
BuildRequires:	publican
%endif

%description
Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

Available rpmbuild rebuild options:
  --without : heartbeat ais snmp esmtp publican

%package -n pacemaker-libs
License:	GPLv2+ and LGPLv2+
Summary:	Libraries used by the Pacemaker cluster resource manager and its clients
Group:		System Environment/Daemons
Requires:	%{name} = %{version}-%{release}

%description -n pacemaker-libs
Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%package -n pacemaker-libs-devel 
License:	GPLv2+ and LGPLv2+
Summary:	Pacemaker development package
Group:		Development/Libraries
Requires:	pacemaker-libs = %{version}-%{release}
Requires:	cluster-glue-libs-devel
Requires:	libxml2-devel libxslt-devel bzip2-devel glib2-devel 
%if %{with ais}
Requires:	corosynclib-devel
%endif
%if %{with heartbeat}
Requires:	heartbeat-devel
%endif

%description -n pacemaker-libs-devel
Headers and shared libraries for developing tools for Pacemaker.

Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%package	cts
License:	GPLv2+ and LGPLv2+
Summary:	Test framework for cluster-related technologies like Pacemaker
Group:		System Environment/Daemons
Requires:	python

%description	cts
Test framework for cluster-related technologies like Pacemaker

%package	doc
License:	GPLv2+ and LGPLv2+
Summary:	Documentation for Pacemaker
Group:		Documentation

%description	doc
Documentation for Pacemaker.

Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%prep
%setup -q -n %{upstream_prefix}%{?upstream_version}

%build
./autogen.sh

# RHEL <= 5 does not support --docdir
docdir=%{pcmk_docdir} %{configure}	\
	%{?_without_heartbeat}		\
	%{?_without_ais}		\
	%{?_with_cman}			\
	%{?_without_esmtp}		\
	%{?_without_snmp}		\
	%{?_with_profiling}		\
	%{?_with_gcov}			\
	%{?_with_tracedata}		\
        --with-initdir=%{_initddir}	\
	--localstatedir=%{_var}		\
	--enable-fatal-warnings=no

make %{_smp_mflags} docdir=%{pcmk_docdir}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} docdir=%{pcmk_docdir} install

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
install -m 644 mcp/pacemaker.sysconfig ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/pacemaker

# Scripts that need should be executable
chmod a+x %{buildroot}/%{_libdir}/heartbeat/hb2openais-helper.py
chmod a+x %{buildroot}/%{_datadir}/pacemaker/tests/cts/CTSlab.py
chmod a+x %{buildroot}/%{_datadir}/pacemaker/tests/cts/extracttests.py

# These are not actually scripts
find %{buildroot} -name '*.xml' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.xsl' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.rng' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.dtd' -type f -print0 | xargs -0 chmod a-x
 
# Dont package static libs
find %{buildroot} -name '*.a' -type f -print0 | xargs -0 rm -f
find %{buildroot} -name '*.la' -type f -print0 | xargs -0 rm -f

# Do not package these either
rm -f %{buildroot}/%{_libdir}/heartbeat/crm_primitive.*
rm -f %{buildroot}/%{_libdir}/heartbeat/atest
rm -f %{buildroot}/%{_libdir}/service_crm.so

%if %{with gcov}
GCOV_BASE=%{buildroot}/%{_var}/lib/pacemaker/gcov
mkdir -p $GCOV_BASE
find . -name '*.gcno' -type f | while read F ; do
        D=`dirname $F`
        mkdir -p ${GCOV_BASE}/$D
        cp $F ${GCOV_BASE}/$D
done
%endif

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add pacemaker || :

%preun
if [ $1 -eq 0 ]; then
        /sbin/service pacemaker stop &>/dev/null || :
        /sbin/chkconfig --del pacemaker || :
fi

%post -n pacemaker-libs -p /sbin/ldconfig

%postun -n pacemaker-libs -p /sbin/ldconfig

%files
###########################################################
%defattr(-,root,root)

%exclude %{_datadir}/pacemaker/tests

%config(noreplace) %{_sysconfdir}/sysconfig/pacemaker
%{_initddir}/pacemaker
%{_sbindir}/pacemakerd

%{_datadir}/pacemaker
%{_datadir}/snmp/mibs/PCMK-MIB.txt
%{_libdir}/heartbeat/*
%{_sbindir}/cibadmin
%{_sbindir}/crm_attribute
%{_sbindir}/crm_diff
%{_sbindir}/crm_failcount
%{_sbindir}/crm_master
%{_sbindir}/crm_mon
%{_sbindir}/crm
%{_sbindir}/crm_resource
%{_sbindir}/crm_standby
%{_sbindir}/crm_verify
%{_sbindir}/crmadmin
%{_sbindir}/iso8601
%{_sbindir}/attrd_updater
%{_sbindir}/ptest
%{_sbindir}/crm_shadow
%{_sbindir}/cibpipe
%{_sbindir}/crm_node
%{_sbindir}/crm_simulate
%{_sbindir}/fence_legacy
%{_sbindir}/stonith_admin
%{_sbindir}/crm_report
%{py_sitedir}/crm
%doc %{_mandir}/man8/*.8*
%doc %{_mandir}/man7/*.7*

%if %{with heartbeat}
%{_sbindir}/crm_uuid
%else
%exclude %{_sbindir}/crm_uuid
%endif

%doc COPYING
%doc AUTHORS
%doc ChangeLog

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/heartbeat/crm
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pengine
%dir %attr (750, %{uname}, %{gname}) %{_var}/run/crm
%dir /usr/lib/ocf
%dir /usr/lib/ocf/resource.d
/usr/lib/ocf/resource.d/pacemaker
%if %{with ais}
%{_libexecdir}/lcrso/pacemaker.lcrso
%endif

%files -n pacemaker-libs
%defattr(-,root,root)
%{_libdir}/libcib.so.*
%{_libdir}/libcrmcommon.so.*
%{_libdir}/libcrmcluster.so.*
%{_libdir}/libpe_status.so.*
%{_libdir}/libpe_rules.so.*
%{_libdir}/libpengine.so.*
%{_libdir}/libtransitioner.so.*
%{_libdir}/libstonithd.so.*
%doc COPYING.LIB
%doc AUTHORS

%files doc
%defattr(-,root,root)
%doc %{pcmk_docdir}

%files cts
%defattr(-,root,root)
%{py_sitedir}/cts
%{_datadir}/pacemaker/tests/cts
%doc COPYING.LIB
%doc AUTHORS

%files -n pacemaker-libs-devel
%defattr(-,root,root)
%exclude %{_datadir}/pacemaker/tests/cts
%{_datadir}/pacemaker/tests
%{_includedir}/pacemaker
%{_libdir}/*.so
%if %{with gcov}
%dir %{_var}/lib/pacemaker
%{_var}/lib/pacemaker
%endif
%doc COPYING.LIB
%doc AUTHORS

%changelog
* Wed Oct 20 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.4-1
- Moved all the interesting parts of the changelog into a separate file as per the Fedora policy :-/
- Update source tarball to revision: 75406c3eb2c1 tip
- Significant performance enhancements to the Policy Engine and CIB
- Statistics:
  Changesets: 169
  Diff:       772 files changed, 56172 insertions(+), 39309 deletions(-)
- See included ChangeLog file or http://hg.clusterlabs.org/pacemaker/1.1/file/tip/ChangeLog for details

* Tue Sep 21 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.3-1
- Update source tarball to revision: e3bb31c56244 tip
- Statistics:
  Changesets: 352
  Diff:       481 files changed, 14130 insertions(+), 11156 deletions(-)

* Wed May 12 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-1
- Update source tarball to revision: c25c972a25cc tip
- Statistics:
  Changesets: 339
  Diff:       708 files changed, 37918 insertions(+), 10584 deletions(-)

* Tue Feb 16 2010 Andrew Beekhof <andrew@beekhof.net> - 1.1.1-1
- First public release of Pacemaker 1.1
- Package reference documentation in a doc subpackage
- Move cts into a subpackage so that it can be easily consumed by others
- Update source tarball to revision: 17d9cd4ee29f
  + New stonith daemon that supports global notifications
  + Service placement influenced by the physical resources
  + A new tool for simulating failures and the cluster’s reaction to them
  + Ability to serialize an otherwise unrelated a set of resource actions (eg. Xen migrations)

* Wed Feb 10 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.7-4
- Rebuild for heartbeat 3.0.2-2

* Wed Feb 10 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.7-3
- Rebuild for cluster-glue 1.0.3

* Tue Jan 19 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.7-2
- Rebuild for corosync 1.2.0

* Mon Jan 18 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.7-1
- Update source tarball to revision: 2eed906f43e9 (stable-1.0) tip
- Statistics:
      Changesets:      193
      Diff:            220 files changed, 15933 insertions(+), 8782 deletions(-)

* Thu Oct 29 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-4
- Include the fixes from CoroSync integration testing
- Move the resource templates - they are not documentation
- Ensure documentation is placed in a standard location
- Exclude documentation that is included elsewhere in the package

- Update the tarball from upstream to version ee19d8e83c2a
  + High: cib: Correctly clean up when both plaintext and tls remote ports are requested
  + High: PE: Bug bnc#515172 - Provide better defaults for lt(e) and gt(e) comparisions
  + High: PE: Bug lf#2197 - Allow master instances placemaker to be influenced by colocation constraints
  + High: PE: Make sure promote/demote pseudo actions are created correctly
  + High: PE: Prevent target-role from promoting more than master-max instances
  + High: ais: Bug lf#2199 - Prevent expected-quorum-votes from being populated with garbage
  + High: ais: Prevent deadlock - dont try to release IPC message if the connection failed
  + High: cib: For validation errors, send back the full CIB so the client can display the errors
  + High: cib: Prevent use-after-free for remote plaintext connections
  + High: crmd: Bug lf#2201 - Prevent use-of-NULL when running heartbeat

* Wed Oct 13 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-3
- Update the tarball from upstream to version 38cd629e5c3c
  + High: Core: Bug lf#2169 - Allow dtd/schema validation to be disabled
  + High: PE: Bug lf#2106 - Not all anonymous clone children are restarted after configuration change
  + High: PE: Bug lf#2170 - stop-all-resources option had no effect
  + High: PE: Bug lf#2171 - Prevent groups from starting if they depend on a complex resource which can not
  + High: PE: Disable resource management if stonith-enabled=true and no stonith resources are defined
  + High: PE: do not include master score if it would prevent allocation
  + High: ais: Avoid excessive load by checking for dead children every 1s (instead of 100ms)
  + High: ais: Bug rh#525589 - Prevent shutdown deadlocks when running on CoroSync
  + High: ais: Gracefully handle changes to the AIS nodeid
  + High: crmd: Bug bnc#527530 - Wait for the transition to complete before leaving S_TRANSITION_ENGINE
  + High: crmd: Prevent use-after-free with LOG_DEBUG_3
  + Medium: xml: Mask the "symmetrical" attribute on rsc_colocation constraints (bnc#540672)
  + Medium (bnc#520707): Tools: crm: new templates ocfs2 and clvm
  + Medium: Build: Invert the disable ais/heartbeat logic so that --without (ais|heartbeat) is available to rpmbuild
  + Medium: PE: Bug lf#2178 - Indicate unmanaged clones
  + Medium: PE: Bug lf#2180 - Include node information for all failed ops
  + Medium: PE: Bug lf#2189 - Incorrect error message when unpacking simple ordering constraint
  + Medium: PE: Correctly log resources that would like to start but can not
  + Medium: PE: Stop ptest from logging to syslog
  + Medium: ais: Include version details in plugin name
  + Medium: crmd: Requery the resource metadata after every start operation

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.0.5-2.1
- rebuilt with new openssl

* Wed Aug 19 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-2
- Add versioned perl dependency as specified by
    https://fedoraproject.org/wiki/Packaging/Perl#Packages_that_link_to_libperl
- No longer remove RPATH data, it prevents us finding libperl.so and no other
  libraries were being hardcoded
- Compile in support for heartbeat
- Conditionally add heartbeat-devel and corosynclib-devel to the -devel requirements 
  depending on which stacks are supported

* Mon Aug 17 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-1
- Add dependency on resource-agents
- Use the version of the configure macro that supplies --prefix, --libdir, etc
- Update the tarball from upstream to version 462f1569a437 (Pacemaker 1.0.5 final)
  + High: Tools: crm_resource - Advertise --move instead of --migrate
  + Medium: Extra: New node connectivity RA that uses system ping and attrd_updater
  + Medium: crmd: Note that dc-deadtime can be used to mask the brokeness of some switches

* Tue Aug 11 2009 Ville Skyttä <ville.skytta@iki.fi> - 1.0.5-0.7.c9120a53a6ae.hg
- Use bzipped upstream tarball.

* Wed Jul  29 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.6.c9120a53a6ae.hg
- Add back missing build auto* dependancies
- Minor cleanups to the install directive

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.5.c9120a53a6ae.hg
- Add a leading zero to the revision when alphatag is used

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.4.c9120a53a6ae.hg
- Incorporate the feedback from the cluster-glue review
- Realistically, the version is a 1.0.5 pre-release
- Use the global directive instead of define for variables
- Use the haclient/hacluster group/user instead of daemon
- Use the _configure macro
- Fix install dependancies

* Fri Jul  24 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-3
- Initial Fedora checkin
- Include an AUTHORS and license file in each package
- Change the library package name to pacemaker-libs to be more 
  Fedora compliant
- Remove execute permissions from xml related files
- Reference the new cluster-glue devel package name
- Update the tarball from upstream to version c9120a53a6ae
  + High: PE: Only prevent migration if the clone dependency is stopping/starting on the target node
  + High: PE: Bug 2160 - Dont shuffle clones due to colocation
  + High: PE: New implementation of the resource migration (not stop/start) logic
  + Medium: Tools: crm_resource - Prevent use-of-NULL by requiring a resource name for the -A and -a options
  + Medium: PE: Prevent use-of-NULL in find_first_action()

* Tue Jul 14 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-2
- Reference authors from the project AUTHORS file instead of listing in description
- Change Source0 to reference the Mercurial repo
- Cleaned up the summaries and descriptions
- Incorporate the results of Fedora package self-review

* Thu Jun 04 2009 Andrew Beekhof <abeekhof@suse.de> - 1.0.4-1
- Update source tarball to revision: 1d87d3e0fc7f (stable-1.0)
- Statistics:
    Changesets:      209
    Diff:            266 files changed, 12010 insertions(+), 8276 deletions(-)

* Wed Apr 08 2009 Andrew Beekhof <abeekhof@suse.de> - 1.0.3-1
- Update source tarball to revision: b133b3f19797 (stable-1.0) tip
- Statistics:
    Changesets:      383
    Diff:            329 files changed, 15471 insertions(+), 15119 deletions(-)

* Mon Feb 16 2009 Andrew Beekhof <abeekhof@suse.de> - 1.0.2-1
- Update source tarball to revision: d232d19daeb9 (stable-1.0) tip
- Statistics:
    Changesets:      441
    Diff:            639 files changed, 20871 insertions(+), 21594 deletions(-)

* Tue Nov 18 2008 Andrew Beekhof <abeekhof@suse.de> - 1.0.1-1
- Update source tarball to revision: 6fc5ce8302ab (stable-1.0) tip
- Statistics:
    Changesets:      170
    Diff:            816 files changed, 7633 insertions(+), 6286 deletions(-)

* Thu Oct 16 2008 Andrew Beekhof <abeekhof@suse.de> - 1.0.0-1
- Update source tarball to revision: 388654dfef8f tip
- Statistics:
    Changesets:      261
    Diff:            3021 files changed, 244985 insertions(+), 111596 deletions(-)

* Mon Sep 22 2008 Andrew Beekhof <abeekhof@suse.de> - 0.7.3-1
- Update source tarball to revision: 33e677ab7764+ tip
- Statistics:
    Changesets:      133
    Diff:            89 files changed, 7492 insertions(+), 1125 deletions(-)

* Wed Aug 20 2008 Andrew Beekhof <abeekhof@suse.de> - 0.7.1-1
- Update source tarball to revision: f805e1b30103+ tip
- Statistics:
    Changesets:      184
    Diff:            513 files changed, 43408 insertions(+), 43783 deletions(-)

* Fri Jul 18 2008 Andrew Beekhof <abeekhof@suse.de> - 0.7.0-19
- Update source tarball to revision: 007c3a1c50f5 (unstable) tip
- Statistics:
    Changesets:      108
    Diff:            216 files changed, 4632 insertions(+), 4173 deletions(-)

* Wed Jun 25 2008 Andrew Beekhof <abeekhof@suse.de> - 0.7.0-1
- Update source tarball to revision: bde0c7db74fb tip
- Statistics:
    Changesets:      439
    Diff:            676 files changed, 41310 insertions(+), 52071 deletions(-)

* Thu Jun 19 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.5-1
- Update source tarball to revision: b9fe723d1ac5 tip
- Statistics:
    Changesets:      48
    Diff:            37 files changed, 1204 insertions(+), 234 deletions(-)

* Thu May 22 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.4-1
- Update source tarball to revision: 226d8e356924 tip
- Statistics:
    Changesets:       55
    Diff:             199 files changed, 7103 insertions(+), 12378 deletions(-)

* Wed Apr 23 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.3-1
- Update source tarball to revision: fd8904c9bc67 tip
- Statistics:
    Changesets:      117
    Diff:            354 files changed, 19094 insertions(+), 11338 deletions(-)

* Thu Feb 14 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.2-1
- Update source tarball to revision: 28b1a8c1868b tip
- Statistics:
    Changesets:    11
    Diff:          7 files changed, 58 insertions(+), 18 deletions(-)

* Tue Feb 12 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.1-1
- Update source tarball to revision: e7152d1be933 tip
- Statistics:
    Changesets:    25
    Diff:          37 files changed, 1323 insertions(+), 227 deletions(-)

* Mon Jan 14 2008 Andrew Beekhof <abeekhof@suse.de> - 0.6.0-2
- This is the first release of the Pacemaker Cluster Resource Manager formerly part of Heartbeat.
- For those looking for the GUI, mgmtd, CIM or TSA components, they are now found in
  the new pacemaker-pygui project.  Build dependancies prevent them from being
  included in Heartbeat (since the built-in CRM is no longer supported) and,
  being non-core components, are not included with Pacemaker.
- Update source tarball to revision: c94b92d550cf
- Statistics:
    Changesets:      347
    Diff:            2272 files changed, 132508 insertions(+), 305991 deletions(-)
- Test hardware:
    + 6-node vmware cluster (sles10-sp1/256Mb/vmware stonith) on a single host (opensuse10.3/2Gb/2.66Ghz Quad Core2)
    + 7-node EMC Centera cluster (sles10/512Mb/2Ghz Xeon/ssh stonith)
- Notes: Heartbeat Stack
    + All testing was performed with STONITH enabled
    + The CRM was enabled using the "crm respawn" directive
- Notes: OpenAIS Stack
    + This release contains a preview of support for the OpenAIS cluster stack
    + The current release of the OpenAIS project is missing two important
    patches that we require.  OpenAIS packages containing these patches are
    available for most major distributions at:
    http://download.opensuse.org/repositories/server:/ha-clustering
    + The OpenAIS stack is not currently recommended for use in clusters that
    have shared data as STONITH support is not yet implimented
    + pingd is not yet available for use with the OpenAIS stack
    + 3 significant OpenAIS issues were found during testing of 4 and 6 node
    clusters.  We are activly working together with the OpenAIS project to
    get these resolved.
- Pending bugs encountered during testing:
    + OpenAIS   #1736 - Openais membership took 20s to stabilize
    + Heartbeat #1750 - ipc_bufpool_update: magic number in head does not match
    + OpenAIS   #1793 - Assertion failure in memb_state_gather_enter()
    + OpenAIS   #1796 - Cluster message corruption

* Mon Dec 10 2007 Andrew Beekhof <abeekhof@suse.de> - 0.6.0-1
- Initial opensuse package check-in
