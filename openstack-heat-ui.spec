%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global pypi_name heat-dashboard
%global openstack_name heat-ui

# tests are disabled by default
%bcond_with tests

Name:           openstack-%{openstack_name}
Version:        1.4.0
Release:        1%{?dist}
Summary:        OpenStack Heat Dashboard for Horizon

License:        ASL 2.0
URL:            https://launchpad.net/heat-dashboard
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz

BuildArch:      noarch

BuildRequires:  git
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools
BuildRequires:  python2-django-nose
BuildRequires:  python-nose-exclude
BuildRequires:  python2-oslo-sphinx
BuildRequires:  python2-pbr
BuildRequires:  python2-openstackdocstheme
BuildRequires:  python2-subunit
BuildRequires:  python2-sphinx
BuildRequires:  python2-oslotest
BuildRequires:  openstack-macros
# Required to compile i18n messages
BuildRequires:  python2-django
BuildRequires:  gettext

Requires:       openstack-dashboard
Requires:       python2-XStatic-Angular-UUID
Requires:       python2-XStatic-Angular-Vis
Requires:       python2-XStatic-FileSaver
Requires:       python2-XStatic-Json2yaml
Requires:       python2-XStatic-JS-Yaml
Requires:       python2-pbr >= 2.0.0
Requires:       python2-heatclient >= 1.10.0

%description
Heat Dashboard is an extension for OpenStack Dashboard that provides a UI
for Heat.

# Documentation package
%package -n python-%{openstack_name}-doc
Summary:        Documentation for OpenStack Heat Dashboard for Horizon

%description -n python-%{openstack_name}-doc
Documentation for Heat Dashboard

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Let RPM handle the dependencies
%py_req_cleanup

%build
%py2_build
# Generate i18n files
pushd build/lib/heat_dashboard
django-admin compilemessages
popd

# Build html documentation
python setup.py build_sphinx -b html
# Remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}

%install
%py2_install

# Move config to horizon
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
for f in heat_dashboard/enabled/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 640 heat_dashboard/enabled/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(filename)
done

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python2_sitelib}/heat_dashboard/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python2_sitelib}/heat_dashboard/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{?with_test}
%{__python2} manage.py test
%endif

%files -f django.lang
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
* Thu Aug 23 2018 RDO <dev@lists.rdoproject.org> 1.4.0-1
- Update to 1.4.0

* Mon Aug 20 2018 RDO <dev@lists.rdoproject.org> 1.3.0-1
- Update to 1.3.0


