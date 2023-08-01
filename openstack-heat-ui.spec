%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order nodeenv xvfbwrapper
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global with_doc 1
%global rhosp 0

%global pypi_name heat-dashboard
%global openstack_name heat-ui

# tests are disabled by default
%bcond_with tests

Name:           openstack-%{openstack_name}
Version:        XXX
Release:        XXX
Summary:        OpenStack Heat Dashboard for Horizon

License:        Apache-2.0
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
BuildRequires:  pyproject-rpm-macros
BuildRequires:  openstack-macros
BuildRequires:  gettext

Requires:       openstack-dashboard
%description
Heat Dashboard is an extension for OpenStack Dashboard that provides a UI
for Heat.

%if 0%{?with_doc}
# Documentation package
%package -n python3-%{openstack_name}-doc
Summary:        Documentation for OpenStack Heat Dashboard for Horizon
%description -n python3-%{openstack_name}-doc
Documentation for Heat Dashboard
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git

sed -i '/.*-c{env:.*_CONSTRAINTS_FILE.*/,+1d' tox.ini
sed -i  '/^[[:space:]]*-r{toxinidir}\/test-requirements.txt/d' tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel
# Generate i18n files
pushd build/lib/heat_dashboard
django-admin compilemessages
popd

%if 0%{?with_doc}
# Build html documentation
%tox -e docs
# Remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

# Move config to horizon
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/default_policies

for f in heat_dashboard/enabled/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 644 heat_dashboard/enabled/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${filename}
done

%if 0%{?rhosp} == 0
  for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_16*.py*; do
    filename=`basename $f`
    ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${filename} \
      %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/${filename}
  done
%endif

for f in heat_dashboard/local_settings.d/_16*.py*; do
  filename=`basename $f`
  install -p -D -m 644 heat_dashboard/local_settings.d/${filename} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/${filename}
done

%if 0%{?rhosp} == 0
  for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_16*.py*; do
    filename=`basename $f`
    ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/${filename} \
      %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d/${filename}
  done
%endif

mv heat_dashboard/conf/heat_policy.yaml %{buildroot}%{_sysconfdir}/openstack-dashboard
mv heat_dashboard/conf/default_policies/heat.yaml %{buildroot}%{_sysconfdir}/openstack-dashboard/default_policies/

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
%{python3_sitelib}/heat_dashboard
%{python3_sitelib}/*.dist-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_16*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_16*.py*
%{_sysconfdir}/openstack-dashboard/heat_policy.yaml
%{_sysconfdir}/openstack-dashboard/default_policies/heat.yaml
%config(noreplace) %attr(0640, root, apache) %{_sysconfdir}/openstack-dashboard/default_policies/heat.yaml
%config(noreplace) %attr(0640, root, apache) %{_sysconfdir}/openstack-dashboard/heat_policy.yaml

%if 0%{?rhosp} == 0
  %{_sysconfdir}/openstack-dashboard/enabled/_16*.py*
  %{_sysconfdir}/openstack-dashboard/local_settings.d/_16*.py*
%endif

%if 0%{?with_doc}
%files -n python3-%{openstack_name}-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
