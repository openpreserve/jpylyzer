<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE refentry PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN"
"http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd" [

<!--

`xsltproc -''-nonet \
          -''-param man.charmap.use.subset "0" \
          -''-param make.year.ranges "1" \
          -''-param make.single.year.ranges "1" \
          /usr/share/xml/docbook/stylesheet/nwalsh/manpages/docbook.xsl \
          manpage.xml'

A manual page <package>.<section> will be generated. You may view the
manual page with: nroff -man <package>.<section> | less'. A typical entry
in a Makefile or Makefile.am is:

DB2MAN = /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl
XP     = xsltproc -''-nonet -''-param man.charmap.use.subset "0"

manpage.1: manpage.xml
        $(XP) $(DB2MAN) $<

The xsltproc binary is found in the xsltproc package. The XSL files are in
docbook-xsl. A description of the parameters you can use can be found in the
docbook-xsl-doc-* packages. Please remember that if you create the nroff
version in one of the debian/rules file targets (such as build), you will need
to include xsltproc and docbook-xsl in your Build-Depends control field.
Alternatively use the xmlto command/package. That will also automatically
pull in xsltproc and docbook-xsl.

Notes for using docbook2x: docbook2x-man does not automatically create the
AUTHOR(S) and COPYRIGHT sections. In this case, please add them manually as
<refsect1> ... </refsect1>.

To disable the automatic creation of the AUTHOR(S) and COPYRIGHT sections
read /usr/share/doc/docbook-xsl/doc/manpages/authors.html. This file can be
found in the docbook-xsl-doc-html package.

Validation can be done using: `xmllint -''-noout -''-valid manpage.xml`

General documentation about man-pages and man-page-formatting:
man(1), man(7), http://www.tldp.org/HOWTO/Man-Page/

-->

  <!-- Fill in your name for FIRSTNAME and SURNAME. -->
  <!ENTITY dhfirstname "Johan">
  <!ENTITY dhsurname   "van der Knijff">
  <!-- dhusername could also be set to "&dhfirstname; &dhsurname;". -->
  <!ENTITY dhusername  "unknown">
  <!ENTITY dhemail     "Johan.vanderKnijff@kb.nl">
  <!-- SECTION should be 1-8, maybe w/ subsection other parameters are
       allowed: see man(7), man(1) and
       http://www.tldp.org/HOWTO/Man-Page/q2.html. -->
  <!ENTITY dhsection   "SECTION">
  <!-- TITLE should be something like "User commands" or similar (see
       http://www.tldp.org/HOWTO/Man-Page/q2.html). -->
  <!ENTITY dhtitle     "jpylyzer User Manual">
  <!ENTITY dhucpackage "jpylyzer">
  <!ENTITY dhpackage   "jpylyzer">
]>

<refentry>
  <refentryinfo>
    <title>&dhtitle;</title>
    <productname>&dhpackage;</productname>
    <authorgroup>
      <author>
       <firstname>&dhfirstname;</firstname>
        <surname>&dhsurname;</surname>
        <contrib>Wrote this manpage for the Debian system.</contrib>
        <address>
          <email>&dhemail;</email>
        </address>
      </author>
    </authorgroup>
    <copyright>
      <year>2012</year>
      <holder>&dhusername;</holder>
    </copyright>
    <legalnotice>
      <para>This manual page was written for the Debian system
        (and may be used by others).</para>
      <para>Permission is granted to copy, distribute and/or modify this
        document under the terms of the GNU General Public License,
        Version 2 or (at your option) any later version published by
        the Free Software Foundation.</para>
      <para>On Debian systems, the complete text of the GNU General Public
        License can be found in
        <filename>/usr/share/common-licenses/GPL</filename>.</para>
    </legalnotice>
  </refentryinfo>
  <refmeta>
    <refentrytitle>&dhucpackage;</refentrytitle>
    <manvolnum>&dhsection;</manvolnum>
  </refmeta>
  <refnamediv>
    <refname>&dhpackage;</refname>
    <refpurpose>Prototype JP2 (JPEG 2000 Part 1) validator and properties extractor</refpurpose>
  </refnamediv>
  <refsynopsisdiv>
    <cmdsynopsis>
      <command>&dhpackage;</command>
      <!-- Normally the help and version options make the programs stop
           right after outputting the requested information. -->
      <group choice="opt">
        <arg choice="plain">
          <group choice="req">
            <arg choice="plain"><option>-h</option></arg>
            <arg choice="plain"><option>--help</option></arg>
          </group>
        </arg>
        <arg choice="plain">
          <group choice="req">
            <arg choice="plain"><option>-v</option></arg>
            <arg choice="plain"><option>--version</option></arg>
          </group>
        </arg>
      </group>
      <arg choice="opt" rep="repeat">jp2file</arg>
    </cmdsynopsis>
  </refsynopsisdiv>
  <refsect1 id="description">
    <title>DESCRIPTION</title>
    <para>Prototype JP2 (JPEG 2000 Part 1) validator and properties extractor.</para>
    <para>Output to stdout.
    
Example (output redirected to file 'rubbish.xml'):

jpylyzer.py rubbish.jp2 > rubbish.xml

Outline of output elements:

1. toolInfo: tool name (jpylyzer) + version.
2. fileInfo: name, path, size and last modified time/date of input file.
3. isValidJP2: "True"/"False" flag indicating whether file is valid JP2.
4. tests: tree of test outcomes, expressed as "True"/"False" flags.
   File is considered valid JP2 only if all tests return "True". Tree follows 
   JP2 box structure. 
5. properties: tree of image properties. Follows JP2 box structure. Naming of
   properties follows ISO/IEC 15444-1 Annex I (JP2 file format syntax) and
   Annex A (Codestream syntax).</para>
    
  </refsect1>
  <refsect1 id="options">
    <title>OPTIONS</title>
    <para>The program follows the usual GNU command line syntax,
      with long options starting with two dashes (`-').  A summary of
      options is included below.  For a complete description, see the
      <citerefentry>
        <refentrytitle>info</refentrytitle>
        <manvolnum>1</manvolnum>
      </citerefentry> files.</para>
    <variablelist>
      <!-- Use the variablelist.term.separator and the
           variablelist.term.break.after parameters to
           control the term elements. -->
      <varlistentry>
        <term><option>-h</option></term>
        <term><option>--help</option></term>
        <listitem>
          <para>shows a help message and exit.</para>
        </listitem>
      </varlistentry>
      <varlistentry>
        <term><option>-v</option></term>
        <term><option>--version</option></term>
        <listitem>
          <para>show program's version number and exit.</para>
        </listitem>
      </varlistentry>
    </variablelist>
  </refsect1>
  <refsect1 id="bugs">
    <!-- Or use this section to tell about upstream BTS. -->
    <title>BUGS</title>
    <para>The upstreams <acronym>BTS</acronym> can be found
      at <ulink url="https://github.com/openpreserve/jpylyzer/issues"/>.</para>
  </refsect1>
</refentry>

