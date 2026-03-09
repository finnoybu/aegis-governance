import glob
import re
import sys

# Required metadata fields and section headers (adjust as your template evolves)
REQUIRED_HEADERS = [
    r'\*\*RFC:\*\*',
    r'\*\*Status:\*\*',
    r'\*\*Version:\*\*',
    r'\*\*Created:\*\*',
    r'\*\*Updated:\*\*',
    r'\*\*Author:\*\*',
]
REQUIRED_SECTIONS = [
    r'## Summary',
    r'## Motivation',
    r'## Guide-Level Explanation',
    r'## Reference-Level Explanation',
    r'## Drawbacks',
    r'## Alternatives Considered',
    r'## Compatibility',
    r'## Implementation Notes',
    r'## Open Questions',
    r'## Success Criteria',
    r'## References',
]

failures = 0
for path in glob.glob('rfc/RFC-*.md'):
    if 'TEMPLATE' in path:
        continue
    with open(path, encoding='utf-8') as f:
        content = f.read()
        for header in REQUIRED_HEADERS:
            if not re.search(header, content):
                print(f'Missing metadata: {header} in {path}')
                failures += 1
        for section in REQUIRED_SECTIONS:
            if not re.search(section, content):
                print(f'Missing section: {section} in {path}')
                failures += 1
if failures:
    print(f"\n{failures} RFC(s) missing required template fields or sections.")
    sys.exit(1)
else:
    print("All RFCs conform to the template.")
=======
import os
import sys
import re

REQUIRED_FIELDS = [
    'Title:',
    'Status:',
    'Created:',
    'Last-Modified:',
    'Author:',
    'Type:',
    'Topic:',
    'Content:',
]

PLACEHOLDER_STATUS = 'Placeholder'

RFC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'rfc')

missing_fields = {}
skipped_files = []

for filename in os.listdir(RFC_DIR):
    if not filename.startswith('RFC-') or not filename.endswith('.md'):
        continue
    # Skip template and placeholder files
    if filename.startswith('RFC-0000-'):
        skipped_files.append(filename)
        continue
    path = os.path.join(RFC_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Robustly skip RFCs with '**Status:** Placeholder' anywhere in file
    content = ''.join(lines)
    if re.search(r'\*\*Status:\*\*\s*Placeholder', content, re.IGNORECASE):
        skipped_files.append(filename)
        continue
    content = ''.join(lines)
    missing = [field for field in REQUIRED_FIELDS if field not in content]
    if missing:
        missing_fields[filename] = missing

if missing_fields:
    print('RFC template check failed:')
    for file, fields in missing_fields.items():
        print(f'- {file} missing fields: {fields}')
    sys.exit(1)
else:
    print('All RFCs pass template check.')
    if skipped_files:
        print('Skipped placeholder RFCs:', ', '.join(skipped_files))
    sys.exit(0)