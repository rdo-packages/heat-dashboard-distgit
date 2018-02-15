%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

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
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python-ddt
BuildRequires:  python-django-nose
BuildRequires:  python-nose-exclude
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-pbr
BuildRequires:  python-selenium
BuildRequires:  python-openstackdocstheme
BuildRequires:  python-subunit
BuildRequires:  python-sphinx
BuildRequires:  python-oslotest
BuildRequires:  openstack-macros

Requires:       openstack-dashboard
Requires:       python-pbr >= 2.0.0
Requires:       python-heatclient >= 1.10.0

%description
Heat Dashboard is an extension for OpenStack Dashboard that provides a UI
for Heat.

# Documentation package
%package -n python-%{openstack_name}-doc
Summary:        Documentation for OpenStack Heat Dashboard for Horizon

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Let RPM handle the dependencies
%py_req_cleanup

%build
%py2_build

# Build html documentation
python setup.py build_sphinx -b html
# Remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}

%install
%py2_install

# Move config to horizon
for f in heat_dashboard/enabled/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 640 heat_dashboard/enabled/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(filename)
done

%check
%if 0%{?with_test}
%{__python2} manage.py test
%endif

%files
%doc README.rst
%license LICENSE
%{python2_sitelib}/heat_dashboard
%{python2_sitelib}/*.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1610_project_orchestration_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1620_project_stacks_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1630_project_resource_types_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1640_project_template_versions_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1650_project_template_generator_panel.py*

%files -n python-%{openstack_name}-doc
%doc doc/build/html
%license LICENSE

%changelog
