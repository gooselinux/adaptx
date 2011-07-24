# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

Name:          adaptx
Version:       0.9.13
Release:       8.1%{?dist}
Summary:       AdaptX XSLT processor and XPath engine
License:       BSD
Group:         Applications/Text
# svn export http://svn.codehaus.org/castor/adaptx/tags/0.9.13/ adaptx-0.9.13-src
# tar cjf adaptx-0.9.13-src.tar.bz2 adaptx-0.9.13-src
Source0:       %{name}-%{version}-src.tar.bz2

Patch0:        %{name}-%{version}-xsl.patch
Patch1:        %{name}-%{version}-missingstubs.patch
Patch2:        %{name}-%{version}-build-xml.patch
Patch3:        adaptx-0.9.13-no-enum-as-identifier.patch
Url:           http://castor.codehaus.org/
BuildRequires: ant >= 0:1.6
BuildRequires: jpackage-utils >= 0:1.6
BuildRequires: log4j
BuildRequires: xml-commons-apis
BuildRequires: xerces-j2
Requires:      log4j
Requires:      xml-commons-apis
Requires:      xerces-j2
Requires(pre):    jpackage-utils
Requires(postun): jpackage-utils
%if ! %{gcj_support}
BuildArch:    noarch
%endif
BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
Requires(post):   java-gcj-compat
Requires(postun): java-gcj-compat
%endif

%description
Adaptx is an XSLT processor and XPath engine.

%package javadoc
Group:            Documentation
Summary:          Javadoc for %{name}
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
Javadoc for %{name}.

%package doc
Summary:    Documentation for %{name}
Group:      Documentation

%description doc
Documentation for %{name}.

%prep
%setup -q -n %{name}-%{version}-src
# remove CVS internal files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
# remove all binary libs
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done

%patch0
%patch1
%patch2
%patch3 -p1

%build
perl -p -i -e 's|classic|modern|' src/build.xml
export CLASSPATH=$(build-classpath xml-commons-apis log4j xerces-j2)
ant -buildfile src/build.xml jar javadoc
CLASSPATH=$CLASSPATH:dist/adaptx_%{version}.jar
ant -buildfile src/build.xml doc

%install
rm -rf $RPM_BUILD_ROOT

# jar
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{name}_%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} ${jar/-%{version}/}; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/doc/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
rm -rf build/doc/javadoc

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi

%post
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0664,root,root,0755)
%doc src/etc/{CHANGELOG,contributors.html,LICENSE}
%{_javadir}/*

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files javadoc
%defattr(0664,root,root,0755)
%{_javadocdir}/%{name}-%{version}

%files doc
%defattr(0664,root,root,0755)
%doc build/doc/*

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.9.13-8.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.13-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.13-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.9.13-6
- drop repotag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9.13-5jpp.3
- Autorebuild for GCC 4.3

* Wed Oct 17 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.9.13-4jpp.3
- enum is a reserved keyword now, fix javadoc by not naming variables "enum"

* Wed Apr 18 2007 Permaine Cheung <pcheung@redhat.com> 0.9.13-4jpp.2
- Fixed the building of javadoc

* Wed Jan 31 2007 Deepak Bhole <dbhole@redhat.com> 0.9.13-4jpp.1
- Fixed issues raised by rpmlint

* Thu Aug 03 2006 Deepak Bhole <dbhole@redhat.com> 0:0.9.13-3jpp.1
- Added missing requirements. 

* Sun Jul 23 2006 Deepak Bhole <dbhole@redhat.com> 0:0.9.13-2jpp_3fc
- Adding missing dependency

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:0.9.13-2jpp_2fc
- Rebuilt

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> 0:0.9.13-2jpp_1fc
- Add conditional native compiling.

* Mon Jun 19 2006 Ralph Apel <r.apel at r-apel.de> 0:0.9.13-1jpp
- Upgrade to 0.9.13

* Thu Aug 19 2004 Ralph Apel <r.apel at r-apel.de> 0:0.9.6-2jpp
- Build with ant-1.6.2
- Set xmlns in **/*.xsl

* Tue Sep 09 2003 David Walluck <david@anti-microsoft.org> 0:0.9.6-1jpp
- 0.9.6
- Nicolas wrote the last changelog entry, not me
- adaptx requires itself to build, so I added '--without-external' in case you need or
  wish to use the included jar, but it defaults to '--with-external' (e.g., it defaults
  to using the external jpackage version of the jar).
- use the modern, not the classic, compiler
- BuildRequires: xml-commons-apis for doc target

* Fri May 16 2003 Nicolas Mailhot <Nicolas.Mailhot at laPoste.net> 0:0.9.5-2jpp
- do not self-require for build :)

* Sat May 10 2003 David Walluck <david@anti-microsoft.org> 0:0.9.5-1jpp
- release
