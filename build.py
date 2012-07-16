#! /usr/bin/env python
"""
Copyright (c) 2012 David Pratt (for TideSDK). All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

CONTRIBUTORS:

David Pratt <fairwinds.dp@gmail.com>
Matthew Hershberger <matthewh@multipart.net>

Build third party libraries

"""
import os
import random
import string
import shutil
import subprocess
import sys
import urllib
import zipfile


OS = 'osx'
BUNDLE_VER = '0.1.0'
REMOTE_URL = 'http://tidesdk.multipart.net/thirdparty/libs'
WORKSPACE_DIR = os.getcwd()
SRC_CACHE = os.path.join(WORKSPACE_DIR, 'cache')
BUILD_DIR = os.path.join(WORKSPACE_DIR, 'build')
BUNDLE_DIR = os.path.join(WORKSPACE_DIR, 'bundle')

GROWL_VER = '1.3.1'
PHP_VER = '5.4.4'
POCO_VER = '1.4.3p1'
WEBKIT_VER = 'r122661'

GROWL_SRC = 'Growl-%s-SDK.zip' % GROWL_VER
GROWL_URL = os.path.join(REMOTE_URL, 'osx', 'growl', GROWL_SRC)
PHP_SRC = 'php-%s.tar.gz' % PHP_VER
PHP_URL = os.path.join(REMOTE_URL, 'generic', 'php', PHP_SRC)
POCO_SRC = 'poco-%s.tar.gz' % POCO_VER
POCO_URL = os.path.join(REMOTE_URL, 'generic', 'poco', POCO_SRC)
WEBKIT_SRC = 'WebKit-%s.tar.bz2' % WEBKIT_VER
WEBKIT_URL = os.path.join(REMOTE_URL, 'osx', 'webkit', WEBKIT_SRC)

def random_name():
    """Generate a random name suitable for a temporary folder"""  
    return 'tidesdk-thirdparty-'+ \
        ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(8))

def call(cmd):
    """Call command with output to std out/std err"""
    proc = subprocess.Popen(cmd, shell=True)
    return_code = proc.wait()

def fetch(src, src_url):
    """Fetch src from cache if exists or from remote stash if not."""
    print('TideSDK Thirdparty Linux ==> Fetching %s' % src_url)
    if not os.path.exists(BUNDLE_DIR):
        os.makedirs(BUNDLE_DIR, 0755);  
    if not os.path.exists(SRC_CACHE):
        os.makedirs(SRC_CACHE, 0755);
    cache_src = os.path.join(SRC_CACHE, src)
    build_dir = os.path.join(BUILD_DIR, random_name())
    os.makedirs(build_dir, 0755)
    
    if os.path.exists(cache_src):
        print('TideSDK Thirdparty Linux ==> Fetching from cache')
        shutil.copy(cache_src, build_dir) 
        return build_dir
    else:
        print('TideSDK Thirdparty Linux ==> Fetching from remote stash')
        try:
            os.chdir(SRC_CACHE)
            urllib.urlretrieve(src_url, src)
            shutil.copy(cache_src, build_dir)
            return build_dir
        except Exception, err:
            sys.stderr.write('Error: %s\n' % str(err))

def unpack(name, src_file, src_url, build_dir, ext):
    os.chdir(build_dir)
    print('TideSDK Thirdparty Linux ==> Unpacking %s %s' % (name, src_file))
    src = os.path.join(build_dir, src_file)
    if ext == 'tar.gz':
        try:
            call('tar -zxf ' + src)
            src_dir = os.path.splitext(os.path.splitext(src)[0])[0]
            os.chdir(src_dir)
            return True
        except Exception, err:
            sys.stderr.write('Error: %s\n' % str(err))
    if ext == 'zip':
        try:
            z = zipfile.ZipFile(src)
            for f in z.namelist():
                if f.endswith('/'):
                    os.makedirs(f)
            return True
        except Exception, err:
            sys.stderr.write('Error: %s\n' % str(err))
    if ext == 'tar.bz2':
        try:
            call('tar -xjf ' + src)
            src_dir = os.path.splitext(os.path.splitext(src)[0])[0]
            os.chdir(src_dir)
            return True
        except Exception, err:
            sys.stderr.write('Error: %s\n' % str(err))

# PHP dependencies

def build_php():
    """Build php from sources"""
    print('TideSDK Thirdparty Linux ==> Building PHP %s' % PHP_VER)
    build_dir = fetch(PHP_SRC, PHP_URL)
    prefix = os.path.join(BUNDLE_DIR, 'php')
    if unpack('PHP', PHP_SRC, PHP_URL, build_dir, 'tar.gz'):
        print('TideSDK Thirdparty Linux ==> PHP unpacked')
        call('./configure --prefix=%s' % prefix)
        print('TideSDK Thirdparty Linux ==> building PHP')
        call('make')
        print('TideSDK Thirdparty Linux ==> installing PHP in bundle')
        call('make install')
        # cleanup
        call('rm -rf %s' % build_dir)

def build_poco():
    print('TideSDK Thirdparty Linux ==> Building Poco %s' % POCO_VER)
    build_dir = fetch(POCO_SRC, POCO_URL)
    prefix = os.path.join(BUNDLE_DIR, 'poco')
    bin_dir = os.path.join(prefix, 'bin')
    if unpack('Poco', POCO_SRC, POCO_URL, build_dir, 'tar.gz'):
        print('TideSDK Thirdparty Linux ==> Poco unpacked')
        call('./configure --prefix=%s' % prefix)
        print('TideSDK Thirdparty Linux ==> building Poco')
        call('make')
        print('TideSDK Thirdparty Linux ==> installing Poco in bundle')
        call('make install')
        # cleanup
        call('rm -rf %s' % bin_dir)
    
def build_webkit():
    """Build TideSDK's patched webkit from sources"""
    print('TideSDK Thirdparty Linux ==> Building Webkit %s' % WEBKIT_VER)
    build_dir = fetch(WEBKIT_SRC, WEBKIT_URL)
    prefix = os.path.join(BUNDLE_DIR, 'WEBKIT')
    if unpack('Webkit', WEBKIT_SRC, WEBKIT_URL, build_dir, 'tar.bz2'):
        print('TideSDK Thirdparty Linux ==> Webkit unpacked')
        src = os.path.splitext(os.path.splitext(WEBKIT_SRC)[0])[0]
        src_dir = os.path.join(build_dir, src)
        os.chdir(src_dir)
        
        print('TideSDK Thirdparty Linux ==> building Webkit')
        call('./Tools/Scripts/build-webkit --gtk')
        
        print('TideSDK Thirdparty Linux ==> installing Webkit in bundle')
        webkit_dir = os.path.join(BUNDLE_DIR, 'webkit')
        webkit_release_dir = os.path.join(
            build_dir, src_dir, 'WebKitBuild', 'Release')
        call('mkdir %s' % webkit_dir)
        frameworks = [
            'JavaScriptCore.framework',
            'WebCore.framework',
            'WebKit.framework',
            'WebKit2.framework'
        ]
        for f in frameworks:
            framework_dir = os.path.join(webkit_release_dir, f)
            dest_dir = os.path.join(webkit_dir, f)
            shutil.copytree(framework_dir, dest_dir, symlinks=True)
        # cleanup
        # call('rm -rf %s' % build_dir)

def bundle():
    """Archives the bundle for transport"""
    commit_hash = os.environ['GIT_COMMIT']
    hash_8 = commit_hash[-8:]
    artefact_name = '%s-%s-%s-%s' (BUNDLE_BASE_NAME, OS, BUNDLE_VER, hash_8)
    artefact_dir = os.path.join(os.getcwd(), artefact_name)
    call('mv % %' % (BUNDLE_DIR, artefact_dir))
    call('tar -cf - %s | gzip -c > %s.tar.gz' % (artefact_name, artefact_name))
        
def build():
    """Run the build"""
    print('TideSDK Thirdparty Linux ==> Building Dependencies')
    build_php()
    build_poco()
    build_webkit()
    bundle()

if __name__ == '__main__':
    build()