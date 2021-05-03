%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global pypi_name heat-dashboard
%global openstack_name heat-ui

# tests are disabled by default
%bcond_with tests

Name:           openstack-%{openstack_name}
Version:        XXX
Release:        XXX
Summary:        OpenStack Heat Dashboard for Horizon

License:        ASL 2.0
URL:            https://launchpad.net/heat-dashboard
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools
BuildRequires:  python3-pbr
BuildRequires:  python3-subunit
BuildRequires:  python3-oslotest
BuildRequires:  openstack-macros
# Required to compile i18n messages
BuildRequires:  python3-django
BuildRequires:  gettext

Requires:       openstack-dashboard
Requires:       python3-XStatic-Angular-UUID
Requires:       python3-XStatic-Angular-Vis
Requires:       python3-XStatic-FileSaver
Requires:       python3-XStatic-Json2yaml
Requires:       python3-XStatic-JS-Yaml
Requires:       python3-pbr >= 2.0.0
Requires:       python3-heatclient >= 1.10.0

%description
Heat Dashboard is an extension for OpenStack Dashboard that provides a UI
for Heat.

%if 0%{?with_doc}
# Documentation package
%package -n python3-%{openstack_name}-doc
Summary:        Documentation for OpenStack Heat Dashboard for Horizon
%{?python_provide:%python_provide python3-%{openstack_name}-doc}
BuildRequires:  python3-openstackdocstheme
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinxcontrib-rsvgconverter

%description -n python3-%{openstack_name}-doc
Documentation for Heat Dashboard
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Let RPM handle the dependencies
%py_req_cleanup

%build
%{py3_build}
# Generate i18n files
pushd build/lib/heat_dashboard
django-admin compilemessages
popd

%if 0%{?with_doc}
# Build html documentation
sphinx-build -W -b html doc/source doc/build/html
# Remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

# Move config to horizon
install -p -D -m 644 heat_dashboard/local_settings.d/_1699_orchestration_settings.py %{buildroot}%{_sysconfdir}/openstack-dashboard/openstack_dashboard/local_settings.d/_1699_orchestration_settings.py
install -p -D -m 644 heat_dashboard/conf/heat_policy.yaml %{buildroot}%{_sysconfdir}/openstack-dashboard/openstack_dashboard/heat_policy.yaml
install -p -D -m 644 heat_dashboard/conf/default_policies/heat.yaml %{buildroot}%{_sysconfdir}/openstack-dashboard/openstack_dashboard/default_policies/heat.yaml

mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
for f in heat_dashboard/enabled/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 644 heat_dashboard/enabled/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(filename)
done

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python3_sitelib}/heat_dashboard/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python3_sitelib}/heat_dashboard/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{?with_test}
%{__python3} manage.py test
%endif

%files -f django.lang
%doc README.rst
%license LICENSE
%config(noreplace) %attr(0640, root, apache) %{_sysconfdir}/openstack-dashboard/openstack_dashboard/local_settings.d/_1699_orchestration_settings.py
%config(noreplace) %attr(0640, root, apache) %{_sysconfdir}/openstack-dashboard/openstack_dashboard/heat_policy.yaml
%config(noreplace) %attr(0640, root, apache) %{_sysconfdir}/openstack-dashboard/openstack_dashboard/default_policies/heat.yaml
%{python3_sitelib}/heat_dashboard
%{python3_sitelib}/*.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1610_project_orchestration_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1620_project_stacks_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1630_project_resource_types_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1640_project_template_versions_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1650_project_template_generator_panel.py*

%if 0%{?with_doc}
%files -n python3-%{openstack_name}-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
