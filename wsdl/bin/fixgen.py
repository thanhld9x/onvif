#!/usr/bin/env python3
import sys
import os
import re
from urllib.request import urlopen

# How to use:
# go get github.com/hooklift/gowsdl/...
# ./fixgen.py [onvif profile file name without .wsdl]

if len(sys.argv) != 2:
    print("Usage:\n./fixgen.py [path to profile file without .wsdl]")
    exit(1)

go_package = os.path.basename(sys.argv[1])
go_src = os.path.basename(sys.argv[1]) + '.go'
wsdl_file = sys.argv[1] + '.wsdl'

with open(wsdl_file, 'r') as file:
    wsdl = file.read()

r = re.findall(r'targetNamespace="(http://www.onvif.org/.+)"', wsdl)
if len(r):
    targetNamespace = r[0]

os.system('gowsdl -o ' + go_src + ' -p ' + go_package + ' ' + wsdl_file + ' | grep -v expected')

with open(go_package + '/' + go_src, 'r') as file:
    data = file.read()

data = data.replace('// Code generated by gowsdl DO NOT EDIT.', '')
print(' - Replace import')
data = data.replace('"github.com/hooklift/gowsdl/soap"',
                    '"github.com/videonext/onvif/soap"')
########################################################################

print(' - Working around some bugs in the gowsdl')
data = data.replace('interface{}', '')
data = data.replace('TLS1.0 bool', 'TLS1_0 bool')
data = data.replace('TLS1.1 bool', 'TLS1_1 bool')
data = data.replace('TLS1.2 bool', 'TLS1_2 bool')
data = data.replace('X.509Token bool', 'X_509Token bool')
########################################################################

print(' - Adding wsdl\'s namespace and method name to the SOAP action')
data = re.sub(r'(?s)func \(service (\*\w+\)) (\w+)Context\s*\(ctx context.Context, request (\*\w+\)) \((\*\w+), error\)(.+?)service\.client\.CallContext\(ctx, "(\'\')",',
              r'func (service \1 \2Context(ctx context.Context, request \3 (\4, error)\5service.client.CallContext(ctx, "' + targetNamespace + '/' + r'\2",', data)
########################################################################

print(' - Patching object, CallContext and New* functions: add xaddr field/arg')
data = re.sub(r'(?s)type\s+(\w+?)\s+struct\s+\{\s+?client\s+\*soap\.Client',
              r'type \1 struct {\nclient *soap.Client\nxaddr  string\n', data)
data = data.replace('service.client.CallContext(ctx,', 'service.client.CallContext(ctx, service.xaddr,')
data = re.sub(r'(?s)func New(.+?)\(client \*soap.Client\) (.+?) \{.+?return \&(\w+)\{.+?}',
              r'func New\1(client *soap.Client, xaddr string) \2 {\n return &\3{\nclient: client,\nxaddr: xaddr,\n}', data)
########################################################################

print(' - Fixing namespaces in the xsd types')
type_map = {}
xsds = ['http://www.onvif.org/ver10/schema/common.xsd',
        'http://www.onvif.org/ver10/schema/onvif.xsd',
        'http://www.w3.org/2001/xml.xsd',
        'http://www.onvif.org/ver10/schema/metadatastream.xsd',
        'http://www.onvif.org/ver10/pacs/types.xsd',
        'http://www.onvif.org/ver20/analytics/rules.xsd',
        'http://www.onvif.org/ver20/analytics/radiometry.xsd']
for xsd in xsds:
    xsd_data = urlopen(xsd).read().decode('utf-8')
    r = re.findall(r'targetNamespace="(http://.+?)"', xsd_data)
    if len(r):
        ns = r[0]
    else:
        raise Exception('No namespace in the ' + xsd)
    r = re.findall(r'\<xs:\w+Type name="(\w+)">', xsd_data)
    for t in r:
        if not t[0].isupper():
            t = t.title()
        if t in type_map:
            continue
        type_map[t] = ns
# reading used types from onvif.xsd
onvif_xsd_data = urlopen('http://www.onvif.org/ver10/schema/onvif.xsd').read().decode('utf-8')
r = re.findall(r'type="xs:(.+?)"', onvif_xsd_data)
for t in r:
    if not t[0].isupper():
        t = t.title()
    if t in type_map:
        continue
    type_map[t] = 'http://www.onvif.org/ver10/schema'
# reading used types from common.xsd
common_xsd_data = urlopen('http://www.onvif.org/ver10/schema/common.xsd').read().decode('utf-8')
r = re.findall(r'type="xs:(.+?)"', common_xsd_data)
for t in r:
    if not t[0].isupper():
        t = t.title()
    if t in type_map:
        continue
    type_map[t] = 'http://www.onvif.org/ver10/schema'
# reading types from wsdl
r = re.findall(r'\<xs:\w+Type name="(\w+)">', wsdl)
for t in r:
    if not t[0].isupper():
        t = t.title()
    if t in type_map:
        continue
    type_map[t] = targetNamespace
# some other types
type_map['String'] = 'http://www.onvif.org/ver10/schema'
type_map['string'] = 'http://www.onvif.org/ver10/schema'
type_map['time.Time'] = 'http://www.onvif.org/ver10/schema'
type_map['byte'] = 'http://www.onvif.org/ver10/schema'
type_map['int'] = 'http://www.onvif.org/ver10/schema'
type_map['uint'] = 'http://www.onvif.org/ver10/schema'
type_map['int8'] = 'http://www.onvif.org/ver10/schema'
type_map['uint8'] = 'http://www.onvif.org/ver10/schema'
type_map['int16'] = 'http://www.onvif.org/ver10/schema'
type_map['uint16'] = 'http://www.onvif.org/ver10/schema'
type_map['int32'] = 'http://www.onvif.org/ver10/schema'
type_map['uint32'] = 'http://www.onvif.org/ver10/schema'
type_map['int64'] = 'http://www.onvif.org/ver10/schema'
type_map['uint64'] = 'http://www.onvif.org/ver10/schema'
type_map['float32'] = 'http://www.onvif.org/ver10/schema'
type_map['float64'] = 'http://www.onvif.org/ver10/schema'
type_map['bool'] = 'http://www.onvif.org/ver10/schema'
type_map['[]string'] = 'http://www.onvif.org/ver10/schema'
type_map['ReferenceToken'] = 'http://www.onvif.org/ver10/schema'
type_map['time.Time'] = 'http://www.onvif.org/ver10/schema'
type_map['NonNegativeInteger'] = 'http://www.onvif.org/ver10/schema'
if type_map['Anyuri'] != None:
    type_map['AnyURI'] = type_map['Anyuri']
# print(type_map)
for k, v in type_map.items():
    ns = v
    # # check if type used in the wsdl we are processing
    r = re.findall(r'type="\w+:' + re.escape(k), wsdl)
    # if len(r) and (re.search(r'complexType name="' + k + '"', common_xsd_data) or re.search(r'complexType name="' + k + '"', onvif_xsd_data)):
    #     ns = targetNamespace
    if len(r):
        ns = targetNamespace
    data = re.sub(r"(?s)(\w+)\s+\*" + re.escape(k) + r"\s+`xml:\"\1(.*?)\"`",
                  r"\1 *" + k + r' `xml:"' + ns + r' \1\2"`',
                  data)
    data = re.sub(r"(?s)(\w+)\s+\[\]\*" + re.escape(k) + r"\s+`xml:\"\1(.*?)\"`",
                  r"\1 []*" + k + r' `xml:"' + ns + r' \1\2"`',
                  data)
    data = re.sub(r"(?s)(\w+)\s+\[\]" + re.escape(k) + r"\s+`xml:\"\1(.*?)\"`",
                  r"\1 []" + k + r' `xml:"' + ns + r' \1\2"`',
                  data)
    data = re.sub(r"(?s)(\w+)\s+" + re.escape(k) + r"\s+`xml:\"\1(.*?)\"`",
                  r"\1 " + k + r' `xml:"' + ns + r' \1\2"`',
                  data)
########################################################################

with open(go_package + '/' + go_src, 'w') as file:
    file.write(data)

os.system("gofmt -w " + go_package + '/' + go_src)

with open(go_package + '/' + go_src, 'r') as file:
    data = file.read()

print(' - Removing unused types')
for k, v in type_map.items():
    r1 = re.findall(r"(\w+)\s+\*" + re.escape(k) + r"\s+`xml:\"", data)
    r2 = re.findall(r"\*" + re.escape(k), data)
    if len(r1) == 0 and len(r2) == 0:
        regex = re.compile(r"(?s)type\s+" + re.escape(k) + r"\s+struct\s+\{(.+?)^\}", re.MULTILINE)
        data = re.sub(regex, "// Removed " + k + " by fixgen.py\n", data)
########################################################################

print(' - Adding missed simple types')
data += "\ntype AnyURI string\n"
data += "type Duration string\n"
data += "type QName string\n"
data += "type NCName string\n"
data += "type NonNegativeInteger int64\n"
data += "type PositiveInteger int64\n"
data += "type NonPositiveInteger int64\n"
data += "type AnySimpleType string\n"
data += "type String string\n"
########################################################################

print(' - Removing pointers for simple types')
data = data.replace('*AnyURI', 'AnyURI')
data = data.replace('*Duration', 'Duration')
data = data.replace('*QName', 'QName')
data = data.replace('*NonNegativeInteger', 'NonNegativeInteger')
data = data.replace('*PositiveInteger', 'PositiveInteger')
data = data.replace('*NonPositiveInteger', 'NonPositiveInteger')
data = data.replace('*AnySimpleType', 'AnySimpleType')
data = data.replace('*Description', 'Description')
data = data.replace('*Name `xml', 'Name `xml')
data = data.replace('*string `xml', 'string `xml')
data = data.replace('*String `xml', 'String `xml')
data = data.replace('*int32 `xml', 'int32 `xml')
data = data.replace('*float32 `xml', 'float32 `xml')
data = data.replace('*bool `xml', 'bool `xml')
data = data.replace('*time.Time `xml', 'string `xml')
data = data.replace('time.Time `xml', 'string `xml')
data = data.replace('[]*', '[]')
data = data.replace('*NCName', 'NCName')
########################################################################

print(' - Removing duplicated types')
data = re.sub(r'type \b(\w+)\s+\1\b', '', data)
data = data.replace('type IntList IntAttrList', '')
data = data.replace('type FloatList FloatAttrList', '')
data = data.replace('type Capabilities DeviceServiceCapabilities', '')
data = data.replace('type FaultcodeEnum *QName', 'type FaultcodeEnum QName')
data = data.replace('type FaultCodesType *QName', 'type FaultCodesType QName')
data = data.replace('type RelationshipType *AnyURI', 'type RelationshipType AnyURI')
data = re.sub(r'(?s)type QueryExpressionType struct \{\n\s+XMLName xml\.Name `xml:"http://docs\.oasis-open\.org/wsn/b-2 ProducerProperties(.+?)\}',
              r'// Removed QueryExpressionType', data)
r = re.findall(r'(?s)(type Capabilities struct(.+?)\})', data)
if len(r) == 2:
    data = data.replace(r[1][0], '/* Removed ' + r[1][0] + ' Removed*/')
########################################################################

print(' - Removing pointers to xml data types')
data = re.sub(r"(\w+)\s+\*(\w+)\s+`xml:\"(.*?)\"`",
              r'\1 \2 `xml:"\3"`',
              data)
data = re.sub(r"(\w+)\s+\[\]\*(\w+)\s+`xml:\"(.*?)\"`",
              r'\1 []\2 `xml:"\3"`',
              data)
# keep some of them to prevent recursion
data = data.replace('Extension NetworkZeroConfigurationExtension `xml:"', 'Extension *NetworkZeroConfigurationExtension `xml:"')
data = data.replace('Tunnel Transport `xml:"', 'Tunnel *Transport `xml:"')
data = data.replace('Subcode Subcode `xml:"', 'Subcode *Subcode `xml:"')
data = data.replace('*Ref', 'Ref')
########################################################################

# add comments to exported types
regex = re.compile(r'^type\s+(.+?)\s+', re.MULTILINE)
data = re.sub(regex, r'// \1 type\ntype \1 ', data)

# remove ns from *Response* types
regex = re.compile(r'(?s)^(type \w+Response\w+ struct \{.+?\})', re.MULTILINE)
r = re.findall(regex, data)
regex = re.compile(r'(?s)^(type \w+Response struct \{.+?\})', re.MULTILINE)
r += re.findall(regex, data)
for block in r:
    block2 = re.sub(r'xml:"http.+? ', 'xml:"', block)
    data = data.replace(block, block2)


with open(go_package + '/' + go_src, 'w') as file:
    file.write(data)


os.system("gofmt -w " + go_package + '/' + go_src)


print('Done')
