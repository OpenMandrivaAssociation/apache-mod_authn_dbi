#Module-Specific definitions
%define mod_name mod_authn_dbi
%define mod_conf A82_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Provides Authentication against an SQL database backend
Name:		apache-%{mod_name}
Version:	0.9.0
Release:	%mkrel 8
Group:		System/Servers
License:	GPL
URL:		http://mod-auth.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/mod-auth/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_authn_dbi-0.9.0-module.diff
Patch1:		mod_authn_dbi-0.9.0-missing_separator.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	libdbi-devel >= 0.8.1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The module mod_authn_dbi provides Authentication against an SQL database
backend. It uses the application-independent abstraction layer provided by
libdbi. Database drivers for libdbi are provided by the libdbi-drivers,
project. At the moment, drivers are provided for MySQL, PostgreSQL, SQLite, 
mSQL and FreeTDS (MSSQL/Sybase).

mod_authn_dbi is very flexible and offers several levels of customization. This
makes it easy to integrate it into existing installations and authenticate
users  without having to alter the structure of existing tables. It is also
relatively easy to port existing authentication information from other sources,
e.g. file-based authentication to a backend for use by mod_authn_dbi. 

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p1
%patch1 -p1

# stupid libtool...
perl -pi -e "s|libmod_authn_dbi|mod_authn_dbi|g" src/Makefile*

# lib64 fixes
perl -pi -e "s|/lib\b|/%{_lib}|g" *

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export CPPFLAGS="`apr-1-config --cppflags` `apr-1-config --includes`"

%configure2_5x --localstatedir=/var/lib \
    --with-dbi=%{_prefix} \
    --with-dbi-libs=%{_libdir} \
    --with-dbi-include=%{_includedir} \
    --with-apxs=%{_sbindir}/apxs

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 src/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
 %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
 if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
 fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog INSTALL README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
