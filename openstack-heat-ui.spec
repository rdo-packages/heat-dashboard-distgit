# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
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

BuildArch:      noarch

BuildRequires:  git
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  openstack-macros
# Required to compile i18n messages
BuildRequires:  python%{pyver}-django
BuildRequires:  gettext

Requires:       openstack-dashboard
Requires:       python%{pyver}-XStatic-Angular-UUID
Requires:       python%{pyver}-XStatic-Angular-Vis
Requires:       python%{pyver}-XStatic-FileSaver
Requires:       python%{pyver}-XStatic-Json2yaml
Requires:       python%{pyver}-XStatic-JS-Yaml
Requires:       python%{pyver}-pbr >= 2.0.0
Requires:       python%{pyver}-heatclient >= 1.10.0

%description
Heat Dashboard is an extension for OpenStack Dashboard that provides a UI
for Heat.

%if 0%{?with_doc}
# Documentation package
%package -n python%{pyver}-%{openstack_name}-doc
Summary:        Documentation for OpenStack Heat Dashboard for Horizon
%{?python_provide:%python_provide python%{pyver}-%{openstack_name}-doc}
BuildRequires:  python%{pyver}-openstackdocstheme
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-sphinxcontrib-rsvgconverter

%description -n python%{pyver}-%{openstack_name}-doc
Documentation for Heat Dashboard
%endif

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Let RPM handle the dependencies
%py_req_cleanup

%build
%{pyver_build}
# Generate i18n files
pushd build/lib/heat_dashboard
django-admin compilemessages
popd

%if 0%{?with_doc}
# Build html documentation
%{pyver_bin} setup.py build_sphinx -b html
# Remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Move config to horizon
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
for f in heat_dashboard/enabled/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 644 heat_dashboard/enabled/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(filename)
done

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{pyver_sitelib}/heat_dashboard/locale/*/LC_*/django*.po
rm -f %{buildroot}%{pyver_sitelib}/heat_dashboard/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{?with_test}
%{pyver_bin} manage.py test
%endif

%files -f django.lang
%doc README.rst
%license LICENSE
%{pyver_sitelib}/heat_dashboard
%{pyver_sitelib}/*.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1610_project_orchestration_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1620_project_stacks_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1630_project_resource_types_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1640_project_template_versions_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1650_project_template_generator_panel.py*

%if 0%{?with_doc}
%files -n python%{pyver}-%{openstack_name}-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
